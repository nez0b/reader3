import os
import pickle
from functools import lru_cache
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from bs4 import BeautifulSoup

from reader3 import Book, BookMetadata, ChapterContent, TOCEntry
from llm_client import llm_client

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Where are the book folders located?
BOOKS_DIR = "."

@lru_cache(maxsize=10)
def load_book_cached(folder_name: str) -> Optional[Book]:
    """
    Loads the book from the pickle file.
    Cached so we don't re-read the disk on every click.
    """
    file_path = os.path.join(BOOKS_DIR, folder_name, "book.pkl")
    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, "rb") as f:
            book = pickle.load(f)
        return book
    except Exception as e:
        print(f"Error loading book {folder_name}: {e}")
        return None

class ReadAlongRequest(BaseModel):
    book_id: str
    chapter_index: int
    level: str

@app.post("/api/readalong")
async def get_readalong(request: ReadAlongRequest):
    book = load_book_cached(request.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if request.chapter_index < 0 or request.chapter_index >= len(book.spine):
        raise HTTPException(status_code=404, detail="Chapter not found")
        
    current_chapter = book.spine[request.chapter_index]
    
    # Extract text from HTML
    soup = BeautifulSoup(current_chapter.content, "html.parser")
    text_content = soup.get_text(separator="\n")
    
    # Limit text length
    truncated_text = text_content[:4000]
    if len(text_content) > 4000:
        truncated_text += "\n...(text truncated)..."
        
    # Cache path
    cache_path = os.path.join(BOOKS_DIR, request.book_id, "readalong_cache.json")
    cache_key = f"{request.chapter_index}_{request.level}"
    
    # Context
    context = f"Title: {book.metadata.title}"
    
    explanation = llm_client.get_cached_explanation(
        cache_path=cache_path,
        key=cache_key,
        text=truncated_text,
        level=request.level,
        context=context
    )
    
    return {"content": explanation}

@app.get("/", response_class=HTMLResponse)
async def library_view(request: Request):
    """Lists all available processed books."""
    books = []

    # Scan directory for folders ending in '_data' that have a book.pkl
    if os.path.exists(BOOKS_DIR):
        for item in os.listdir(BOOKS_DIR):
            if item.endswith("_data") and os.path.isdir(item):
                # Try to load it to get the title
                book = load_book_cached(item)
                if book:
                    books.append({
                        "id": item,
                        "title": book.metadata.title,
                        "author": ", ".join(book.metadata.authors),
                        "chapters": len(book.spine)
                    })

    return templates.TemplateResponse("library.html", {"request": request, "books": books})

@app.get("/read/{book_id}", response_class=HTMLResponse)
async def redirect_to_first_chapter(book_id: str):
    """Helper to just go to chapter 0."""
    return await read_chapter(book_id=book_id, chapter_index=0)

@app.get("/read/{book_id}/{chapter_index}", response_class=HTMLResponse)
async def read_chapter(request: Request, book_id: str, chapter_index: int):
    """The main reader interface."""
    book = load_book_cached(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if chapter_index < 0 or chapter_index >= len(book.spine):
        raise HTTPException(status_code=404, detail="Chapter not found")

    current_chapter = book.spine[chapter_index]

    # Calculate Prev/Next links
    prev_idx = chapter_index - 1 if chapter_index > 0 else None
    next_idx = chapter_index + 1 if chapter_index < len(book.spine) - 1 else None

    return templates.TemplateResponse("reader.html", {
        "request": request,
        "book": book,
        "current_chapter": current_chapter,
        "chapter_index": chapter_index,
        "book_id": book_id,
        "prev_idx": prev_idx,
        "next_idx": next_idx
    })

@app.get("/read/{book_id}/images/{image_name}")
async def serve_image(book_id: str, image_name: str):
    """
    Serves images specifically for a book.
    The HTML contains <img src="images/pic.jpg">.
    The browser resolves this to /read/{book_id}/images/pic.jpg.
    """
    # Security check: ensure book_id is clean
    safe_book_id = os.path.basename(book_id)
    safe_image_name = os.path.basename(image_name)

    img_path = os.path.join(BOOKS_DIR, safe_book_id, "images", safe_image_name)

    if not os.path.exists(img_path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(img_path)

if __name__ == "__main__":
    import uvicorn
    print("Starting server at http://127.0.0.1:8123")
    uvicorn.run(app, host="127.0.0.1", port=8123)
