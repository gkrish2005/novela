import { useCallback, useEffect, useState } from "react";
import { api, Book, Chapter } from "./api/client";
import { BookView } from "./components/BookView";
import { FullScreenPlayer } from "./components/FullScreenPlayer";
import { ImportScreen } from "./components/ImportScreen";
import { LibrarySidebar } from "./components/LibrarySidebar";

export default function App() {
  const [books, setBooks] = useState<Book[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [showImport, setShowImport] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const [showSyncedText, setShowSyncedText] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const [fullscreenChapter, setFullscreenChapter] = useState<Chapter | null>(null);

  const selectedBook = books.find((b) => b.id === selectedId) ?? null;
  const activeChapter =
    selectedBook?.chapters.find((c) => c.status === "ready") ?? selectedBook?.chapters[0] ?? null;

  useEffect(() => {
    if (!selectedBook || !fullscreenChapter) return;
    const updated = selectedBook.chapters.find((c) => c.id === fullscreenChapter.id);
    if (updated) setFullscreenChapter(updated);
  }, [selectedBook?.id, selectedBook?.chapters.length]);

  const refreshBooks = useCallback(async () => {
    try {
      const list = await api.listBooks();
      setBooks(list);
      if (selectedId && !list.find((b) => b.id === selectedId)) {
        setSelectedId(null);
      }
    } catch {
      setBackendOk(false);
    }
  }, [selectedId]);

  const refreshBook = useCallback(async (id: number) => {
    const book = await api.getBook(id);
    setBooks((prev) => prev.map((b) => (b.id === id ? book : b)));
  }, []);

  useEffect(() => {
    let active = true;
    let timer: any = null;

    const check = async () => {
      try {
        await api.health();
        if (active) {
          setBackendOk(true);
          refreshBooks();
          if (timer) clearInterval(timer);
        }
      } catch {
        if (active) {
          setBackendOk(false);
        }
      }
    };

    check();
    timer = setInterval(check, 1500);

    return () => {
      active = false;
      if (timer) clearInterval(timer);
    };
  }, [refreshBooks]);

  const handleImported = async (bookId: number) => {
    setShowImport(false);
    await refreshBooks();
    setSelectedId(bookId);
    const job = await api.narrate(bookId);
    const poll = setInterval(async () => {
      const j = await api.getJob(job.id);
      if (j.status === "done" || j.status === "error") {
        clearInterval(poll);
        refreshBook(bookId);
      }
    }, 2000);
  };

  const handleCoverChange = async (bookId: number, file: File) => {
    await api.uploadCover(bookId, file);
    refreshBook(bookId);
  };

  const handleRename = async (bookId: number, oldTitle: string) => {
    const newTitle = prompt("Enter new title:", oldTitle);
    if (newTitle && newTitle.trim() && newTitle.trim() !== oldTitle) {
      try {
        await api.updateBook(bookId, { title: newTitle.trim() });
        await refreshBooks();
      } catch (err) {
        alert(err instanceof Error ? err.message : "Rename failed");
      }
    }
  };

  const handleDelete = async (bookId: number) => {
    if (confirm("Are you sure you want to delete this book? This will erase all text, cover image, and generated audio from disk.")) {
      try {
        await api.deleteBook(bookId);
        await refreshBooks();
      } catch (err) {
        alert(err instanceof Error ? err.message : "Deletion failed");
      }
    }
  };

  if (backendOk === false) {
    return (
      <div className="backend-error">
        <h1 className="serif-title">Novela</h1>
        <p>Cannot reach the Python backend at http://127.0.0.1:8742</p>
        <p className="hint">Start it with: <code>cd backend && uvicorn app.main:app --port 8742</code></p>
        <style>{`
          .backend-error {
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            color: var(--text-secondary);
          }
          .hint code {
            background: var(--bg-card);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            color: var(--accent);
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <LibrarySidebar
        books={books}
        selectedId={selectedId}
        activeBook={selectedBook}
        currentChapterTitle={activeChapter?.title ?? ""}
        speed={speed}
        onSelect={(id) => {
          setSelectedId(id);
          setShowImport(false);
        }}
        onNew={() => {
          setShowImport(true);
          setSelectedId(null);
        }}
        onOpenPlayer={() => {
          if (selectedBook && activeChapter?.status === "ready") {
            setFullscreenChapter(activeChapter);
            setFullscreen(true);
          }
        }}
        onCoverChange={handleCoverChange}
        onRename={handleRename}
        onDelete={handleDelete}
      />

      <main className="main-content">
        {showImport || (!selectedBook && books.length === 0) ? (
          <ImportScreen onImported={handleImported} />
        ) : selectedBook ? (
          <BookView book={selectedBook} onRefresh={() => refreshBook(selectedBook.id)} />
        ) : (
          <ImportScreen onImported={handleImported} />
        )}
      </main>

      {fullscreen && selectedBook && fullscreenChapter && (
        <FullScreenPlayer
          book={selectedBook}
          chapter={fullscreenChapter}
          speed={speed}
          onSpeedChange={setSpeed}
          onChapterChange={(ch) => setFullscreenChapter(ch)}
          onPrioritizeChapter={async (ch) => {
            await api.prioritizeChapter(ch.id);
            await refreshBook(selectedBook.id);
          }}
          onClose={() => setFullscreen(false)}
          showText={showSyncedText}
          onToggleText={() => setShowSyncedText((v) => !v)}
          coverUrl={api.coverUrl(selectedBook.id)}
        />
      )}
    </div>
  );
}
