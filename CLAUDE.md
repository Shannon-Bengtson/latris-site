# CLAUDE.md

Notes for AI coding agents working in this repository. Start at
[README.md](./README.md): what each page is for and how the generated ones
are built.

## How this repo connects to the others

The site is one of four repos (sibling checkouts sit next to each other, e.g.
`../latris`):

- **latris** (public library, github.com/Shannon-Bengtson/latris): the source
  of every generated page here: `/changelog/`, `/methods/reference/`, the
  generated model-type pages and list, and `llms.txt`. After a latris release,
  rerun the `tools/build.py` commands in the README and open a PR.
- **latris-examples** (public): its CI rebuilds the example models and pushes
  them into `examples/gallery/`. Don't edit that folder by hand; change the
  model there.
- **latris-app** (private): the app at app.latris.app. Its `latris_present`
  builds `examples/explorer/beach.html` (`tools/explorer-example/build.py`).
  Its source isn't available from a clone of this repo alone.

## Open work lives in GitHub issues

To-dos and bugs for this repo are its GitHub issues (public: engineering and
content only, see below). Don't keep to-do lists in Markdown here.

## Publishing is the founder's call

Every push or merge to `main` publishes straight to latris.app (GitHub Pages,
no build step, no review). Work on a branch and open a pull request; don't
push or merge to `main` until the founder says to.

## This repo is public

Everything here is public: on GitHub, and every page on latris.app (`_config.yml` keeps this file, README.md and `tools/` off the site, but not off GitHub). Never add business or sensitive information: go-to-market or growth
strategy, pricing, revenue, customers, sales conversations or trial
participants, competitive positioning, the founder's personal or admin
details, internal infrastructure (server addresses, how deploys reach them,
where secrets are kept), secrets or tokens, or the private app's code and
internal plans.
Those live in the private app repo. If a change seems to need them, write only
the engineering or user-facing part, or ask the founder. Commit messages and
pull-request text are public too.
