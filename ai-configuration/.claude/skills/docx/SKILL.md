---
name: docx
description: "Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files) or Word templates (.dotx files). Triggers include: any mention of 'Word doc', 'word document', '.docx', '.dotx', or requests to produce professional documents with formatting like tables of contents, headings, page numbers, or letterheads. Also use when extracting or reorganizing content from .docx or .dotx files, inserting or replacing images in documents, performing find-and-replace in Word files, working with tracked changes or comments, or converting content into a polished Word document. If the user asks for a 'report', 'memo', 'letter', 'template', or similar deliverable as a Word or .docx file, use this skill. Do NOT use for PDFs, spreadsheets, Google Docs, or general coding tasks unrelated to document generation."
---

# DOCX creation, editing, and analysis

A `.docx` is a ZIP archive of XML parts. **python-docx is the only route here.**
Node, LibreOffice, `pandoc` and `zip` are absent from the target machine, so
docx-js, a rendered preview and an unpack-edit-repack loop are all out.

The library reaches the XML for you. `document.element` and every `_element`
attribute below it give you the lxml tree, so anything the API misses is still
one `OxmlElement` away. Never unpack the file to disk.

`pip install python-docx` gives the `docx` module. The import name is `docx`,
not `python_docx`.

Every code block below was run, and its output passed a schema check against
ECMA-376. Do not rewrite one from memory.

## Read a document

```bash
markitdown report.docx          # the whole document as Markdown, fastest
```

Read the structure with the library when you need the paragraph styles, the
tables, or a run:

```python
from docx import Document

doc = Document("report.docx")
for para in doc.paragraphs:
    print(para.style.name, para.text)
for table in doc.tables:
    for row in table.rows:
        print([cell.text for cell in row.cells])
```

## Two gotchas that make an invalid file

Fix both on every document you create. Neither is obvious, and one of them is
visible to the user.

**1. A field does not refresh by itself.** A `TOC` field renders **blank** until
something tells Word to update it. The `w:updateFields` setting does that. But
`CT_Settings` is an ordered sequence in ECMA-376, so an append to the end of
`settings.xml` gives `This element is not expected` and a broken file. Insert
the element before its schema successors instead.

**2. python-docx writes `<w:zoom/>` with no `percent`.** The attribute is
required, so every document from the default template fails a schema check until
you set it. Word tolerates the omission, so this one costs you nothing in Word
and fails in a stricter reader.

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# The elements that follow w:updateFields in CT_Settings, read out of wml.xsd.
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
    """Insert a Word field, such as PAGE, NUMPAGES, or a TOC instruction."""
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

## The rest of the API

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
`Light List` and `Light Grid`. A template you open yourself may define more.

## Four traps in the content itself

- **Never write a literal bullet character.** Use the `List Bullet` style. A
  literal one gives two bullets, or one with no indent.
- **Never put a newline inside a run.** It does nothing. Add a paragraph for
  each line.
- **A TOC only sees a built-in heading style.** `doc.add_heading(text, 1)` gives
  `Heading 1`, which the TOC finds. A custom style needs an outline level, or it
  does not appear. `doc.add_heading(text, 0)` gives the `Title` style, and a TOC
  built with `\o "1-3"` does **not** list it. That is correct for a document
  title, and it surprises you when you used level 0 for a section.
- **Do not draw a horizontal rule with a table.** Put a bottom border on an
  empty paragraph.

## Edit an existing document

Open it, change it, then save it under a new name. Keep the original.

**Word splits one visible phrase across many runs.** A revision id or a
spell-check marker starts a new `<w:r>`, so the text you can see often does not
exist as one string. `paragraph.text` joins the runs and reads correctly, but a
find-and-replace over `run.text` then misses the phrase. Replace at the
paragraph level, and rebuild the runs:

```python
def replace_in_paragraph(paragraph, old, new):
    """Replace text that Word split across several runs."""
    if old not in paragraph.text:
        return
    merged = paragraph.text.replace(old, new)  # read it BEFORE you drop a run
    for run in paragraph.runs[1:]:             # keep run 0 and its formatting
        run._r.getparent().remove(run._r)
    paragraph.runs[0].text = merged
```

This flattens the formatting of the paragraph onto the first run. That is the
trade, and it is visible: bold on a word inside the replaced paragraph is gone
after the call. When the mixed formatting must survive, walk the runs one by
one, and accept that a phrase across two runs needs both of them.

A legacy `.doc` is a different format, and nothing here reads it. Ask the user
to open it in Word and to save it as `.docx`.

## Tracked changes and comments

python-docx has no API for either. Both are reachable through the XML, and both
have a shape that is easy to get wrong.

**Tracked changes.** Wrap a run in `<w:ins>` or `<w:del>`, with `w:id`,
`w:author` and `w:date` attributes. Inside `<w:del>` the text element is
`<w:delText>`, not `<w:t>`. A deleted paragraph mark means "join this paragraph
to the next one", and it is written as `<w:del/>` inside the `<w:rPr>` of the
`<w:pPr>`. To delete a whole paragraph you need that **and** a `<w:del>` around
every run. The `<w:del/>` must come before the other children of the `rPr`,
because the schema fixes their order.

**Comments.** A comment needs six cross-linked parts: `comments.xml`,
`commentsExtended.xml`, `commentsIds.xml`, `commentsExtensible.xml`, the
relationship, and the content-type override. It also needs three markers in
`document.xml`: `<w:commentRangeStart>`, `<w:commentRangeEnd>` and
`<w:commentReference>`. Without the markers the comment exists in the file and
stays invisible in Word. This is a large amount of hand-built XML. Say so, and
agree the cost with the user before you start.

## Verify

Nothing here renders a document, and the ECMA-376 schemas are too big to ship,
so there is no structural check either. Two things you can still do:

1. **Reopen the file with python-docx** and read back the headings, the tables
   and the text you wrote. This catches an empty document and a lost section.
2. **Ask the user to open it in Word.** This is the only real check, and the
   only one that sees the layout.

Never report the layout as checked. Say which parts you read back, then say that
Word has not opened the file yet.

## What python-docx cannot do

- a chart. Build the data as a table instead, or make the chart a picture.
- a header or footer that differs on the first page, unless you set
  `section.different_first_page_header_footer` and accept the limits.
- most of the format. Reach for `OxmlElement` and the lxml tree for the rest.
