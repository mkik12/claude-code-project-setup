---
name: xlsx
description: "Use this skill any time a spreadsheet file is the primary input or output. This means any task where the user wants to: open, read, edit, or fix an existing .xlsx, .xlsm, .xltx, .csv, or .tsv file (e.g., adding columns, computing formulas, formatting, charting, cleaning messy data); create a new spreadsheet from scratch or from other data sources; or convert between tabular file formats. Trigger especially when the user references a spreadsheet file by name or path - even casually (like \"the xlsx in my downloads\") - and wants something done to it or produced from it. Also trigger for cleaning or restructuring messy tabular data files (malformed rows, misplaced headers, junk data) into proper spreadsheets. The deliverable must be a spreadsheet file. Do NOT trigger when the primary deliverable is a Word document, HTML report, standalone Python script, database pipeline, or Google Sheets API integration, even if tabular data is involved."
---

# XLSX creation, editing, and analysis

| Task | Route |
| :--- | :--- |
| create or edit, with formulas and formatting | `openpyxl` |
| bulk data in or out | `pandas`, with `read_excel` and `to_excel` |
| a quick look at a sheet | `markitdown file.xlsx`, one section for each sheet |
| read a model, formulas **and** values | two `load_workbook` passes, see below |

`markitdown` gives you no cell coordinates, so do not plan an edit from it.

## No formula ever computes here

LibreOffice is absent from the target machine, and nothing else evaluates a
formula. openpyxl writes a formula as a string with **no cached value**. Until
Excel opens the file, that cell reads back as `None` to `pandas`, to
`load_workbook(data_only=True)`, and to every previewer.

**Choose by who reads the file next.**

- **A person, in Excel.** Write the formulas. Excel computes them on open. Tell
  the user that Excel computes the values, and that you did not.
- **Code, or a preview.** Compute the values in Python and write numbers. Add a
  formula only where the user asked for a live model.

You cannot check that a formula evaluates, so keep the formulas simple. Write
two or three first, check the ranges by hand, then build out the grid. Say that
they are unverified.

## Function names Excel refuses

Excel stores a post-2007 function name with an `_xlfn.` prefix, and its own
interface hides that. openpyxl writes your string into the XML exactly as you
gave it. So a bare `TEXTJOIN` becomes `#NAME?` when Excel opens the file.

- **An Excel-2007-era function needs no prefix**: `SUMIFS`, `INDEX`, `MATCH`,
  `IFERROR`, `SUMPRODUCT`. Prefer these.
- **Six functions need the prefix**: `_xlfn.TEXTJOIN`, `_xlfn.CONCAT`,
  `_xlfn.IFS`, `_xlfn.SWITCH`, `_xlfn.MAXIFS`, `_xlfn.MINIFS`.
- **A spilling function takes a different prefix again**, such as `XLOOKUP`,
  `SORT`, `FILTER`, `UNIQUE` and `SEQUENCE`. Confirm the exact prefixed name
  before you write one, or use `INDEX` and `MATCH` instead and sort, filter and
  de-duplicate in Python.

## openpyxl gotchas

- **A model takes two loads.** `data_only=True` gives the cached values with the
  formulas gone. The default gives the formula strings with no values. One pass
  cannot give you both.
- **`data_only=True` destroys the file if you save it.** That workbook holds no
  formula any more, so a save replaces every one with a literal, permanently.
- **`data_only=True` on a file you just wrote returns `None` everywhere**,
  because no cached value exists yet. A formula whose result is an empty string
  also reads back as `None`.
- **A merged range takes the top-left anchor only.** Every other cell is a
  `MergedCell` with a read-only `.value`.
- **`.xlsm` loses its macros** unless you pass `keep_vba=True` to
  `load_workbook`.
- **A sheet name with a space needs quotes** in a cross-sheet reference:
  `='Assumptions Inputs'!$B$5`. Without them the cell reads `#VALUE!`.
- **A link to another file dies on a re-save.** A formula such as
  `='[1]Returns Analysis'!$B$2` points at a separate file on disk, and the
  cached value is the only copy of that data here. openpyxl drops the cached
  value on save. Copy those values out of the original before you save over it.

## Requirements for every output

- **A professional font** throughout, such as Arial or Times New Roman, unless
  the user says otherwise.
- **Follow the user specification exactly.** The tab names, the column headers
  and the formula they spelled out. A redesign that computes something else
  fails, however elegant.
- **Document every assumption and every hardcoded number** where the reader sees
  it: a cell comment, or a cell beside the end of the table. Name a real source
  when one exists. When the number came from the user, say so.
- **A workbook you build for someone to fill in** needs a short legend that
  names the cells to edit, and one example row with realistic values. Never add
  such a row to a file you were asked to edit.
- **An existing file keeps its own conventions.** They beat every rule here.
  Find its input cells first, because a distinct font color or fill marks them.
  Write only there, and leave every existing formula alone.

## Financial models

Unless the user says otherwise, or the file already does something else.

**Color.** Blue text (`0,0,255`) for a hardcoded input or a scenario lever.
Black for a formula. Green (`0,128,0`) for a link to another sheet. Red
(`255,0,0`) for a link to another file. Yellow fill (`255,255,0`) for a key
assumption and for a cell the user must fill in.

**Numbers.** Currency `$#,##0`, with the unit in the header, such as
`Revenue ($mm)`. A zero renders as `-`, in a percentage too
(`$#,##0;($#,##0);-`). A negative goes in parentheses. A percentage is `0.0%`
and is **stored as a fraction**, so `0.15` renders `15.0%` and `15` renders
`1500.0%`. A multiple is `0.0x`. A year is text, so `"2024"` and never `2,024`.

**Structure.** Every assumption sits in its own labeled cell, and each formula
that uses it points at that cell: `=B5*(1+$B$6)`, never `=B5*1.05`. Keep the
formula the same across every projection period, because one edited cell in the
middle of a row is the commonest silent error. Guard a denominator that can
reach zero.

## Verify

Reopen the file and read back the sheet names, the headers, and a sample of the
cells. When you wrote numbers, check two of them against the source by hand.
When you wrote formulas, say that Excel has not computed them yet.
