# latris-site

The marketing and documentation site for **Latris**, served by GitHub Pages
at [latris.app](https://latris.app).

Plain HTML, one shared stylesheet and one small script. No framework and no
build step on deploy: what's committed is what's served.

## Pages

| Path | What it's for |
|---|---|
| `/` | Short landing page: hero, the live river example, three pillars, who it's for, key facts |
| `/how-it-works/` | The workflow, evidence on each claim, AI labelling, challenges, handover check, outputs, history |
| `/formalisms/` | "Which model?": the five model types, what's available, what's on the roadmap. Keep this URL: the library's README and `llms.txt` link to it |
| `/ai/` | The connector for Claude and ChatGPT; agents driving the CLI; what data Latris receives |
| `/examples/` | The river-health model, what to click, the fields Latris fits |
| `/for-reviewers/` | For decision owners and reviewers: what they can check; review packs |
| `/open-source/` | The open engine: library vs app, design, agents, quickstart |
| `/methods/` | Methods and foundations, generated from `docs/FOUNDATIONS.md` in the latris repo |
| `/about/` | Founder, "Work with me", contact, release-notes sign-up |
| `/changelog/` | Releases of the open-source engine |
| `/support/`, `/privacy/`, `/terms/` | Help and legal |
| `404.html` | Not found |

Old single-page anchors (`/#builders`, `/#about`, …) are redirected to their
new pages by `assets/site.js`. `/#example` still exists on the home page.

## Shared parts

- `assets/site.css`: every style. Brand tokens mirror `theme.ts` in the app.
- `assets/site.js`: sticky header, mobile menu, scroll reveal, copy buttons,
  the release-notes form (Formspree), and the legacy-anchor redirects. Pages
  work without it.
- The `<head>` boilerplate, site header and footer are stamped into every page
  by `tools/build.py`, between marker comments:

  ```html
  <!-- @head:start --> … <!-- @head:end -->
  <!-- @header:start --> … <!-- @header:end -->
  <!-- @footer:start --> … <!-- @footer:end -->
  ```

  Don't edit inside the markers by hand. To change the nav, footer or shared
  head, edit `tools/build.py` and run it. Also run it after changing
  `site.css` or `site.js`, so the cache-busting `?v=` hashes update.

```bash
python3 tools/build.py            # restamp every page
python3 tools/build.py --check    # exit 1 if any page is out of date

# Also regenerate /methods/ from the library repo (needs: pip install markdown)
python3 tools/build.py --foundations ../latris/docs/FOUNDATIONS.md
```

A new page needs an entry in `PAGES` in `tools/build.py`, the three marker
pairs, a `<link rel="canonical">`, and a line in `sitemap.xml`.

## Other files

- `llms.txt`: the documentation map for AI agents. It's the latris repo's
  `llms.txt` with absolute links, plus the install line, the connector
  pointer, the website pages and the "Choosing a model type" guide. Keep the
  two in step.
- `assets/og-image.png`: 1200×630 link-preview image.
- `assets/report-*.{webp,png}`: crops of the river-health report.
- `CNAME`, `robots.txt`, `sitemap.xml`, `favicon.svg`, `favicon.png`,
  `latris-wordmark.svg`.

## Deploy

GitHub Pages, deployed from `main` / root. The `CNAME` file sets the custom
domain on push. DNS: apex `A` records to GitHub Pages, `www` `CNAME` to
`shannon-bengtson.github.io`.

## Style

No em dashes in site copy. `/methods/` is the exception: it mirrors
`FOUNDATIONS.md` verbatim.
