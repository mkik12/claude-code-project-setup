---
name: pptx
description: "Use this skill any time a .pptx or .potx file is involved in any way - as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx or .potx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates (.potx), layouts, speaker notes, or comments. Trigger whenever the user mentions \"deck,\" \"slides,\" \"presentation,\" or references a .pptx or .potx filename, regardless of what they plan to do with the content afterward. If a .pptx or .potx file needs to be opened, created, or touched, use this skill."
---

# PPTX creation, editing, and analysis

A `.pptx` is a ZIP archive of XML parts. **python-pptx is the only route here.**
Node, LibreOffice and `zip` are absent from the target machine, so pptxgenjs, a
thumbnail grid and any rendered preview are all out.

This is not a downgrade for charts. python-pptx writes chart XML that PowerPoint
opens. pptxgenjs writes chart XML that PowerPoint refuses and every other tool
accepts, so the Python route is the better one here, not the fallback.

`pip install python-pptx` gives the `pptx` module. Every code block below was
run, and its output passed a schema check against ECMA-376. Do not rewrite one
from memory.

**Nothing renders the deck.** Text overflow is the most common defect and the
one you cannot see. Read "Verify" before you size a text box.

## Read a deck

```bash
markitdown deck.pptx      # one block per slide, under a slide-number marker
```

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

## The second gotcha: the placeholders stay 4:3

`Presentation()` loads a 4:3 template. The two lines above resize the **canvas**
and leave every layout placeholder where the template put it. So a title on
layout 0 or 1 still ends at 9.25 inches on a 13.333 inch slide, and the right
quarter of the deck is empty. Measured, not guessed: the title placeholder is
0.75 to 9.25, and the body placeholder is 0.50 to 9.50.

Nothing renders the deck here, so this defect never announces itself.

**The repair has its own trap, and it is worse than the defect.** A placeholder
that inherits its position carries no `<a:xfrm>` of its own. The first write to
any one of `left`, `top`, `width` or `height` creates that element, and it
writes **zero** into the three you did not set. So a helper that sets `left` and
`width` puts every placeholder at `top=0` with `height=0`, and the title and the
subtitle then land on top of each other at the edge of the slide. Measured: a
title inherits `top=2.33 height=1.61` and reads back `top=0.00 height=0.00`
after a write to `left` alone.

Read all four, then write all four:

```python
MARGIN = Inches(0.8)


def fit_placeholders(slide, presentation, margin=MARGIN):
    """Widen every placeholder to the canvas, and keep its vertical geometry."""
    usable = presentation.slide_width - 2 * margin
    for shape in slide.placeholders:
        top, height = shape.top, shape.height   # read before the first write
        shape.left = margin
        shape.top = top                         # a write drops what you skip
        shape.width = usable
        shape.height = height
```

The same rule holds anywhere you move a placeholder, not only here. Read the
whole geometry first.

A slide on layout 6 (Blank) has no placeholder and needs none of this, because
you set every position yourself. For a deck built from scratch that is the
simpler road: layout 6 and the `textbox` helper below, with no inherited
geometry to repair.

## Layouts, bullets and notes

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

`text_frame.text` sets the first paragraph. A call to `add_paragraph()` for the
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
instead of wrapping, and no renderer here catches that.

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

The row count and the column count are fixed at creation. There is no `add_row`.

## Charts

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

Set `include_in_layout = False`, or the legend overlaps the plot.

**Turn the legend off when there is one series.** PowerPoint then colors each
bar differently and lists the **categories** in the legend, not the series, so
the legend repeats the category axis and adds nothing. Set
`chart.has_legend = False` and put the series name in the chart title. Keep the
legend from two series up.

Keep a chart native. A picture of a chart cannot be edited, and it looks soft
on a projector. Only a shape PowerPoint has no native form for, such as a
Sankey or a network diagram, goes in as an image.

## Images

```python
slide.shapes.add_picture("logo.png", Inches(4.7), Inches(2.4), Inches(4.0))
```

Give the width or the height, not both, and the other one scales. Both together
distort the image, and no preview here shows you that.

## Work from a template

A `.potx` and a `.pptx` open the same way. Three limits decide the approach:

- **python-pptx cannot duplicate a slide.** The only entry point is
  `add_slide(layout)`. To repeat a template design, add a slide on the same
  layout and fill it again.
