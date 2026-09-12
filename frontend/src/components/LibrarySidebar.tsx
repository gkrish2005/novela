import { useRef } from "react";
import { api, Book, formatTime } from "../api/client";

type Props = {
  books: Book[];
  selectedId: number | null;
  activeBook: Book | null;
  currentChapterTitle: string;
  speed: number;
  onSelect: (id: number) => void;
  onNew: () => void;
  onOpenPlayer: () => void;
  onCoverChange: (bookId: number, file: File) => void;
  onRename: (bookId: number, oldTitle: string) => void;
  onDelete: (bookId: number) => void;
};

export function LibrarySidebar({
  books,
  selectedId,
  activeBook,
  currentChapterTitle,
  speed,
  onSelect,
  onNew,
  onOpenPlayer,
  onCoverChange,
  onRename,
  onDelete,
}: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  const coverTarget = useRef<number | null>(null);

  const langLabel = (l: string) => (l === "hi" ? "Hindi" : l === "mixed" ? "Mixed" : "English");

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="serif-title app-logo">Novela</h1>
        <button className="btn-primary" onClick={onNew}>
          + New
        </button>
      </div>

      <div className="library-list">
        {books.length === 0 && (
          <p className="empty-hint">Import a book to get started.</p>
        )}
        {books.map((book) => (
          <div
            key={book.id}
            className={`library-row ${selectedId === book.id ? "selected" : ""}`}
            onClick={() => onSelect(book.id)}
            onContextMenu={(e) => {
              e.preventDefault();
              coverTarget.current = book.id;
              fileRef.current?.click();
            }}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              const file = e.dataTransfer.files[0];
              if (file?.type.startsWith("image/")) onCoverChange(book.id, file);
            }}
          >
            <img
              className="cover-thumb"
              src={api.coverUrl(book.id)}
              alt=""
              onError={(e) => {
                (e.target as HTMLImageElement).style.visibility = "hidden";
              }}
            />
            <div className="row-meta" style={{ flex: 1 }}>
              <div className="row-title" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span>{book.title}</span>
                <div className="item-actions">
                  <button
                    className="action-btn"
                    title="Rename"
                    onClick={(e) => {
                      e.stopPropagation();
                      onRename(book.id, book.title);
                    }}
                  >
                    ✏️
                  </button>
                  <button
                    className="action-btn"
                    title="Delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(book.id);
                    }}
                  >
                    🗑️
                  </button>
                </div>
              </div>
              <div className="row-sub">
                {langLabel(book.language)} · {book.chapters.length} ch
                {book.total_duration_ms > 0 && ` · ${formatTime(book.total_duration_ms)}`}
              </div>
            </div>
          </div>
        ))}
      </div>

      {activeBook && (
        <button className="mini-player" onClick={onOpenPlayer}>
          <img className="cover-thumb" src={api.coverUrl(activeBook.id)} alt="" />
          <div className="row-meta">
            <div className="row-title">{activeBook.title}</div>
            <div className="row-sub">
              {currentChapterTitle} · {speed}x
            </div>
          </div>
        </button>
      )}

      <input
        ref={fileRef}
        type="file"
        accept="image/*"
        hidden
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file && coverTarget.current) onCoverChange(coverTarget.current, file);
          e.target.value = "";
        }}
      />

      <style>{`
        .sidebar {
          width: var(--sidebar-width);
          min-width: var(--sidebar-width);
          background: var(--bg-panel);
          border-right: 1px solid var(--border);
          display: flex;
          flex-direction: column;
          height: 100vh;
        }
        .sidebar-header {
          padding: 1.25rem 1rem;
          display: flex;
          align-items: center;
          justify-content: space-between;
          border-bottom: 1px solid var(--border);
        }
        .app-logo {
          margin: 0;
          font-size: 1.5rem;
          color: var(--accent);
        }
        .library-list {
          flex: 1;
          overflow-y: auto;
          padding: 0.5rem;
        }
        .empty-hint {
          color: var(--text-muted);
          font-size: 0.9rem;
          padding: 1rem;
          text-align: center;
        }
        .library-row {
          display: flex;
          gap: 0.75rem;
          padding: 0.6rem;
          border-radius: 8px;
          cursor: pointer;
          background: transparent;
          transition: background 0.15s;
        }
        .library-row:hover, .library-row.selected {
          background: var(--bg-card);
        }
        .cover-thumb {
          width: 48px;
          height: 48px;
          border-radius: 6px;
          object-fit: cover;
          background: var(--bg-card);
          flex-shrink: 0;
        }
        .row-meta { min-width: 0; text-align: left; }
        .row-title {
          font-size: 0.95rem;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .item-actions {
          display: flex;
          gap: 0.35rem;
          opacity: 0;
          transition: opacity 0.15s ease-in-out;
        }
        .library-row:hover .item-actions {
          opacity: 1;
        }
        .action-btn {
          background: transparent;
          border: none;
          padding: 2px 4px;
          cursor: pointer;
          font-size: 0.85rem;
          border-radius: 4px;
          transition: background 0.1s;
        }
        .action-btn:hover {
          background: rgba(255, 255, 255, 0.12);
        }
        .row-sub {
          font-size: 0.75rem;
          color: var(--text-secondary);
          margin-top: 0.15rem;
        }
        .mini-player {
          display: flex;
          gap: 0.75rem;
          padding: 0.75rem 1rem;
          background: var(--bg-card);
          border-top: 1px solid var(--border);
          width: 100%;
          text-align: left;
        }
        .mini-player:hover { background: #1a1a1e; }
      `}</style>
    </aside>
  );
}
