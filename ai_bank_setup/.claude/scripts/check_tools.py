#!/usr/bin/env python3
"""Report which document tools this machine actually has.

    python .claude/scripts/check_tools.py

The skills in `.claude/skills/` each offer more than one route to the same
result, and which route works depends on what is installed. Run this before
document work rather than guessing, and read the "Environment" section of the
skill you are about to use.

Exit code is always 0. A missing tool is information, not a failure.
"""
import importlib
import shutil
import sys

BINARIES = {
    "git": "version control",
    "unzip": "unpack a .docx or .pptx for direct XML editing",
    "zip": "repack it again; Python's zipfile covers this if absent",
    "soffice": "render Office files, recalculate formulas, convert legacy formats",
    "node": "docx-js and pptxgenjs, the richer creation route",
    "npm": "install the Node libraries",
    "pandoc": "convert Markdown to .docx",
    "pdftotext": "extract text from a PDF",
    "pdftoppm": "turn PDF pages into images",
    "pdfimages": "extract embedded images from a PDF",
    "qpdf": "merge, split and repair PDFs",
    "tesseract": "OCR a scanned PDF",
}

MODULES = {
    "docx": "python-docx: create and edit Word files",
    "pptx": "python-pptx: create and edit decks",
    "openpyxl": "read and write .xlsx",
    "pandas": "tabular data handling",
    "pypdf": "merge, split and rotate PDFs",
    "pdfplumber": "extract text and tables from a PDF",
    "reportlab": "create a PDF from scratch",
    "PIL": "Pillow: images and thumbnails",
    "lxml": "XML handling and schema validation",
    "defusedxml": "needed by scripts/office/validate.py",
    "markitdown": "dump an Office file to Markdown",
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
