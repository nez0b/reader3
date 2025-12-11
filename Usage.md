# Usage Guide

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended package manager)

## Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    uv sync
    ```

## Configuration (LLM / OpenAI)

To enable the "Read Along" feature (JLPT explanations):

1.  Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
2.  Edit `.env` and configure your OpenAI settings:
    ```bash
    OPENAI_API_KEY=your-secret-api-key
    LLM_MODEL=gpt-4o-mini  # or other supported models
    LLM_DRY_RUN=false      # Set to 'true' to simulate responses without API usage
    ```

## Processing Books

Before reading, you must process your EPUB files into the format used by the reader.

1.  Place your `.epub` file in the project directory.
2.  Run the processing script:
    ```bash
    uv run python process_book.py your_book.epub
    ```
    This will create a folder named `your_book_data` containing the processed content.

## Running the Server

Start the web server:

```bash
uv run uvicorn server:app --reload --port 8123
```

Visit `http://127.0.0.1:8123` in your browser.

## Using the Read-Along Feature

1.  Open a book from the library.
2.  On the right side of the screen, you will see buttons for **N5** through **N1**.
3.  Click a level button to request an explanation of the current chapter suited for that JLPT level.
4.  The explanation (Summary, Vocabulary, Grammar) will appear in a sidebar drawer.
