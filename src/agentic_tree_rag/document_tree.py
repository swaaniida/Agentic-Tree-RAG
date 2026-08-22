from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import re
from typing import Iterator


@dataclass
class DocumentNode:
    """A section or text leaf in a parsed document hierarchy."""

    node_id: str
    title: str
    text: str = ""
    level: int = 0
    kind: str = "section"
    summary: str = ""
    children: list["DocumentNode"] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)

    @property
    def is_leaf(self) -> bool:
        return not self.children

    def walk(self) -> Iterator["DocumentNode"]:
        yield self
        for child in self.children:
            yield from child.walk()

    def leaves(self) -> list["DocumentNode"]:
        return [node for node in self.walk() if node.is_leaf]

    def all_text(self) -> str:
        return "\n".join(part for part in (self.text, *(c.all_text() for c in self.children)) if part.strip())

    def find(self, node_id: str) -> "DocumentNode | None":
        return next((node for node in self.walk() if node.node_id == node_id), None)


def _stable_id(seed: str, prefix: str) -> str:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def markdown_to_tree(markdown: str, name: str = "document") -> DocumentNode:
    """Convert Markdown headings and paragraphs into a deterministic tree."""

    root = DocumentNode(_stable_id(name, "root"), name, level=0, kind="root")
    stack: list[tuple[int, DocumentNode]] = [(0, root)]
    paragraph_lines: list[str] = []
    paragraph_index = 0

    def flush_paragraph() -> None:
        nonlocal paragraph_index
        text = "\n".join(paragraph_lines).strip()
        paragraph_lines.clear()
        if not text:
            return
        paragraph_index += 1
        parent = stack[-1][1]
        seed = f"{name}:{paragraph_index}:{text[:80]}"
        parent.children.append(
            DocumentNode(
                _stable_id(seed, "text"),
                f"Paragraph {paragraph_index}",
                text=text,
                level=parent.level + 1,
                kind="text",
            )
        )

    for raw_line in markdown.splitlines():
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", raw_line)
        if match:
            flush_paragraph()
            level = len(match.group(1))
            title = match.group(2)
            while stack and stack[-1][0] >= level:
                stack.pop()
            parent = stack[-1][1] if stack else root
            seed = f"{name}:{level}:{title}:{len(list(root.walk()))}"
            section = DocumentNode(
                _stable_id(seed, "section"),
                title,
                level=level,
                kind="section",
            )
            parent.children.append(section)
            stack.append((level, section))
        elif raw_line.strip():
            paragraph_lines.append(raw_line.rstrip())
        else:
            flush_paragraph()

    flush_paragraph()
    return root


def merge_small_leaves(root: DocumentNode, min_chars: int = 100) -> DocumentNode:
    """Merge adjacent short text leaves under the same section."""

    if min_chars < 1:
        raise ValueError("min_chars must be positive")

    for node in list(root.walk()):
        if not node.children:
            continue
        merged: list[DocumentNode] = []
        pending: DocumentNode | None = None
        for child in node.children:
            if child.kind == "text" and len(child.text.strip()) < min_chars:
                if pending is None:
                    pending = child
                else:
                    pending.text = f"{pending.text.rstrip()}\n{child.text.lstrip()}"
                continue
            if pending is not None:
                merged.append(pending)
                pending = None
            merged.append(child)
        if pending is not None:
            merged.append(pending)
        node.children = merged
    return root
