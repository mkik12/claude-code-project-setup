# Creating a .docx with python-docx

The Node-free route. Use it when `node` is absent, and read
[SKILL.md](../SKILL.md) for the docx-js route when `node` is present.

Every snippet here was run and the output passed
`python scripts/office/validate.py`.

`pip install python-docx` provides the `docx` module. The import name is `docx`,
not `python_docx`.

## Two gotchas that fail the schema

Fix both on every document you create. Neither is optional, and neither is
obvious.

**1. A field does not refresh by itself.** A `TOC` field renders blank until
something tells Word to update it. The `w:updateFields` setting does that, but
`CT_Settings` is an ordered sequence in ECMA-376, so appending the element to the
end of `settings.xml` produces `This element is not expected` and an invalid
file. Insert it before its schema successors instead.

**2. python-docx writes `<w:zoom/>` with no `percent`.** The attribute is
required, so every document from the default template fails schema validation
until you set it. Word itself tolerates the omission, which is why the library
gets away with it.

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# The elements that follow w:updateFields in CT_Settings. Taken from the
# bundled scripts/office/schemas/ISO-IEC29500-4_2016/wml.xsd.
_AFTER_UPDATE_FIELDS = ("w:compat", "w:rsids", "w:themeFontLang",
                        "w:clrSchemeMapping", "w:doNotAutoCompressPictures",
                        "w:shapeDefaults", "w:decimalSymbol", "w:listSeparator")


def force_field_update(document):
    """Make Word refresh every field on open, so a TOC is not blank."""
    settings = document.settings.element
    if settings.find(qn("w:updateFields")) is not None:
        return
    upd = OxmlElement("w:updateFields")
    upd.set(qn("w:val"), "true")
    settings.insert_element_before(upd, *_AFTER_UPDATE_FIELDS)


def fix_default_zoom(document):
    """python-docx ships <w:zoom/> with no percent, which fails the schema."""
    zoom = document.settings.element.find(qn("w:zoom"))
    if zoom is not None and zoom.get(qn("w:percent")) is None:
        zoom.set(qn("w:percent"), "100")
```

## Fields: page numbers and a table of contents

python-docx has no field API, so build the three-element run by hand.

```python
def add_field(paragraph, instr):
    """Insert a Word field, e.g. PAGE, NUMPAGES, or a TOC instruction."""
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    text = OxmlElement("w:instrText")
    text.set(qn("xml:space"), "preserve")
    text.text = instr
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    for el in (begin, text, end):
        run._r.append(el)
```

A table of contents, which needs `force_field_update` to render:

```python
add_field(doc.add_paragraph(), r'TOC \o "1-3" \h \z \u')
```

A centred `Page N of M` footer:

```python
footer = doc.sections[0].footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
footer.text = "Page "
add_field(footer, "PAGE")
footer.add_run(" of ")
add_field(footer, "NUMPAGES")
```

## The rest of it

```python
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT

doc = Document()

section = doc.sections[0]                      # margins
section.left_margin = section.right_margin = Inches(1)

doc.add_heading("Title", 0)                    # 0 is the document title
doc.add_heading("Section", 1)                  # 1-9 are heading levels

para = doc.add_paragraph("Exposure rose ")     # mixed formatting in one line
para.add_run("12%").bold = True
para.add_run(" this quarter.")

doc.add_paragraph("A point", style="List Bullet")     # built-in styles
doc.add_paragraph("A step", style="List Number")
doc.add_paragraph("A quote", style="Intense Quote")

doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)  # page break

doc.add_picture("logo.png", width=Inches(2))
```

A table with a bold header row:

```python
table = doc.add_table(rows=1, cols=3)
table.style = "Table Grid"
table.alignment = WD_TABLE_ALIGNMENT.CENTER
for cell, head in zip(table.rows[0].cells, ("Segment", "Exposure", "Change")):
    cell.paragraphs[0].add_run(head).bold = True
for values in (("Retail", "1.2bn", "+8%"), ("Corporate", "3.4bn", "+14%")):
    for cell, value in zip(table.add_row().cells, values):
        cell.text = value
```

`Table Grid` is the style to reach for. A style name that the default template
does not carry raises `KeyError`, so stay with `Table Grid`, `Light Shading`,
`Light List` and `Light Grid` unless you are working from a template that
defines more.

## Verify

```bash
python scripts/office/validate.py output.docx
```

The XSD check is pure Python and needs no LibreOffice. It catches a bad field, a
broken relationship and an out-of-order element. It cannot tell you whether the
page looks right, so say that the layout is unverified when you hand the file
over.

## What python-docx cannot do

Reach for direct XML editing (see [SKILL.md](../SKILL.md)) for any of these:

- tracked changes and comments
- a chart
- a header or footer that differs on the first page, unless you set
  `section.different_first_page_header_footer` and accept the limits
- anything the library has no API for, which is most of the format
