#!/usr/bin/env python3
"""
build.py — LPC Lab static site generator

Reads markdown/YAML data files, injects them into templates/index.html,
and writes the final site to docs/.

Usage:
    python build.py

Dependencies:
    pip install pyyaml markdown
"""

import hashlib
import os
import re
import shutil
import yaml
import markdown as md_lib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
DOCS_DIR = os.path.join(BASE_DIR, "docs")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(text):
    """Split a file into (frontmatter_dict, body_string)."""
    text = text.strip()
    if not text.startswith("---"):
        return {}, text
    # Find the closing --- on its own line (avoids matching --- inside YAML values)
    match = re.search(r'\n---[ \t]*(\n|$)', text[3:])
    if not match:
        return {}, text
    fm_text = text[3: match.start() + 3].strip()
    body = text[match.end() + 3:].strip()
    data = yaml.safe_load(fm_text) or {}
    return data, body


def md_to_html(text):
    """Convert markdown body to HTML (paragraphs, links, emphasis)."""
    return md_lib.markdown(text)


def inline_md(text):
    """Convert markdown links and em-dashes in a single line of text to HTML.

    Used for news item text where we want inline rendering without wrapping <p>.
    """
    # em-dash shorthand
    text = text.replace(" --- ", " \u2014 ")
    # [label](url) -> <a href="url">label</a>
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text