- **`text_frame.text = "..."` destroys the formatting.** It collapses the
  paragraph into one unstyled run. Assign `run.text` instead, and keep the run
  that the template built.
- **`add_picture` cannot read SVG or EMF**, which is what most template art
  uses. It raises `UnidentifiedImageError`. Reuse the picture that is on the
  layout already.

Two more traps when you fill a template in:

- **A template slot is not a source item.** When the template shows four team
  members and you have three, remove the whole fourth group, which means the
  picture and every text box. Text alone leaves an orphan image behind.
- **Never round-trip the XML through `xml.etree.ElementTree`.** It rewrites the
  namespace prefixes and breaks the deck. Stay inside python-pptx, which uses
  lxml and keeps them.

## Design

**Do not make a boring deck.** Plain bullets on white impress nobody.

- **Pick a palette that fits the topic.** When your colors would work just as
  well in an unrelated deck, they are not specific enough. Do not default to
  blue.
- **One color dominates**, at 60 to 70 percent of the visual weight. Add one or
  two supporting tones and one sharp accent. Equal weight reads as noise.
- **Dark for the title and the closing slide, light for the content.** Or commit
  to dark throughout.
- **Repeat one motif** across every slide, such as a rounded image frame or an
  icon in a colored circle.

| Theme | Primary | Secondary | Accent |
| :--- | :--- | :--- | :--- |
| Midnight Executive | `1E2761` navy | `CADCFC` ice blue | `FFFFFF` white |
| Forest and Moss | `2C5F2D` forest | `97BC62` moss | `F5F5F5` cream |
| Warm Terracotta | `B85042` terracotta | `E7E8D1` sand | `A7BEAE` sage |
| Ocean Gradient | `065A82` deep blue | `1C7293` teal | `21295C` midnight |
| Charcoal Minimal | `36454F` charcoal | `F2F2F2` off-white | `212121` black |
| Berry and Cream | `6D2E46` berry | `A26769` dusty rose | `ECE2D0` cream |

**Every slide needs one visual element**: an image, a chart, an icon or a shape.
A text-only slide is forgettable. Vary the layout across the deck: two columns,
icon rows, a 2x2 grid, a half-bleed image with the content beside it. For data,
reach for a large stat callout, a comparison column or a numbered process flow.

**Fonts.** Choose a face that ships with Office: Arial, Calibri, Cambria, Times
New Roman, Courier New, Georgia, Trebuchet MS. **Never default to Aptos.** It is
the post-2023 Office default and an older Office install does not carry it.

| Element | Size |
| :--- | :--- |
| Slide title | 36-44pt bold |
| Section header | 20-24pt bold |
| Body text | 14-16pt |
| Caption | 10-12pt, muted |

**Spacing.** A 0.5 inch margin at least. A 0.3 to 0.5 inch gap between content
blocks. Pick one gap and keep it.

**Avoid these.** Each one marks a deck as machine-made:

- an accent line under a title
- a decorative color bar, a header or footer stripe, a sidebar stripe, or a
  single-side border on a card
- centred body text. Center a title only, and left-align a paragraph or a list.
- a cream or beige background by default. Use white or the brand palette.
- low contrast: a light icon on a light ground, or dark text on dark.
- one styled slide among plain ones. Commit fully, or keep it simple throughout.

## Verify

There is no renderer and no structural check, so two of the three usual passes
are gone. Do these instead:

1. **Read the deck back.** `markitdown output.pptx` shows the text of every
   slide. Check the order, the spelling and the missing content.
2. **Search for leftover placeholder text** when you worked from a template:
   `lorem`, `ipsum`, `TODO`, `[insert`, `xxx`, and "this slide layout".
3. **Ask the user to open it in PowerPoint.** This is the only real check.

**Text overflow is the defect you cannot see and the one that happens most.**
Two habits cover for it:

- leave 10 percent slack in every text box, and more on a font you did not
  measure
- keep a line under about 60 characters at 18pt on an 11.7 inch width

Never report a deck as visually checked. Say that PowerPoint has not opened it.

## What python-pptx cannot do

- reorder or delete a slide, which needs a direct edit of `p:sldIdLst`
- a comment
- SmartArt
- a slide master, or a new layout
