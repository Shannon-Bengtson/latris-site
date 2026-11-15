#!/usr/bin/env python3
"""Stamp the shared head, header and footer into every page of latris.app.

The site is plain HTML served by GitHub Pages with no build step on deploy.
This script is run by hand after editing a partial below, and its output is
committed. Each page carries marker comments; everything between a pair of
markers is owned by this script and overwritten on every run:

    <!-- @head:start -->     ... <!-- @head:end -->      shared <head> lines
    <!-- @header:start -->   ... <!-- @header:end -->    skip link + site header
    <!-- @footer:start -->   ... <!-- @footer:end -->    site footer

It can also regenerate the Changelog page from the library's git history
(one section per "Bump version to X" commit; needs a full, unshallow clone):

    python3 tools/build.py --changelog ../latris

    <!-- @changelog:start --> ... <!-- @changelog:end -->

and the Methods page body from the library's methods reference (needs
`pip install markdown`; em dashes are rewritten, see EM_DASH_RULES).
`--llms ../latris/llms.txt` rewrites the site's llms.txt from the repo's.

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


# The site's copy uses no em dashes. FOUNDATIONS.md does, so they are rewritten
# on the way in: specific patterns first (pairs become parentheses or a colon,
# clause joins a semicolon), then any other em dash becomes a comma. Read the
# generated page after FOUNDATIONS.md changes; add a rule here if one reads badly.
_W = r"\s+"  # the source wraps lines anywhere
EM_DASH_RULES = [
    # Paired asides
    (r"The guide by question\s+—\s+([\s\S]*?\(SD\))\s+—\s+lives at", r"The guide by question, \1, lives at"),
    (r"Matter method\s+—\s+(Schoenberg, Davidsen[\s\S]*?Review\*)\s+—\s+with", r"Matter method (\1), with"),
    (r"vocabulary\s+—\s+(claims, warrants, rebuttals)\s+—\s+is", r"vocabulary (\1) is"),
    (r"test\s+—\s+(`latris capabilities`, `excluded_by_design`)\)", r"test: \1)"),
    # Headings, bold labels and table cells take a colon
    (r"^(#+ [^\n]*?)\s+—\s+", r"\1: "),
    (r"\*\*Limits\s+—\s+", "**Limits: "),
    (r"(\| [^|\n]*?)\s+—\s+", r"\1: "),
    (r"graph surgery\s+—\s+", "graph surgery: "),
    # Two clauses joined: a semicolon
    (r"\s+—\s+(?=it" + _W + r"implements|they" + _W + r"are|weights" + _W + r"need|no" + _W + r"junction"
     r"|see" + _W + r"`latris|the" + _W + r"method" + _W + r"explains|a" + _W + r"paraphrase|a" + _W + r"check)",
     "; "),
]


def strip_em_dashes(md: str) -> str:
    for pat, rep in EM_DASH_RULES:
        md = re.sub(pat, rep, md, flags=re.M)
    md = re.sub(r"\n(\s*)—\s+", r",\n\1", md)    # a dash that starts a wrapped line
    md = re.sub(r"\s+—\s+", ", ", md)            # anything else
    return md.replace("—", ", ")


def foundations_html(md_path: Path) -> str:
    try:
        import markdown  # type: ignore
    except ImportError:
        raise SystemExit("--foundations needs the markdown package: pip install markdown")
    src = md_path.read_text(encoding="utf-8")
    src = re.sub(r"\A# .*\n", "", src)  # the page supplies its own <h1>
    src = strip_em_dashes(src)
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


# ── Changelog page from the library's git history ────────────────────────

# Commit kinds that say nothing to a reader of the site.
_SKIP = re.compile(r"^(style|ci|test|tests|chore|build)(\(|:|!)|^Bump version|\btest:", re.I)
_PREFIX = re.compile(r"^[a-z]+(\(([^)]+)\))?!?:\s*")
_MONTHS = ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"]


def _human_date(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{int(d)} {_MONTHS[int(m) - 1]} {y}"


def _commit_html(subject: str) -> str:
    import html as _html
    m = _PREFIX.match(subject)
    if m:
        scope = m.group(2)
        subject = subject[m.end():]
        if scope:
            subject = f"{scope.capitalize()}: {subject}"
    if not subject.startswith("latris "):  # keep command names as typed
        subject = subject[:1].upper() + subject[1:]
    subject = re.sub(r"\s+—\s+", ", ", subject).replace("—", ", ")
    text = _html.escape(subject, quote=False)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", text)


def changelog_html(repo: Path) -> str:
    import subprocess
    ref = "origin/main"
    if subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "-q", ref],
                      capture_output=True).returncode != 0:
        ref = "HEAD"
    shallow = subprocess.run(["git", "-C", str(repo), "rev-parse", "--is-shallow-repository"],
                             capture_output=True, text=True).stdout.strip()
    if shallow == "true":
        raise SystemExit(f"{repo} is a shallow clone; run `git -C {repo} fetch --unshallow origin main` first")
    log = subprocess.run(
        ["git", "-C", str(repo), "log", ref, "--reverse", "--date=short", "--format=%H%x1f%ad%x1f%s"],
        capture_output=True, text=True, check=True).stdout

    releases: list[tuple[str, str, str, list[str]]] = []  # (version, date, sha, subjects)
    pending: list[str] = []
    for line in log.splitlines():
        sha, date, subject = line.split("\x1f", 2)
        bump = re.match(r"Bump version to (\S+)", subject)
        first = re.match(r"Initial commit\b.*?(\d+\.\d+\.\d+)", subject)
        if bump or first:
            if first:
                pending.append("First open-source release")
            releases.append(((bump or first).group(1), date, sha, pending))
            pending = []
        elif not _SKIP.search(subject):
            pending.append(subject)

    out = ["\n<!-- Generated from the latris repo's git history by tools/build.py --changelog. Don't edit by hand. -->"]
    if pending:
        out.append('<h2 id="unreleased">Unreleased</h2>\n<ul>')
        out += [f"  <li>{_commit_html(s)}</li>" for s in reversed(pending)]
        out.append("</ul>")
    for version, date, sha, subjects in reversed(releases):
        out.append(f'<h2 id="v{version}"><a href="https://github.com/Shannon-Bengtson/latris/commit/{sha}">{version}</a> '
                   f'<span class="status-pill">{_human_date(date)}</span></h2>')
        if subjects:
            out.append("<ul>")
            out += [f"  <li>{_commit_html(s)}</li>" for s in reversed(subjects)]
            out.append("</ul>")
        else:
            out.append("<p>Fixes and maintenance.</p>")
    return "\n".join(out) + "\n"


# ── llms.txt from the library's copy ────────────────────────────────────

WEBSITE_SECTION = """## Website (for the person you're helping)

