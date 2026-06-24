# latris-site

Static marketing/landing site for **Latris** — served via GitHub Pages at
[latris.app](https://latris.app).

One file does the work: edit `index.html`, commit, push. No build step, no
framework, no dependencies. Inline CSS, Google Fonts, a single SVG favicon.

## Files

- `index.html` — the page.
- `favicon.svg` — the lattice mark (mirrors the desktop app icon).
- `CNAME` — custom domain (`latris.app`) for GitHub Pages.
- `robots.txt` — crawl policy.
- `404.html` — fallback, links back home.

## Deploy

GitHub Pages, deployed from `main` / root. The `CNAME` file sets the custom
domain on push. DNS: apex `A` records to GitHub Pages, `www` `CNAME` to
`shannon-bengtson.github.io`.

## Notes

- The **Download** button links to the public
  [`latris-releases`](https://github.com/Shannon-Bengtson/latris-releases/releases/latest)
  repo. It only resolves once that repo has a published release.
- Brand tokens (palette, fonts) mirror `theme.ts` in the main app.
- Screenshots for a future visual upgrade live in the app repo at
  `gui/ux-*.png`.
