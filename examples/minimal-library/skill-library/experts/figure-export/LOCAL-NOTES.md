# Local notes — figure-export

- Example expert. Use whatever plotting library the project already has; do not
  install a stack for this file.
- Headless rendering only. Never open an interactive window from an automated run.
- Write outputs to a project directory; never overwrite an existing figure that a
  document already references.
- Keep the numbers file and the image side by side, with the same base name.
- If a colour map encodes categories, use one that stays distinguishable in
  greyscale; do not rely on colour alone to carry meaning.
