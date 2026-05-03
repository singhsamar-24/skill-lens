from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TextChunk:
    source: str
    title: str
    text: str
    chunk_id: str
    section_index: int
    chunk_index: int


def chunk_markdown(source: str, content: str, *, chunk_size: int = 850, overlap: int = 120) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    title = source.title()
    sections: list[tuple[str, str]] = []
    current_title = title
    current_lines: list[str] = []

    for line in content.splitlines():
        if line.startswith("#"):
            if current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
                current_lines = []
            current_title = line.lstrip("#").strip() or title
        else:
            current_lines.append(line)
    if current_lines:
        sections.append((current_title, "\n".join(current_lines).strip()))

    for section_index, (section_title, section_text) in enumerate(sections):
        normalized = " ".join(section_text.split())
        if not normalized:
            continue
        start = 0
        chunk_index = 0
        while start < len(normalized):
            end = min(len(normalized), start + chunk_size)
            text = normalized[start:end].strip()
            if text:
                chunks.append(
                    TextChunk(
                        source=source,
                        title=section_title,
                        text=text,
                        chunk_id=f"{source}:{section_index}:{chunk_index}",
                        section_index=section_index,
                        chunk_index=chunk_index,
                    )
                )
            if end == len(normalized):
                break
            chunk_index += 1
            start = max(0, end - overlap)
    return chunks
