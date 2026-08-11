"""PDF parsing + page-aware chunking for long documents (500+ pages)."""

from pypdf import PdfReader

from .config import settings


def extract_pages(pdf_path: str) -> list[str]:
    """Return one text string per page. Empty pages become ''."""
    reader = PdfReader(pdf_path)
    pages: list[str] = []
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        pages.append(text.strip())
    return pages


def chunk_page_text(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[str]:
    """Split a single page into overlapping char chunks."""
    size = chunk_size or settings.chunk_size_chars
    ov = overlap or settings.chunk_overlap_chars
    text = text.strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]
    chunks: list[str] = []
    step = max(size - ov, 1)
    for start in range(0, len(text), step):
        piece = text[start:start + size].strip()
        if piece:
            chunks.append(piece)
        if start + size >= len(text):
            break
    return chunks


def chunk_pages(pages: list[str]) -> list[dict]:
    """Flatten pages -> [{page_number (1-based), chunk_index, text}]."""
    out: list[dict] = []
    idx = 0
    for i, page_text in enumerate(pages):
        for piece in chunk_page_text(page_text):
            out.append(
                {"page_number": i + 1, "chunk_index": idx, "text": piece}
            )
            idx += 1
    return out
