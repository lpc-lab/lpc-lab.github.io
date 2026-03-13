# lpc-lab.github.io

Website for the Language & Predictive Computation group at MPI Psycholinguistics.

## Setup

```bash
pip install pyyaml markdown
python build.py        # outputs to docs/
open docs/index.html   # preview locally
```

## Updating content

**Add a news item** — edit `data/news.md`, prepend a new entry:
```yaml
- date: "Apr 2026"
  tag: paper          # optional: paper | grant | hiring | talk
  text: "Title with optional [link](https://example.com)"
```

**Add a person** — create `data/people/yourname.md`:
```yaml
---
name: First Last
role: PhD Student
photo: yourname.jpg   # drop file in data/people/photos/
order: 2              # controls display order
links:
  website: https://...
  scholar: https://...
---
Bio text in markdown.
```

**Add a research thread** — create `data/research/04-new-thread.md`:
```yaml
---
number: "04"
title: Thread title
methods:
  - method one
  - method two
---
Description paragraph in markdown.
```

**Deploy** — push to `main`. GitHub Actions runs `build.py` and deploys `docs/` to GitHub Pages automatically.

## One-time GitHub setup

In the repo Settings → Pages, set source to **GitHub Actions**.
