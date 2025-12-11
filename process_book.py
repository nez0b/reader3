import sys
import os
import reader3

def main():
    if len(sys.argv) < 2:
        print("Usage: uv run python process_book.py <filename.epub>")
        sys.exit(1)

    epub_file = sys.argv[1]
    if not os.path.exists(epub_file):
        print(f"Error: File '{epub_file}' not found.")
        sys.exit(1)

    out_dir = os.path.splitext(epub_file)[0] + "_data"
    
    print(f"Processing {epub_file} -> {out_dir}...")
    
    try:
        # Process the book using the imported module functions
        # This ensures the pickled classes are linked to 'reader3' module, not '__main__'
        book_obj = reader3.process_epub(epub_file, out_dir)
        reader3.save_to_pickle(book_obj, out_dir)
        print("Success! You can now run the server.")
    except Exception as e:
        print(f"Error processing book: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
