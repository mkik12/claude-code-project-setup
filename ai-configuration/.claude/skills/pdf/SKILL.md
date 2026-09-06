---
name: pdf
description: Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text and tables from PDFs, combining or merging multiple PDFs into one, splitting PDFs apart, rotating pages, adding watermarks, creating new PDFs, filling PDF forms, encrypting or decrypting PDFs, and extracting images. If the user mentions a .pdf file or asks to produce one, use this skill.
---

# PDF processing

Three libraries cover the work, and all three are pure Python.

| Task | Library |
| :--- | :--- |
| merge, split, rotate, watermark, encrypt, read a form | `pypdf` |
| extract text with the layout, extract a table, read coordinates | `pdfplumber` |
| create a PDF | `reportlab` |

`pdftotext` is on the target machine and is the fastest way to dump a long
document. `qpdf`, `pdftoppm`, `pdfimages` and `tesseract` are **not**. So
nothing here turns a page into an image, and nothing here reads a scanned page.

## Read a PDF

```bash
pdftotext -layout report.pdf -      # to stdout, columns preserved
pdftotext -f 1 -l 5 report.pdf out.txt
```

`pdfplumber` when you need the tables or the coordinates:

```python
import pdfplumber

with pdfplumber.open("report.pdf") as pdf:
    for page in pdf.pages:
        print(page.extract_text())
        for table in page.extract_tables():
            for row in table:
                print(row)
```

**A scanned PDF holds no text layer**, so both routes return an empty string or
a `(cid:NN)` pattern. There is no OCR here. Say that the file is an image, and
ask the user for a text version.

## Merge, split, rotate, watermark, encrypt

```python
from pypdf import PdfReader, PdfWriter

writer = PdfWriter()                                   # merge
for name in ("a.pdf", "b.pdf"):
    for page in PdfReader(name).pages:
        writer.add_page(page)
with open("merged.pdf", "wb") as out:
    writer.write(out)

reader = PdfReader("input.pdf")                        # split, rotate, stamp
stamp = PdfReader("watermark.pdf").pages[0]
for i, page in enumerate(reader.pages, start=1):
    page.rotate(90)
    page.merge_page(stamp)                             # stamp goes on top
    single = PdfWriter()
    single.add_page(page)
    with open(f"page_{i}.pdf", "wb") as out:
        single.write(out)

writer.encrypt("user-password", "owner-password")      # before write()
```

`page.rotate()` takes a multiple of 90 and turns clockwise. `merge_page` puts
the stamp over the page, so a filled watermark hides the text under it. Use a
transparent or a light one.

## Create a PDF

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

styles = getSampleStyleSheet()
story = [Paragraph("Quarterly Exposure", styles["Title"]), Spacer(1, 12)]
story.append(Paragraph("Retail exposure rose 8%.", styles["Normal"]))
story.append(PageBreak())
story.append(Paragraph("Appendix", styles["Heading1"]))

SimpleDocTemplate("report.pdf", pagesize=A4).build(story)
```

Use `SimpleDocTemplate` and a story for anything that flows across pages. Reach
for a bare `canvas` only for exact placement on one page.

**Never write a Unicode subscript or superscript character into a reportlab
PDF.** The built-in fonts carry no glyph for one, so it renders as a solid black
box. Use the markup tags inside a `Paragraph` instead:

```python
Paragraph("H<sub>2</sub>O and x<super>2</super>", styles["Normal"])
```

For text drawn on a `canvas`, there is no markup. Change the font size and the
position by hand.

## Fill a form

**Find out first whether the form has real fields.** The two routes share
nothing.

```python
reader = PdfReader("form.pdf")
fields = reader.get_fields()          # None or {} means there are no fields
```

**With fields.** Each entry gives the field type and, for a checkbox or a radio
group, the exact values it accepts. Read them out rather than guessing, because
a checkbox rarely takes `True`.

```python
from pypdf.generic import NameObject, BooleanObject

writer = PdfWriter(clone_from="form.pdf")
writer.set_need_appearances_writer(True)
writer.update_page_form_field_values(
    writer.pages[0], {"last_name": "Simpson", "over_18": "/On"})
```

`set_need_appearances_writer(True)` tells the reader to draw the value. Without
it the field holds the text and the page looks empty.

**Without fields**, you draw the text onto the page. Get the coordinates from
`pdfplumber`, because nothing here renders a page for you to look at:

- `page.extract_words()` gives every label with `x0`, `top`, `x1`, `bottom`
- `page.rects` gives the boxes, and a small square is a checkbox
- `page.lines` gives the horizontal rules that separate the rows

An entry area starts a few points after its label ends, and it stops at the next
label or at the row boundary. Build a one-page overlay with reportlab at the
same page size, then merge it:

```python
page.merge_page(PdfReader("overlay.pdf").pages[0])
```

**pdfplumber and reportlab count the y axis from opposite ends.** pdfplumber
gives `top` as the distance down from the top of the page. reportlab draws from
the bottom. Convert with `y = page_height - top - font_size`, and check one
field before you place forty.

## Verify

Extract the text back out of the file you wrote, and compare it against what you
put in. This catches a missing page, a lost field value and an overlay that
landed on the wrong page.

It does not show the layout, because nothing here renders a page. Never report a
PDF as visually checked. Ask the user to open it.
