---
name: figure-export
description: "Produces a reproducible result figure: explicit axes and units, readable size, saved numbers next to the image, deterministic output. Use when a result needs to leave the notebook as a file; not for choosing what to plot or for styling documents."
metadata:
  version: "0.1.0"
  scope: "example expert for ml-workflow-router"
---

# Figure export

## What this is for

Turn computed results into a file someone else can read, without turning a plot
into an unverifiable screenshot.

## Steps

1. **Fix the numbers first.** The values being plotted are written to a table or
   JSON next to the figure. If the numbers cannot be reproduced, the figure is
   decoration.
2. **Declare axes.** Label both axes with quantity and unit. State the sample size
   or the aggregation in the caption field of the figure metadata.
3. **Choose the encoding honestly.** Show distributions rather than single bars
   when spread matters; if uncertainty exists, show it; do not use a line for
   unordered categories.
4. **Size and output.** Readable font size, no clipped labels, headless rendering.
   Export a raster for quick viewing and a vector format when the figure will be
   printed or scaled.
5. **Determinism.** Fixed seed where sampling is involved, fixed colour mapping
   where categories matter, no timestamps in the filename.

## Output

- the figure file(s), one raster and optionally one vector
- the data behind the figure, in a plain format
- the command that regenerated both

## Checks before finishing

- Axis labels and units are present.
- The plotted values trace back to a saved table, not to a manual edit.
- No truncated axis that exaggerates differences without saying so.
- Text does not overlap or get cut off at the chosen output size.
- The figure regenerates from the saved data with the same command.

## What it does not do

Does not decide which comparison is meaningful, does not present statistical
significance, and does not imply causation. Association shown in a figure is not
evidence of a mechanism.
