# Agent Quickstart

- **What this project is**: Python CLI (`flat.py`) that collects likes/uploads from YouTube, Pocket, Vimeo and a few RSS feeds into SQLite (`db.sqlite`), then serves them via a Flask + GraphQL API with a React UI in `api/ui` (legacy static builder still exists).

- **Core commands**
  - Collect data: `python flat.py collect` (use `--update` to refresh duplicates, `--debug` for verbose).
  - Run API server: `python flat.py runapi --debug --port 3001` (serves GraphQL at `/graphql` and the built UI).
  - React dev server: `cd api/ui && yarn start` (points at `http://localhost:3001/`).
  - Build production UI: `cd api/ui && yarn build` (output used by the API).
  - Legacy static flow: `python flat.py init --template empty && python flat.py collect && python flat.py build`.

- **Secrets & data**
  - App creds go in `appkeys/<service>.json` (e.g. `google.json`, `pocket.json`, `vimeo.json`).
  - User tokens are written/read from `userkeys/<service>.json` after the first OAuth dance.
  - DB location/format configured in `flat.json` (defaults to SQLite at `db.sqlite`).

- **Where things live**
  - Collectors: `collectors/` (YouTube, Pocket, Vimeo, RSS, OpenGraph enrichments).
  - Storage backends: `storage/`.
  - API + GraphQL schema: `api/api_server.py`, `api/schema.py`.
  - React UI: `api/ui/src`.
  - Static builder: `flatbuilder/` (deprecated path, but still functional).

- **Gotchas**
  - Running collectors may open a browser for OAuth on first use.
  - The API serves `api/ui/build`; remember to rebuild the UI after frontend changes.
