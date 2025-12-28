# Mobile App Transition Plan

Transforming `reader3` (currently a Python FastAPI web app) into a mobile application (iOS/Android) involves choosing between running the backend on a server vs. running everything on the device.

Here are the three best approaches, ordered from easiest to most complex.

## Approach 1: Self-Hosted Web App (PWA) - **Recommended**

The quickest way to use this on mobile is to host the current application on a server (e.g., a VPS, Raspberry Pi, or your desktop on the local network) and access it via a mobile browser.

### Steps:
1.  **Responsiveness**: Update `reader.html` CSS to ensure the sidebar/drawer works well on small screens (collapsible hamburger menu).
2.  **Manifest**: Add a `manifest.json` to make it installable as a PWA (add to home screen).
3.  **Host**: Run `uvicorn server:app --host 0.0.0.0` on your computer.
4.  **Access**: Open your computer's IP address on your phone (e.g., `http://192.168.1.5:8123`).

**Pros:**
*   Zero code rewrite (mostly CSS).
*   Syncs reading progress across devices automatically (if we add a database later).
*   LLM API keys stay secure on the server.

**Cons:**
*   Requires internet/network connection to the server.
*   Not a true "offline" app.

---

## Approach 2: Flet (Python-based Cross-Platform)

If you need a **standalone offline app** but want to keep writing Python, [Flet](https://flet.dev/) is an excellent choice. It allows you to build Flutter apps using Python.

### Steps:
1.  **UI Rewrite**: You would replace HTML/Jinja2 templates with Flet controls (`ft.Column`, `ft.Container`, `ft.ListView`).
2.  **Logic Port**: Move the `Book`, `ChapterContent` logic into the Flet app structure.
3.  **Packaging**: Flet can package your Python code and dependencies into an APK/IPA using `flet build`.

**Pros:**
*   Reuse existing Python logic (`reader3.py`, `llm_client.py`).
*   True native app install.
*   Offline capability (process books on device).

**Cons:**
*   Requires rewriting the UI layer entirely (HTML -> Flet components).
*   Large app size (bundles Python interpreter).

---

## Approach 3: Decoupled Frontend (React Native / Flutter) + Hosted Backend

If you want a "real" mobile UI with high performance but keep the heavy lifting on a server.

### Steps:
1.  **API Only**: Convert `server.py` to serve only JSON (no HTML templates). You already started this with `/api/readalong`. You'd need endpoints like `/api/books`, `/api/book/{id}/chapter/{idx}`.
2.  **Mobile App**: Build a frontend using React Native, Flutter, or Swift/Kotlin.
3.  **Connection**: The app fetches content from your Python server.

**Pros:**
*   Best user experience (animations, gestures).
*   Standard mobile development path.

**Cons:**
*   Complete rewrite of frontend.
*   Still requires the Python backend to be running somewhere (cannot easily run `ebooklib` and `scikit-learn` equivalents inside React Native).

---

## Summary Recommendation

**Start with Approach 1 (PWA).**
1.  Make your HTML template mobile-friendly.
2.  Run the server on your local network.
3.  Read from your phone.

If you strictly need an **offline** app that runs entirely on the phone without a server, **Approach 2 (Flet)** is your best bet to preserve your Python codebase.
