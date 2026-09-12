import sqlite3
import shutil
import os
from pathlib import Path

# Paths
APP_DATA_DIR = Path.home() / "Library" / "Application Support" / "Novela"
DB_PATH = APP_DATA_DIR / "novela.sqlite"
AUDIO_DIR = APP_DATA_DIR / "audio"
COVERS_DIR = APP_DATA_DIR / "covers"
IMPORTS_DIR = APP_DATA_DIR / "imports"

print("--- Novela Disk & Database Cleanup Script ---")
print("Target App-Data Directory:", APP_DATA_DIR)

if not DB_PATH.exists():
    print(f"Error: Database not found at {DB_PATH}. Nothing to clean.")
    exit(0)

# Connect to database
conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

# Get all books to delete (1, 2, 3, 4, 5, 6)
target_book_ids = [1, 2, 3, 4, 5, 6]
print(f"Targeting books for deletion: {target_book_ids}")

for book_id in target_book_ids:
    print(f"\nCleaning up Book ID: {book_id}")
    
    # Check if book exists in db
    cursor.execute("SELECT id, title, cover_path, source_file_path FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()
    
    if book:
        b_id, title, cover_path, source_file_path = book
        print(f"Found book in database: ID={b_id}, Title={repr(title)}")
        
        # 1. Get all chapters
        cursor.execute("SELECT id FROM chapters WHERE book_id = ?", (book_id,))
        chapters = [r[0] for r in cursor.fetchall()]
        print(f"  Deleting {len(chapters)} chapters...")
        
        for ch_id in chapters:
            # Delete word timestamps
            cursor.execute("DELETE FROM word_timestamps WHERE chapter_id = ?", (ch_id,))
            # Delete chunks
            cursor.execute("DELETE FROM chunks WHERE chapter_id = ?", (ch_id,))
            # Delete chapter
            cursor.execute("DELETE FROM chapters WHERE id = ?", (ch_id,))
            
        # 2. Delete playback state
        cursor.execute("DELETE FROM playback_state WHERE book_id = ?", (book_id,))
        
        # 3. Delete jobs
        cursor.execute("DELETE FROM jobs WHERE book_id = ?", (book_id,))
        
        # 4. Delete book
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        print("  Database records deleted.")
        
        # 5. Delete cover file
        if cover_path:
            p = Path(cover_path)
            if p.exists():
                try:
                    p.unlink()
                    print(f"  Deleted cover file: {p}")
                except Exception as e:
                    print(f"  Error deleting cover: {e}")
                    
        # 6. Delete source file
        if source_file_path:
            p = Path(source_file_path)
            if p.exists():
                try:
                    p.unlink()
                    print(f"  Deleted source file: {p}")
                except Exception as e:
                    print(f"  Error deleting source file: {e}")
    else:
        print(f"Book ID {book_id} not found in database.")
        
    # 7. Delete audio directory
    book_audio_dir = AUDIO_DIR / f"book{book_id}"
    if book_audio_dir.exists():
        try:
            shutil.rmtree(book_audio_dir, ignore_errors=True)
            print(f"  Deleted audio folder: {book_audio_dir}")
        except Exception as e:
            print(f"  Error deleting audio folder: {e}")

# Save database changes
conn.commit()
conn.close()
print("\nDatabase changes committed successfully.")

# 8. Delete redundant temporary import files (import_*.txt / import_*.pdf)
print("\nScanning imports folder for redundant files...")
if IMPORTS_DIR.exists():
    for item in IMPORTS_DIR.iterdir():
        if item.is_file() and item.name.startswith("import_"):
            try:
                item.unlink()
                print(f"Deleted redundant import file: {item.name}")
            except Exception as e:
                print(f"Error deleting {item.name}: {e}")

print("\n--- Disk Space After Cleanup ---")
os.system(f"du -sh \"{APP_DATA_DIR}\"")
os.system(f"du -sh \"{APP_DATA_DIR}\"/*")
