#!/usr/bin/env python3
"""Stamp the shared head, header and footer into every page of latris.app.

The site is plain HTML served by GitHub Pages with no build step on deploy.
This script is run by hand after editing a partial below, and its output is
committed. Each page carries marker comments; everything between a pair of
markers is owned by this script and overwritten on every run:

    <!-- @head:start -->     ... <!-- @head:end -->      shared <head> lines
    <!-- @header:start -->   ... <!-- @header:end -->    skip link + site header
    <!-- @footer:start -->   ... <!-- @footer:end -->    site footer

Optionally it also regenerates the Methods page body from the library's
methods reference (needs `pip install markdown`):

    python3 tools/build.py --foundations ../latris/docs/FOUNDATIONS.md

    <!-- @foundations:start --> ... <!-- @foundations:end -->

`--check` exits 1 if any page is out of date (useful in CI).
Standard library only, except `markdown` for --foundations.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent

# Pages that get the shared chrome, by URL path -> file.
PAGES = {
    "/": "index.html",
    "/how-it-works/": "how-it-works/index.html",
    "/formalisms/": "formalisms/index.html",
    "/ai/": "ai/index.html",
    "/examples/": "examples/index.html",
    "/for-reviewers/": "for-reviewers/index.html",
    "/open-source/": "open-source/index.html",
    "/methods/": "methods/index.html",
    "/about/": "about/index.html",
    "/changelog/": "changelog/index.html",
    "/support/": "support/index.html",
    "/privacy/": "privacy/index.html",
    "/terms/": "terms/index.html",
    "/404": "404.html",
}

# Main navigation: (label, href). "Open Latris" is added as the button.
NAV = [
    ("How it works", "/how-it-works/"),
    ("Models", "/formalisms/"),
    ("Use with AI", "/ai/"),
    ("Examples", "/examples/"),
    ("Open source", "/open-source/"),
    ("About", "/about/"),
]

FOOTER_COLS = [
    ("Product", [
        ("How it works", "/how-it-works/"),
        ("Which model?", "/formalisms/"),
        ("Examples", "/examples/"),
        ("For reviewers", "/for-reviewers/"),
        ("Use with AI", "/ai/"),
        ("Open Latris", "https://app.latris.app/"),
    ]),
    ("Open source", [
        ("Library and CLI", "/open-source/"),
        ("Methods", "/methods/"),
        ("Changelog", "/changelog/"),
        ("GitHub", "https://github.com/Shannon-Bengtson/latris"),
        ("PyPI", "https://pypi.org/project/latris/"),
        ("llms.txt", "/llms.txt"),
    ]),
    ("Latris", [
        ("About", "/about/"),
        ("Contact", "/about/#contact"),
        ("Support", "/support/"),
        ("Privacy", "/privacy/"),
        ("Terms", "/terms/"),
    ]),
]


def asset_version(rel: str) -> str:
    return hashlib.sha256((SITE / rel).read_bytes()).hexdigest()[:10]


def head_html() -> str:
    css_v = asset_version("assets/site.css")
    js_v = asset_version("assets/site.js")
    return f"""
  <script>document.documentElement.classList.add('js')</script>
  <!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "f91a76ef1e8144e9bbbbe3bd2412cd1a"}}'></script><!-- End Cloudflare Web Analytics -->
  <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
  <link rel="alternate icon" href="/favicon.png" />
  <meta name="theme-color" content="#f4f1eb" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/assets/site.css?v={css_v}" />
  <script src="/assets/site.js?v={js_v}" defer></script>
  """


def _link(label: str, href: str, current: str) -> str:
    here = ' aria-current="page"' if href == current else ""
    return f'<a href="{href}"{here}>{label}</a>'


def header_html(current: str) -> str:
    links = "\n        ".join(_link(l, h, current) for l, h in NAV)
    return f"""
  <a class="skip" href="#main">Skip to content</a>
  <header class="site">
    <div class="wrap header-inner">
      <a class="brand" href="/" aria-label="Latris home">
        <img src="/latris-wordmark.svg" alt="Latris" width="85" height="26" />
      </a>
      <button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
        Menu
      </button>
      <nav class="nav" id="site-nav" aria-label="Main">
        {links}
        <a class="btn-nav" href="https://app.latris.app/">Open Latris</a>
      </nav>
    </div>
  </header>
  """


def footer_html(current: str) -> str:
    cols = []
    for title, links in FOOTER_COLS:
        items = "\n            ".join(f"<li>{_link(l, h, current)}</li>" for l, h in links)
        cols.append(f"""
        <div>
          <h2>{title}</h2>
          <ul>
            {items}
          </ul>
        </div>""")
    return f"""
  <footer class="site">
    <div class="wrap foot-grid">
      <div class="foot-brand">
        <img src="/latris-wordmark.svg" alt="Latris" width="72" height="22" />
        <p>Causal models that show their evidence.</p>
        <p>© 2026 Latris · Made in Australia</p>
      </div>{"".join(cols)}
    </div>
  </footer>
  """


def replace_block(text: str, name: str, body: str, path: str) -> str:
    pat = re.compile(rf"(<!-- @{name}:start -->)(.*?)(<!-- @{name}:end -->)", re.S)
    if not pat.search(text):
        raise SystemExit(f"{path}: missing <!-- @{name}:start/end --> markers")
    return pat.sub(lambda m: m.group(1) + body + m.group(3), text, count=1)


# ── Methods page from FOUNDATIONS.md ─────────────────────────────────────

GITHUB_DOCS = "https://github.com/Shannon-Bengtson/latris/blob/main/docs/"


def foundations_html(md_path: Path) -> str:
    try:
        import markdown  # type: ignore
    except ImportError:
        raise SystemExit("--foundations needs the markdown package: pip install markdown")
    src = md_path.read_text(encoding="utf-8")
    src = re.sub(r"\A# .*\n", "", src)  # the page supplies its own <h1>
    html = markdown.markdown(src, extensions=["tables", "sane_lists"])

    def fix(m: re.Match) -> str:
        href = m.group(1)
        if href.startswith("https://latris.app/"):
            href = href[len("https://latris.app"):]
        elif href == "../llms.txt":
            href = "/llms.txt"
        elif not re.match(r"^(https?:|mailto:|#|/)", href):
            href = GITHUB_DOCS + href
        return f'href="{href}"'

    html = re.sub(r'href="([^"]+)"', fix, html)
    html = html.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    return f"\n<!-- Generated from docs/FOUNDATIONS.md in the latris repo by tools/build.py. Don't edit by hand. -->\n{html}\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 if any page would change")
    ap.add_argument("--foundations", type=Path, help="path to latris/docs/FOUNDATIONS.md")
    args = ap.parse_args()

    stale = []
    for url, rel in PAGES.items():
        path = SITE / rel
        text = path.read_text(encoding="utf-8")
        new = replace_block(text, "head", head_html(), rel)
        new = replace_block(new, "header", header_html(url), rel)
        new = replace_block(new, "footer", footer_html(url), rel)
        if url == "/methods/" and args.foundations:
            new = replace_block(new, "foundations", foundations_html(args.foundations), rel)
        if new != text:
            stale.append(rel)
            if not args.check:
                path.write_text(new, encoding="utf-8")

    verb = "out of date" if args.check else "updated"
    print(f"{len(stale)} page(s) {verb}" + (": " + ", ".join(stale) if stale else ""))
    return 1 if (args.check and stale) else 0


if __name__ == "__main__":
    sys.exit(main())
