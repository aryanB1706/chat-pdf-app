"""Agentic Q&A: LLM plans and calls tools (retrieve, summarize, compare).

Returns structured JSON with page-level citations so every answer is
traceable. Phase 4 will wrap `generate_text` with gateway fallback,
caching and token/latency logging — the agent interface stays the same.
"""

from .config import settings


def plan_tools(question: str) -> list[str]:
    """Rule-based planner: pick tools from question intent."""
    q = question.lower()
    if any(w in q for w in ("summariz", "summaris", "summary", "tl;dr", "brief")):
        return ["retrieve", "summarize"]
    if any(w in q for w in ("compar", "differ", " vs ", "versus", "contrast")):
        return ["retrieve", "compare"]
    return ["retrieve"]


def build_citations(chunks: list[dict], excerpt_len: int = 200) -> list[dict]:
    return [
        {
            "page": c["page_number"],
            "chunk_index": c["chunk_index"],
            "excerpt": c["text"][:excerpt_len],
        }
        for c in chunks
    ]


def generate_text(question: str, chunks: list[dict], mode: str) -> str:
    """Draft answer text with Gemini; extractive fallback without API key."""
    context = "\n\n".join(
        f"[Page {c['page_number']}] {c['text']}" for c in chunks
    )
    if mode == "summarize":
        instruction = "Summarize the context below in 3-5 bullet points."
    elif mode == "compare":
        instruction = (
            "Compare the topics across the pages below. "
            "Group points by page number and note agreements/differences."
        )
    else:
        instruction = "Answer the question using ONLY the context below."

    if settings.gemini_api_key:
        try:
            import google.generativeai as genai

            if not getattr(generate_text, "_configured", False):
                genai.configure(api_key=settings.gemini_api_key)
                generate_text._configured = True  # type: ignore[attr-defined]
            model = genai.GenerativeModel(settings.primary_llm_model)
            prompt = f"{instruction}\n\nQuestion: {question}\n\nContext:\n{context[:15000]}"
            return model.generate_content(prompt).text.strip()
        except Exception as e:
            print(f"[agent] LLM failed, extractive fallback: {e}")

    # Extractive fallback (no key / LLM error): traceable by construction.
    if not chunks:
        return "No relevant content found in this document."
    if mode == "summarize":
        bullets = "\n".join(
            f"- (Page {c['page_number']}) {c['text'][:220]}" for c in chunks[:5]
        )
        return f"Summary of the most relevant sections:\n{bullets}"
    if mode == "compare":
        by_page: dict[int, list[str]] = {}
        for c in chunks:
            by_page.setdefault(c["page_number"], []).append(c["text"][:220])
        lines = []
        for page in sorted(by_page):
            lines.append(f"Page {page}: {'; '.join(by_page[page])}")
        return "Comparison across pages:\n" + "\n".join(lines)
    top = chunks[0]
    return f"Based on page {top['page_number']}: {top['text'][:500]}"


def answer_question(
    question: str,
    chunks: list[dict],
    tools_used: list[str] | None = None,
) -> dict:
    """Assemble the structured JSON answer with page-level citations."""
    planned = tools_used or plan_tools(question)
    mode = "summarize" if "summarize" in planned else "compare" if "compare" in planned else "ask"
    return {
        "answer": generate_text(question, chunks, mode),
        "citations": build_citations(chunks),
        "tools_used": planned,
    }
