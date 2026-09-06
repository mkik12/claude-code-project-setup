#!/usr/bin/env python3
"""Repack an unpacked OOXML directory into a .docx, .pptx or .xlsx.

    python scripts/repack.py unpacked/ out.docx

This stands in for `zip -Xr`, which is missing on many Windows machines. It
writes a fresh archive, so a part you deleted from the directory does not
survive into the output. Standard library only.
"""
import pathlib
import sys
import zipfile

CONTENT_TYPES = "[Content_Types].xml"


def repack(source_dir, target):
    """Write every file under source_dir into target as one OOXML package."""
    source = pathlib.Path(source_dir)
    if not (source / CONTENT_TYPES).is_file():
        raise SystemExit(
            f"{source}/{CONTENT_TYPES} is missing. "
            "Point this at the directory you unzipped the file into."
        )

    files = sorted(p for p in source.rglob("*") if p.is_file())
    # [Content_Types].xml goes first. Word reads a package that breaks this
    # convention, but some other readers do not.
    files.sort(key=lambda p: p.relative_to(source).as_posix() != CONTENT_TYPES)

    out = pathlib.Path(target)
    if out.exists():
        # Writing over an existing archive keeps the parts you removed.
        out.unlink()

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(source).as_posix())
    return len(files)


def main():
    """Repack a directory, or print the usage and stop."""
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    count = repack(sys.argv[1], sys.argv[2])
    print(f"wrote {sys.argv[2]} with {count} parts")


if __name__ == "__main__":
    main()
