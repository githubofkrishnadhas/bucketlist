# Bucketly

Bucketly is a local-first bucket list and life experiences journal built with Streamlit and SQLite.

## Requirements

- Python 3.13 or later
- [uv](https://docs.astral.sh/uv/)

## Run locally

From the project root, sync the project dependencies and start Streamlit:

```powershell
uv sync
uv run streamlit run src/bucketly/app.py
```

The app stores its SQLite database in `data/bucketly.db`. Existing databases are upgraded automatically when the app starts. Items can be created, searched, filtered, edited, moved through their status, and deleted. Completed items appear in Memories, where reflections are shown. The Settings page stores a local profile with an avatar choice and optional contact details; the visibility preference is saved but is not published while the app is local-only. About & Contact describes the project and stores feedback locally; feedback is not emailed or transmitted to a maintainer.
