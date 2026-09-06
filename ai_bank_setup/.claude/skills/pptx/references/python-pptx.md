# Creating a .pptx with python-pptx

The Node-free route. Use it when `node` is absent, and read
[SKILL.md](../SKILL.md) for the pptxgenjs route when `node` is present.

Every snippet here was run and the output passed
`python scripts/office/validate.py`.

`pip install python-pptx` provides the `pptx` module.

## The first gotcha: it defaults to 4:3

Set the slide size before you add a slide. Nobody wants 4:3.

```python
from pptx import Presentation
from pptx.util import Inches


def widescreen():
    """A 16:9 deck at 13.333 x 7.5 inches."""
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs
```

Every measurement below assumes that canvas. A 0.8 inch margin on each side
leaves 11.7 inches of usable width.

## Layouts

`prs.slide_layouts` indexes the default template. Three of them do all the work:

| Index | Layout | Use it for |
| :--- | :--- | :--- |
| 0 | Title | the opening slide |
| 1 | Title and Content | anything with bullets |
| 6 | Blank | full control by exact position |

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "Quarterly Exposure"
slide.placeholders[1].text = "Finance, Q3"
```

Bullets with nesting, and speaker notes:

```python
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = "Findings"
body = slide.placeholders[1].text_frame
body.text = "Retail exposure rose 8%"          # the first line, not add_paragraph
for line, level in (("Corporate rose 14%", 0), ("Driven by two clients", 1)):
    para = body.add_paragraph()
    para.text = line
    para.level = level

slide.notes_slide.notes_text_frame.text = "Mention the two clients by name."
```

`text_frame.text` sets the first paragraph. Calling `add_paragraph()` for the
first line leaves an empty bullet above it.

## Exact positioning on a blank slide

```python
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

INK = RGBColor(0x1A, 0x1A, 0x1A)
ACCENT = RGBColor(0x00, 0x5A, 0xA0)


def textbox(slide, left, top, width, height, text, size=18, bold=False,
            color=INK, align=PP_ALIGN.LEFT):
    """Place a text box at an exact position, in inches."""
    box = slide.shapes.add_textbox(Inches(left), Inches(top),
                                   Inches(width), Inches(height))
    frame = box.text_frame
    frame.word_wrap = True
    frame.vertical_anchor = MSO_ANCHOR.TOP
    para = frame.paragraphs[0]
    para.alignment = align
    run = para.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return frame
```

Set `word_wrap = True` on every box. Without it a long line runs off the slide
instead of wrapping, and you have no renderer to catch it.

## Tables

```python
shape = slide.shapes.add_table(3, 3, Inches(0.8), Inches(1.9),
                               Inches(6.0), Inches(1.8))
table = shape.table
for col, head in enumerate(("Segment", "Exposure", "Change")):
    table.cell(0, col).text = head
for row, values in enumerate((("Retail", "1.2bn", "+8%"),
                              ("Corporate", "3.4bn", "+14%")), start=1):
    for col, value in enumerate(values):
        table.cell(row, col).text = value
```

Row count and column count are fixed at creation. There is no `add_row`.

## Charts

python-pptx writes chart XML that PowerPoint opens. This is its clearest
advantage over pptxgenjs, whose chart XML PowerPoint refuses while every other
tool accepts it.

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

data = CategoryChartData()
data.categories = ["Retail", "Corporate"]
data.add_series("Exposure", (1.2, 3.4))

frame = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,
                               Inches(7.2), Inches(1.9),
                               Inches(5.3), Inches(4.4), data)
chart = frame.chart
chart.has_legend = True
chart.legend.position = XL_LEGEND_POSITION.BOTTOM
chart.legend.include_in_layout = False
```

Set `include_in_layout = False` or the legend overlaps the plot.

## Images

```python
slide.shapes.add_picture("logo.png", Inches(4.7), Inches(2.4), Inches(4.0))
```

Give width or height, not both, and the other scales. Giving both distorts the
image, and you have no preview to notice it in.

## Verify

```bash
python scripts/office/validate.py output.pptx
```

Schemas, relationships, content types and chart XML. Pure Python, no
LibreOffice. It cannot see the slide, so Visual QA in [SKILL.md](../SKILL.md)
does not apply on a machine without `soffice`.

Because nothing renders the deck, text overflow is the defect you cannot check
and the one that happens most. Two habits cover for it:

- leave 10% slack in every text box, and more on a font you did not measure
- keep a line under about 60 characters at 18pt on an 11.7 inch width

## What python-pptx cannot do

Reach for direct XML editing (see [SKILL.md](../SKILL.md)) for these:

- reordering or deleting slides, which means editing `p:sldIdLst`
- comments
- SmartArt
- a slide master or a new layout