def html_escape(text):
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def load_config():
    path = os.path.join(DATA_DIR, "config.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_hiring_banner(config):
    hiring = config.get("hiring", {})
    if not hiring.get("show", False):
        return ""
    text_html = inline_md(hiring.get("text", ""))
    return f"""  <div class="hiring-banner fade-in">
    <div class="dot"></div>
    <p>{text_html}</p>
  </div>\n"""


def build_join_box(config):
    jb = config.get("join_box", {})
    if not jb.get("show", False):
        return ""
    heading = jb.get("heading", "")
    text_html = inline_md(jb.get("text", ""))
    return f"""  <section class="join-section">
    <div class="join-box fade-in">
      <h3>{heading}</h3>
      <p>{text_html}</p>
    </div>
  </section>\n"""


def build_news_items():
    path = os.path.join(DATA_DIR, "news.md")
    with open(path, encoding="utf-8") as f:
        content = f.read()
    data, _ = parse_frontmatter(content)
    items = data.get("items", [])

    html = ""
    for item in items:
        date = item.get("date", "")
        tag = item.get("tag", "")
        text = item.get("text", "")

        # Tag is its own grid column; always emit the cell (even empty)
        # so item text stays aligned across tagged and untagged rows.
        tag_html = f'<div class="news-tag">{html_escape(tag)}</div>'

        text_html = inline_md(text)

        html += f"""    <div class="news-item fade-in">
      <div class="news-date">{html_escape(date)}</div>
      {tag_html}
      <div class="news-content">{text_html}</div>
    </div>\n"""

    return html


def build_people_cards():
    people_dir = os.path.join(DATA_DIR, "people")
    photos_dir = os.path.join(people_dir, "photos")

    # Collect all .md files (excluding README etc.)
    files = sorted(
        f for f in os.listdir(people_dir)
        if f.endswith(".md")
    )

    people = []
    for fname in files:
        path = os.path.join(people_dir, fname)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        fm, body = parse_frontmatter(content)
        fm["_body"] = body
        people.append(fm)

    # Sort by order field, default 999
    people.sort(key=lambda p: p.get("order", 999))

    # Split into core members and affiliated members
    core = [p for p in people if p.get("category", "") != "affiliated"]
    affiliated = [p for p in people if p.get("category", "") == "affiliated"]

    def render_card(person):
        name = person.get("name", "")
        role = person.get("role", "")
        photo = person.get("photo", "")
        bio_md = person.get("_body", "")
        links = person.get("links", {})

        photo_path = os.path.join(photos_dir, photo) if photo else ""
        if photo and os.path.exists(photo_path):
            photo_html = f'<img class="person-photo" src="photos/{html_escape(photo)}" alt="{html_escape(name)}">'
        else:
            photo_html = '<div class="person-photo-placeholder"></div>'

        bio_html = md_to_html(bio_md).strip()
        if bio_html.startswith("<p>") and bio_html.endswith("</p>") and bio_html.count("<p>") == 1:
            bio_html = bio_html[3:-4]

        links_html = ""
        if links:
            links_html = '<div class="person-links">'
            for label, url in links.items():
                links_html += f'<a href="{html_escape(url)}">{html_escape(label)}</a>'
            links_html += "</div>"

        return f"""    <div class="person-card fade-in">
      {photo_html}
      <div class="person-info">
        <h3>{html_escape(name)}</h3>
        <div class="person-role">{html_escape(role)}</div>
        <p class="person-bio">{bio_html}</p>
        {links_html}
      </div>
    </div>\n"""

    html = ""
    if affiliated:
        html += '    <div class="section-label">Members</div>\n'
    for person in core:
        html += render_card(person)
    if affiliated:
        html += '    <div class="section-label people-section-label--affiliated">Affiliated members</div>\n'
        for person in affiliated:
            html += render_card(person)

    return html


def build_research_intro():
    path = os.path.join(DATA_DIR, "research", "intro.md")
    with open(path, encoding="utf-8") as f:
        body = f.read().strip()
    return f'''  <section class="research-intro fade-in">
    <p>{body}</p>
  </section>\n'''


def build_research_threads():
    research_dir = os.path.join(DATA_DIR, "research")

    files = sorted(
        f for f in os.listdir(research_dir)
        if f.endswith(".md") and f != "intro.md"
    )

    html = ""
    for fname in files:
        path = os.path.join(research_dir, fname)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        fm, body = parse_frontmatter(content)

        number = fm.get("number", "")
        title = fm.get("title", "")

        # Body as plain paragraph text
        body_html = md_to_html(body).strip()
        if body_html.startswith("<p>") and body_html.endswith("</p>") and body_html.count("<p>") == 1:
            body_html = body_html[3:-4]

        html += f"""    <div class="thread fade-in">
      <div class="thread-number">{html_escape(number)}</div>
      <h3>{html_escape(title)}</h3>
      <p>{body_html}</p>
    </div>\n"""

    return html


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------

def build():
    os.makedirs(DOCS_DIR, exist_ok=True)

    # Read template
    template_path = os.path.join(TEMPLATES_DIR, "index.html")
    with open(template_path, encoding="utf-8") as f:
        html = f.read()

    # Version the stylesheet URL with a content hash: GitHub Pages caches
    # assets for 10 minutes, so an unversioned style.css can pair fresh
    # HTML with a stale cached sheet after a deploy.
    with open(os.path.join(BASE_DIR, "style.css"), "rb") as f:
        css_ver = hashlib.md5(f.read()).hexdigest()[:8]
    html = html.replace('href="style.css"', f'href="style.css?v={css_ver}"')

    # Inject sections
    config = load_config()
    html = html.replace("<!-- HIRING_BANNER -->", build_hiring_banner(config))
    html = html.replace("<!-- JOIN_BOX -->", build_join_box(config))
    html = html.replace("<!-- NEWS_ITEMS -->", build_news_items())
    html = html.replace("<!-- PEOPLE_CARDS -->", build_people_cards())
    html = html.replace("<!-- RESEARCH_INTRO -->", build_research_intro())
    html = html.replace("<!-- RESEARCH_THREADS -->", build_research_threads())

    # Write output
    out_path = os.path.join(DOCS_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  wrote {out_path}")

    # Copy CSS
    src_css = os.path.join(BASE_DIR, "style.css")
    dst_css = os.path.join(DOCS_DIR, "style.css")
    shutil.copy2(src_css, dst_css)
    print(f"  copied style.css -> docs/style.css")

    # Copy favicon
    src_fav = os.path.join(BASE_DIR, "favicon.svg")
    shutil.copy2(src_fav, os.path.join(DOCS_DIR, "favicon.svg"))
    print(f"  copied favicon.svg -> docs/favicon.svg")

    # Copy photos if they exist
    src_photos = os.path.join(DATA_DIR, "people", "photos")
    dst_photos = os.path.join(DOCS_DIR, "photos")
    if os.path.isdir(src_photos):
        if os.path.exists(dst_photos):
            shutil.rmtree(dst_photos)
        shutil.copytree(src_photos, dst_photos)
        print(f"  copied photos -> docs/photos/")

    print("Build complete.")


if __name__ == "__main__":
    build()
