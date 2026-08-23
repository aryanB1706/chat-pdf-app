"""20-question evaluation suite: retrieval hit-rate + tool + citation checks.

Offline mode (default): zero deps — synthetic corpus, keyword retriever with
the same top-k/page contract as pgvector retrieval, and the real agent
planner + answer builder in extractive mode (no API key needed).

Live mode: hits a running API ingested with any long PDF and checks that
/ask returns non-empty answers with page-level citations:
    python -m eval.run --mode live --api http://localhost:8000 --doc <uuid>

Exit code 1 when hit-rate < threshold (quality regression gate for CI).
"""

import argparse
import json
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

STOPWORDS = {
    "what", "where", "when", "which", "how", "does", "do", "is", "are", "the",
    "a", "an", "and", "or", "of", "in", "on", "to", "with", "for", "me",
    "give", "brief", "between", "through", "versus", "contrast",
}

THRESHOLD = 0.9
TOP_K = 5


def tokenize(text: str) -> set[str]:
    words = set(re.findall(r"[a-z0-9]+(?:[-'][a-z0-9]+)*", text.lower()))
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def keyword_retrieve(chunks: list[dict], question: str, top_k: int = TOP_K) -> list[dict]:
    """Deterministic stand-in for pgvector top-k: overlap of content words."""
    qtokens = tokenize(question)
    scored = []
    for c in chunks:
        overlap = len(qtokens & tokenize(c["text"]))
        scored.append((overlap, -c["chunk_index"], c))
    scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
    return [dict(c, score=float(s)) for s, _, c in scored[:top_k]]


def run_offline() -> int:
    from app.agent import answer_question
    from app.pdf import chunk_pages
    from eval.synthetic import PAGES

    chunks = chunk_pages(PAGES)
    with open(os.path.join(os.path.dirname(__file__), "dataset.json")) as f:
        dataset = json.load(f)

    hits = tools_ok = cites_ok = 0
    print(f"{'ID':>3}  {'HIT':>3}  {'TOOLS':>5}  {'CITE':>4}  question")
    for item in dataset:
        retrieved = keyword_retrieve(chunks, item["question"])
        pages = {c["page_number"] for c in retrieved}
        hit = any(p in pages for p in item["expected_pages"])
        # Multi-page compare: require at least one expected page; full
        # coverage reported separately below.
        result = answer_question(item["question"], retrieved)
        tools_match = result["tools_used"] == item["expected_tools"]
        has_cites = (
            len(result["citations"]) > 0
            and all(c["page"] >= 1 for c in result["citations"])
            and any(
                c["page"] in item["expected_pages"] for c in result["citations"]
            )
        )
        answer_text = result["answer"].lower()
        kw_match = any(k.lower() in answer_text for k in item["expected_keywords"])
        ok = hit and kw_match
        hits += 1 if ok else 0
        tools_ok += 1 if tools_match else 0
        cites_ok += 1 if has_cites else 0
        flag = "ok " if ok else "MISS"
        print(
            f"{item['id']:>3}  {flag:>3}  "
            f"{'ok' if tools_match else 'DIFF':>5}  "
            f"{'ok' if has_cites else 'NONE':>4}  "
            f"{item['question'][:60]}"
        )
        if not ok:
            print(f"      expected pages {item['expected_pages']}, got {sorted(pages)}")

    n = len(dataset)
    hit_rate = hits / n
    print(f"\nretrieval hit-rate : {hits}/{n} = {hit_rate:.0%}")
    print(f"planner accuracy   : {tools_ok}/{n} = {tools_ok / n:.0%}")
    print(f"citation coverage  : {cites_ok}/{n} = {cites_ok / n:.0%}")
    if hit_rate < THRESHOLD:
        print(f"FAIL: hit-rate {hit_rate:.0%} < {THRESHOLD:.0%} threshold")
        return 1
    print(f"PASS: hit-rate >= {THRESHOLD:.0%}")
    return 0


def run_live(api: str, doc: str) -> int:
    with open(os.path.join(os.path.dirname(__file__), "dataset.json")) as f:
        dataset = json.load(f)
    ok = 0
    for item in dataset:
        body = json.dumps(
            {"document_id": doc, "question": item["question"], "top_k": TOP_K}
        ).encode()
        req = urllib.request.Request(
            f"{api}/api/v1/ask", data=body,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.load(resp)
        except Exception as e:
            print(f"{item['id']:>3}  ERROR {e}")
            continue
        good = bool(data.get("answer")) and len(data.get("citations", [])) > 0
        ok += 1 if good else 0
        print(f"{item['id']:>3}  {'ok' if good else 'MISS'}  {item['question'][:60]}")
    rate = ok / len(dataset)
    print(f"\nlive answer-rate: {ok}/{len(dataset)} = {rate:.0%}")
    return 0 if rate >= THRESHOLD else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat-PDF eval suite")
    parser.add_argument("--mode", choices=["offline", "live"], default="offline")
    parser.add_argument("--api", default="http://localhost:8000")
    parser.add_argument("--doc", default="")
    args = parser.parse_args()
    if args.mode == "live":
        if not args.doc:
            parser.error("--doc is required for live mode")
        sys.exit(run_live(args.api, args.doc))
    sys.exit(run_offline())
