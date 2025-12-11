# Implementation Plan - Read-Along LLM Feature

## Goal
Add "read along" capability to the ebook reader, allowing users to request JLPT-level specific explanations/summaries (N5-N1) for the current chapter using OpenAI's API.

## Dependencies
- `openai`
- `python-dotenv`

## Step 1: Configuration & Environment
- [ ] 1.  **Create `.env.example`**:
    - Add `OPENAI_API_KEY`, `LLM_MODEL` (default: `gpt-4o-mini`), `LLM_DRY_RUN` (default: `false`).
- [ ] 2.  **Create `config.py`**:
    - Load environment variables using `python-dotenv`.
    - Define a `Settings` class or dictionary to centralize config.

## Step 2: Backend - LLM Client & Caching
- [ ] 1.  **Create `prompts.py`**:
    - Define a dictionary mapping levels (N5-N1) to specific system prompts.
    - Prompts should instruct the LLM to return simple HTML (e.g., `<h3>`, `<ul>`, `<p>`) for easy rendering.
- [ ] 2.  **Create `llm_client.py`**:
    - Implement `LLMClient` class.
    - Method `get_explanation(text: str, level: str, context: str) -> str`.
    - Implement "Dry Run" logic (return static lorem ipsum HTML if enabled).
    - Implement OpenAI API call with error handling.
- [ ] 3.  **Implement Caching (in `server.py` or `llm_client.py`)**:
    - Implement a simple JSON-based cache mechanism.
    - Store cache in `{book_folder}/readalong_cache.json`.
    - Key structure: `{chapter_index}_{level}`.

## Step 3: Backend - API Endpoint
- [ ] 1.  **Update `server.py`**:
    - Import `LLMClient`.
    - Add Pydantic model for request body: `class ReadAlongRequest(BaseModel): book_id: str, chapter_index: int, level: str`.
    - Add route `POST /api/readalong`:
        - Validate inputs.
        - Load book using `load_book_cached`.
        - Retrieve chapter text.
        - Check cache.
        - If miss: call `LLMClient`, update cache, save to disk.
        - Return JSON: `{ "content": "..." }`.

## Step 4: Frontend - UI/UX
- [ ] 1.  **Update `templates/reader.html`**:
    - **Styles**: Add CSS for a "sidebar drawer" (right side, collapsible) and "floating control bar" or sticky header controls.
    - **HTML**:
        - Add a container for the drawer.
        - Add buttons: `[N5] [N4] [N3] [N2] [N1]`.
    - **JavaScript**:
        - Add function `fetchReadAlong(level)`.
        - Show loading spinner in drawer.
        - Fetch from `/api/readalong`.
        - Inject HTML response into drawer.
        - Handle errors (alert or display message).

## Step 5: Verification
- [ ] 1.  Run with `LLM_DRY_RUN=true` and verify UI interactions.
- [ ] 2.  Run with valid API key and verify response content.
- [ ] 3.  Restart server and verify data loads from cache (no new API call).
