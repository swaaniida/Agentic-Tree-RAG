from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}
FORBIDDEN_SUFFIXES = {".pdf", ".hwp", ".docx", ".db", ".pkl", ".pem", ".key", ".p12", ".pfx"}
SECRET_PATTERNS = {
    "Google API key": re.compile(r"AIza[0-9A-Za-z_-]{30,}"),
    "OpenAI-style key": re.compile(r"sk-[0-9A-Za-z_-]{20,}"),
    "assigned credential": re.compile(
        r"(?i)(?:api[_-]?key|secret|access[_-]?token)\s*[\]\"']*\s*[:=]\s*[\"'][^\"']{12,}[\"']"
    ),
}
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and not any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts)
    ]


def validate_links(paths: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        if path.suffix.lower() != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        for target in LINK_PATTERN.findall(text):
            target = target.strip().split("#", 1)[0]
            if not target or re.match(r"^(?:https?://|mailto:)", target):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"broken link: {path.relative_to(ROOT)} -> {target}")
    return errors


def validate_notebook(path: Path) -> list[str]:
    errors: list[str] = []
    notebook = json.loads(path.read_text(encoding="utf-8"))
    for index, cell in enumerate(notebook.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        if cell.get("outputs"):
            errors.append(f"notebook output remains: {path.name} cell {index}")
        source = "".join(cell.get("source", []))
        try:
            ast.parse(source)
        except SyntaxError as exc:
            errors.append(f"notebook syntax: {path.name} cell {index}: {exc}")
    return errors


def main() -> int:
    paths = files()
    errors = validate_links(paths)

    for path in paths:
        relative = path.relative_to(ROOT)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"forbidden file type: {relative}")
        if path.stat().st_size > 20 * 1024 * 1024:
            errors.append(f"file larger than 20 MiB: {relative}")
        if path.suffix.lower() in {".json", ".ipynb"}:
            try:
                json.loads(path.read_text(encoding="utf-8-sig"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                errors.append(f"invalid JSON: {relative}: {exc}")
        if path.suffix.lower() == ".ipynb":
            errors.extend(validate_notebook(path))
        if path.suffix.lower() in {".py", ".md", ".json", ".ipynb", ".toml", ".txt", ".env"} or path.name == ".env.example":
            text = path.read_text(encoding="utf-8", errors="ignore")
            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(text):
                    errors.append(f"possible {label}: {relative}")

    print(f"files: {len(paths)}")
    print(f"markdown: {sum(path.suffix.lower() == '.md' for path in paths)}")
    print(f"json/notebooks: {sum(path.suffix.lower() in {'.json', '.ipynb'} for path in paths)}")
    print(f"validation errors: {len(errors)}")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
