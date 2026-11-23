"""Rebuild the website's live explorer example (/examples/explorer/beach.html) from beach.yaml.

Needs the Latris app's presentation package installed alongside latris (the explorer page is part
of the app, not the open library):

    python tools/explorer-example/build.py

Rerun after a release that changes the explorer, so the example matches what readers get.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent / "examples" / "explorer" / "beach.html"

os.environ.setdefault("LATRIS_AI_MOCK", "1")
for key in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
    os.environ[key] = "Latris example"
for key in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
    os.environ[key] = "example@latris.app"

from latris.operations.build import build_from_spec, load_spec  # noqa: E402
from latris.operations.init import init_project  # noqa: E402
from latris.repo.layout import ProjectPaths  # noqa: E402

try:
    from latris_present.explorer import operations as ops
    from latris_present.exporters import explorer_html
except ImportError:
    sys.exit("needs the Latris app's latris_present package installed (pip install -e ../latris-app)")

INTRO = ("An illustrative model with made-up numbers, to show what a reader can do. "
         "Click a state to say you've seen it (a severe storm, a bloom), and watch the chance of a closed beach move.")


def for_the_site(page: str) -> str:
    """The app's page, fitted to the site: kept out of search results (it's a demo with made-up
    numbers, reached from How it works), and with the site's no-em-dash rule applied (the app's
    template has them in its script comments)."""
    viewport = '<meta name="viewport" content="width=device-width, initial-scale=1">'
    if viewport not in page:
        sys.exit("the explorer page's <head> has changed: no viewport line to put the robots meta after")
    page = page.replace(viewport, viewport + '\n<meta name="robots" content="noindex">', 1)
    return re.sub(r"\s*(—|&mdash;)\s*", ", ", page)


work = Path(tempfile.mkdtemp())
try:
    root = work / "beach"
    init_project(root, statement="How likely is the beach to close after a storm?", name="Beach closures")
    os.chdir(root)
    build_from_spec(load_spec((HERE / "beach.yaml").read_text(encoding="utf-8")), root=root)
    doc, _ = ops.create_explorer(name="Website example", model_type="bn", root=root)
    ops.update_explorer(doc.id, title="Will the beach close?", intro=INTRO, root=root)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(for_the_site(explorer_html.render(ProjectPaths(root), doc.id)), encoding="utf-8")
    print(OUT)
finally:
    os.chdir(HERE)
    shutil.rmtree(work, ignore_errors=True)
