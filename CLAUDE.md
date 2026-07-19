# CLAUDE.md — LPC Lab Website

## Project Overview
Static site for the Language & Predictive Computation group (MPI Psycholinguistics).
Hosted on GitHub Pages at lpc-lab.github.io.

## Architecture
- Content lives in `data/` as markdown files with YAML frontmatter
- `build.py` reads data files and produces final HTML in `docs/`
- GitHub Action runs build.py on every push to main
- Fonts: JetBrains Mono (headings/code/labels) + DM Sans (body text)
- Accent color: #a0cfb0 (muted terminal green)

## Content structure
- `data/news.md` — news items as markdown with dates
- `data/people/*.md` — one file per person, YAML frontmatter + markdown bio
- `data/people/photos/` — headshot images
- `data/research/*.md` — one file per research thread, numbered

## How to update
- Add news: edit `data/news.md`, add entry at top
- Add person: create new `.md` in `data/people/`, add photo to `photos/`
- Add research thread: create new `.md` in `data/research/`
- Test locally: `python build.py` then open `docs/index.html`
- Deploy: push to main, GitHub Action builds automatically

## Design principles
- Dark terminal aesthetic with autocomplete/prediction metaphor
- Hero has a typing animation: "Language & Predic" types out, then
  "tive Computation" fades in as ghost autocomplete text
- Page titles use same motif: first letter white, rest in ghost text
- Three pages: About (landing + news), People, Research
- Minimalistic, high-taste CS lab — NOT a stuffy academic website
- Think design studio but restrained. Lots of whitespace, asymmetry
- No default template look, no generic AI aesthetics
- No Tailwind — hand-written CSS with CSS variables for theming

## Design guardrails
- Never use generic fonts (Inter, Roboto, Arial)
- Never use default blue/purple gradients
- Keep accent color usage restrained — links and the hiring dot
- Typography: tight tracking on large mono headings, generous line-height on body
- Interactive states on all clickable elements (hover, focus)
- Animations: only transform and opacity, subtle easing
- One CSS file, one template, no framework dependencies

## Always do first
- Read this file
- Check `data/` for current content before making changes
- Run `python build.py` after any template/style changes to verify
