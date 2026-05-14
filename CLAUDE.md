# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

Anki addon (v25.9.2). Entry point is `__init__.py`, which registers a single hook:

```python
gui_hooks.webview_did_receive_js_message.append(task_router)
```

`task_router` parses JSON from the JS bridge and dispatches on `action`:

| action | handler | LLM |
|---|---|---|
| `task_for_card_with_eng_word` | `src/core/create_task.py` | none |
| `check grammar and other` | `src/core/review_task.py` | DeepSeek |

Results are pushed back to JS via `context.web.eval("receiveTask(...)")` / `"receiveReviewResponse(...)"`.

### Task creation (`create_task`)

Pure Python, no network. Builds a daily-stable seed: `sum(ord(c) for c in word) + sum(ord(c) for c in definition) + day + month`. Uses `random.choices` with weights from `src/data/english_data.py` to pick tense → usage-or-type → sentence type or usage → pronoun. Returns an Obsidian link for the chosen tense.

### Review (`review_task`)

1. Parses input into `DataToReview` (`src/data/parse_data.py`)
2. Builds a DeepSeek chat-completions request via `src/data/base_request_data.py`
3. Calls `deepseek_client.generate_content()` — expects raw JSON in `choices[0]["message"]["content"]`
4. Parses the JSON directly into `ReviewResponseModel` and stores to SQLite via `src/db/db_writer.py`

`src/llm/gemini.py` exists with model-fallback logic but is **not called** by any current flow.

### Config & paths

`.env` is loaded manually (no python-dotenv) by `src/config/read_env.py`. Key names use hyphens:

```
goog-api-key=YOUR_GOOGLE_API_KEY
deepseek-api-key=YOUR_DEEPSEEK_API_KEY
```

`ROOT_PATH` (`src/utils/path.py`) walks up from `__file__` until it finds `pyproject.toml` — so `pyproject.toml` must stay in the addon root.

### Database

SQLite, stored at `{anki_addons_folder}/review_task_addon/anki.sqlite` (path hardcoded in `src/db/db_writer.py`). Three tables: `words`, `conditions`, `reviews`. Hand-rolled table layer in `src/db/tables/` with service helpers in `src/db/service/`.

### Models

`BaseResponseModel` (`src/data/base_response_mobel.py`) is hand-rolled, not pydantic. Its `.schema()` classmethod reflects `__annotations__` to produce a Gemini-compatible JSON schema (`responseSchema` format). `ReviewResponseModel` inherits it and uses `setattr` in `__init__` to accept arbitrary keys from the LLM response.
