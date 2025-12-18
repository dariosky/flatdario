# flatdario
Personal “flat site” generator that collects activity I like across the web, saves
it locally, and serves it via a small API + React UI (or a legacy static build).

## High level
- Collectors in `collectors/` pull data from YouTube (likes + uploads), Pocket,
  Vimeo and a few RSS feeds. Credentials live in `appkeys/` (app) and
  `userkeys/` (per-user tokens).
- Data is stored in SQLite by default (`flat.json` config), but the storage layer
  also supports TinyDB/JSON.
- The `flat.py` CLI orchestrates collection, static builds (via
  `flatbuilder/`), push notifications, and running the Flask/GraphQL API.
- The API in `api/` serves a GraphQL endpoint plus push-subscribe routes and
  ships the React bundle in `api/ui/build`. The UI uses Apollo to talk to the
  API and offers search and infinite scrolling over the feed.

## Repository map
- `flat.py` – main entry point with CLI actions.
- `collectors/` – individual sources (YouTube, Pocket, Vimeo, RSS, OpenGraph
  enrichments).
- `storage/` – SQLite (`db.sqlite`) and TinyDB storage backends.
- `flatbuilder/` – legacy static-site builder and template copier.
- `api/` – Flask app (`api_server.py`, `schema.py`), GraphQL schema and push
  helpers.
- `api/ui/` – React app served by the API in production; uses `react-app-rewired`.
- `push/` – web push helpers.
- `build/` – generated static site (when using the builder).

## Setup
```bash
# Python deps (recommend a virtualenv)
pip install -r requirements.txt

# Frontend deps
cd api/ui
yarn install   # or npm install
```
Secrets:
- Drop app credentials in `appkeys/<service>.json` (e.g. `google.json`,
  `pocket.json`, `vimeo.json`).
- User tokens are written/read from `userkeys/<service>.json` on first auth.

Configuration:
- `flat.json` controls DB path/format and builder template. Defaults to SQLite
  at `db.sqlite` and the `empty` template.

## CLI usage (python flat.py …)
- `collect` – run all collectors and persist results.
- `build` – render the legacy static site into `build/` using `flatbuilder`.
- `collect+build` (default) – do both steps.
- `init --template empty` – copy a template from `flatbuilder/<name>` into
  `build/`.
- `preview` – serve the built static site locally.
- `runapi` – launch the Flask + GraphQL server (serves `api/ui/build` too).
- `notify` – send pending push notifications to subscribers.

Flags:
- `--debug` for verbose logging (also allows multiple `runapi` instances).
- `--update` to refresh duplicates instead of skipping.
- `--template <name>` to pick a template.
- `--port <port>` for `runapi`.
- `--list` to list available templates.

## API + UI (dynamic mode)
1) Start the API against the current DB:
```bash
python flat.py runapi --debug --port 3001
```
This exposes `http://localhost:3001/graphql`, push endpoints, and serves the
built React bundle from `api/ui/build`.

2) Develop the UI with hot reload:
```bash
cd api/ui
yarn start   # proxies GraphQL to http://localhost:3001/
```

3) Build the production UI bundle (served by the API):
```bash
cd api/ui
yarn build   # outputs to api/ui/build
```

## Legacy static build (deprecated but still available)
The original flow renders a static site under `build/` using templates in
`flatbuilder/`. Customize `flatbuilder/empty` (or add your own template) and run:
```bash
python flat.py init --template empty
python flat.py collect
python flat.py build
python flat.py preview   # view at http://localhost:7747
```
Prefer the dynamic API/UI path above for day-to-day use.

## Supported services and credentials
- **YouTube** (likes + uploads): app creds in `appkeys/google.json`; first run
  stores user tokens in `userkeys/google.json`.
- **Pocket**: consumer key in `appkeys/pocket.json`.
- **Vimeo**: app credentials in `appkeys/vimeo.json`.
- **RSS**: see hard-coded feeds in `flat.py`’s `Aggregator.collectors`; adjust as
  needed.
