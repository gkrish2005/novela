import sqlite3
from pathlib import Path

db_path = Path("/Users/krishgupta/Library/Application Support/Novela/novela.sqlite")
if not db_path.exists():
    print("Database not found!")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Find the latest book in the database
cursor.execute("SELECT id, title, language, source_file_path FROM books ORDER BY id DESC LIMIT 1;")
book = cursor.fetchone()

if not book:
    print("No books found in the database. Please import 1984 first!")
    exit(0)

b_id, title, lang, source_path = book
print(f"=== Latest Book In Database ===")
print(f"Book ID: {b_id}")
print(f"Title: {title}")
print(f"Language: {lang}")
print(f"Source Path: {source_path}")

# Calculate total character count across all chunks
cursor.execute("""
    SELECT SUM(LENGTH(chunks.text)) 
    FROM chunks 
    JOIN chapters ON chunks.chapter_id = chapters.id 
    WHERE chapters.book_id = ?
""", (b_id,))
char_count = cursor.fetchone()[0] or 0
print(f"Total Character Count: {char_count} characters")

# Get list of chapters
cursor.execute("""
    SELECT id, "index", title, status 
    FROM chapters 
    WHERE book_id = ? 
    ORDER BY "index"
""", (b_id,))
chapters = cursor.fetchall()
print(f"\n=== Chapter List ({len(chapters)} chapters) ===")
for ch in chapters:
    # Count chunks in this chapter
    cursor.execute("SELECT COUNT(*), SUM(LENGTH(text)) FROM chunks WHERE chapter_id = ?", (ch[0],))
    chunk_count, ch_len = cursor.fetchone()
    print(f"Index {ch[1]} (ID {ch[0]}): Title={repr(ch[2])} | Status={ch[3]} | Chunks={chunk_count} | Size={ch_len or 0} chars")

# Print first sentence of Chapter 5 and Chapter 10
# Note: Chapter list indices are 0-based.
print("\n=== Chapter 5 & Chapter 10 Navigation Verification ===")
for ch_idx in [5, 10]:
    if ch_idx < len(chapters):
        ch_id = chapters[ch_idx][0]
        ch_title = chapters[ch_idx][2]
        # Get first chunk text
        cursor.execute("SELECT text FROM chunks WHERE chapter_id = ? ORDER BY \"index\" LIMIT 1", (ch_id,))
        chunk_text = cursor.fetchone()
        if chunk_text:
            text = chunk_text[0].strip()
            # Extract first sentence (split by period/newline)
            sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
            first_sentence = sentences[0] if sentences else text
            print(f"Chapter index {ch_idx} ({ch_title}):")
            print(f"  First Sentence: \"{first_sentence}.\"")
        else:
            print(f"Chapter index {ch_idx} ({ch_title}): No chunks found.")
    else:
        print(f"Chapter index {ch_idx}: Not found (only {len(chapters)} chapters in DB).")

# Print sample word timestamps
print("\n=== Sample Word Timestamps (First 15 words with timestamps) ===")
cursor.execute("""
    SELECT word_timestamps.word, word_timestamps.start_ms, word_timestamps.end_ms, word_timestamps.char_start, word_timestamps.char_end
    FROM word_timestamps
    JOIN chapters ON word_timestamps.chapter_id = chapters.id
    WHERE chapters.book_id = ?
    ORDER BY chapters."index", word_timestamps.start_ms
    LIMIT 15
""")
wts = cursor.fetchall()
if wts:
    for w in wts:
        print(f"Word: {repr(w[0]):<15} | Start: {w[1]:<5} ms | End: {w[2]:<5} ms | Span: {w[3]}-{w[4]} | Duration: {w[2]-w[1]} ms")
else:
    print("No word timestamps generated yet. (Have you started narration?)")

conn.close()