- [How it works](https://latris.app/how-it-works/): the workflow, evidence on each claim, AI-proposed labelling, challenges, outputs.
- [Which model?](https://latris.app/formalisms/): the five model types by the question each answers; what's available and what's on the roadmap.
- [Use with AI](https://latris.app/ai/): the connector for Claude and ChatGPT, and agents driving the CLI.
- [For reviewers](https://latris.app/for-reviewers/): what a decision owner or reviewer can check; review packs.
- [Example](https://latris.app/examples/): the river-health model and its live report.
- [Methods](https://latris.app/methods/): methods and foundations, mirrored from docs/FOUNDATIONS.md.
- [Changelog](https://latris.app/changelog/): every release, from the git history.

"""


def llms_txt(repo_llms: Path) -> str:
    """The repo's llms.txt with absolute links, pointing humans at the site,
    plus the website pages. Everything else is maintained in the latris repo."""
    s = repo_llms.read_text(encoding="utf-8")
    s = re.sub(r"\]\((?!https?:|#)([^)]+)\)", lambda m: f"]({GITHUB_DOCS[:-5]}{m.group(1)})", s)
    s = s.replace("humans start at README.md.", "humans start at https://latris.app.", 1)
    if "## Engineering docs" not in s:
        raise SystemExit(f"{repo_llms}: no '## Engineering docs' heading to put the website section before")
    return s.replace("## Engineering docs", WEBSITE_SECTION + "## Engineering docs", 1)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 if any page would change")
    ap.add_argument("--foundations", type=Path, help="path to latris/docs/FOUNDATIONS.md")
    ap.add_argument("--changelog", type=Path, help="path to a full (unshallow) clone of the latris repo")
    ap.add_argument("--llms", type=Path, help="path to latris/llms.txt; writes the site's llms.txt from it")
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
        if url == "/changelog/" and args.changelog:
            new = replace_block(new, "changelog", changelog_html(args.changelog), rel)
        bad = [h for h in re.findall(r'href="([^"]*)"', new) if not re.match(r"(https?:|mailto:|/|#)", h)]
        if bad:
            raise SystemExit(f"{rel}: links that aren't a URL, a /path or an #anchor: {bad}")
        if new != text:
            stale.append(rel)
            if not args.check:
                path.write_text(new, encoding="utf-8")

    if args.llms:
        target = SITE / "llms.txt"
        new = llms_txt(args.llms)
        if target.read_text(encoding="utf-8") != new:
            stale.append("llms.txt")
            if not args.check:
                target.write_text(new, encoding="utf-8")

    verb = "out of date" if args.check else "updated"
    print(f"{len(stale)} page(s) {verb}" + (": " + ", ".join(stale) if stale else ""))
    return 1 if (args.check and stale) else 0


if __name__ == "__main__":
    sys.exit(main())
