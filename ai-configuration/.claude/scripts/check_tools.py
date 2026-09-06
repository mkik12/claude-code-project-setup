#!/usr/bin/env python3
"""Report which document tools this machine actually has.

    python .claude/scripts/check_tools.py

A skill in `.claude/skills/` names the library it needs. Run this before
document work rather than guessing, and install what the report says is
missing.

The list holds only what this configuration uses. LibreOffice, Node, `zip`,
`pandoc` and `tesseract` are absent from the target machine by design, so no
skill offers a route through them and this script does not look for them.

Exit code is always 0. A missing tool is information, not a failure.
"""
import importlib
import shutil
import sys

BINARIES = {
    "git": "version control",
    "pdftotext": "extract text from a PDF, faster than Python for a big file",
    "pdftoppm": "turn PDF pages into images",
    "pdfimages": "extract embedded images from a PDF",
    "qpdf": "merge, split and repair PDFs",
}

MODULES = {
    "docx": "python-docx: create and edit Word files",
    "pptx": "python-pptx: create and edit decks",
    "openpyxl": "read and write .xlsx",
    "pandas": "tabular data handling",
    "pypdf": "merge, split, rotate and encrypt PDFs, and fill a form",
    "pdfplumber": "extract text and tables from a PDF",
    "reportlab": "create a PDF from scratch",
    "PIL": "Pillow: images and thumbnails",
    "lxml": "XML handling, under python-docx and python-pptx",
    "markitdown": "dump an Office file to Markdown, to read it fast",
    "oracledb": "read LDWH1",
    "psycopg": "the application database",
}

PIP_NAMES = {
    "docx": "python-docx", "pptx": "python-pptx", "PIL": "Pillow",
    "psycopg": "psycopg[pool]",
}


def _module_state(name):
    """Return (present, note). Guards against a sibling folder shadowing."""
    try:
        module = importlib.import_module(name)
    except Exception:
        return False, ""
    # A directory named `docx` or `pptx` on sys.path imports as a namespace
    # package with __file__ of None. Running this from inside .claude/skills/
    # does exactly that, and the real library then looks installed when it is
    # not.
    if getattr(module, "__file__", None) is None:
        return False, "shadowed by a local folder of the same name"
    return True, getattr(module, "__version__", "") or ""


def main():
    missing_pip = []
    print("binaries")
    for name, why in BINARIES.items():
        found = shutil.which(name) is not None
        print(f"  [{'x' if found else ' '}] {name:<11} {why}")

    print("\npython packages")
    for name, why in MODULES.items():
        present, note = _module_state(name)
        if not present:
            missing_pip.append(PIP_NAMES.get(name, name))
        suffix = f" ({note})" if note else ""
        print(f"  [{'x' if present else ' '}] {name:<11} {why}{suffix}")

    if missing_pip:
        print("\nto install the missing packages:")
        print("  pip install " + " ".join(missing_pip))

    if any("shadowed" in _module_state(n)[1] for n in MODULES):
        print("\nWARNING: run this from the project root, not from "
              ".claude/skills/. A folder there shares a name with a package.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
