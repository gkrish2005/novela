import { Chapter, formatTime } from "../api/client";

type Props = {
  open: boolean;
  chapters: Chapter[];
  activeChapterId: number | null;
  onClose: () => void;
  onSelectReady: (ch: Chapter) => void;
  onPrioritizePending: (ch: Chapter) => void;
};

export function ChapterOverlay({
  open,
  chapters,
  activeChapterId,
  onClose,
  onSelectReady,
  onPrioritizePending,
}: Props) {
  if (!open) return null;

  return (
    <div className="chapter-overlay-backdrop" onClick={onClose}>
      <div className="chapter-overlay" onClick={(e) => e.stopPropagation()}>
        <div className="chapter-overlay-header">
          <h3>Chapters</h3>
          <button onClick={onClose}>✕</button>
        </div>
        <div className="chapter-overlay-list">
          {chapters.map((ch) => {
            const ready = ch.status === "ready";
            return (
              <button
                key={ch.id}
                className={`chapter-row ${activeChapterId === ch.id ? "active" : ""}`}
                onClick={() => (ready ? onSelectReady(ch) : onPrioritizePending(ch))}
              >
                <div className="chapter-row-main">
                  <span className="chapter-row-title">{ch.title}</span>
                  <span className={`chapter-row-status ${ready ? "ready" : "pending"}`}>
                    {ready ? "Ready" : "Queue next"}
                  </span>
                </div>
                <div className="chapter-row-time">
                  {formatTime(ch.start_ms)} · {formatTime(ch.duration_ms)}
                </div>
              </button>
            );
          })}
        </div>
      </div>
      <style>{`
        .chapter-overlay-backdrop {
          position: fixed;
          inset: 0;
          background: rgba(0, 0, 0, 0.5);
          z-index: 120;
          display: flex;
          justify-content: center;
          align-items: center;
        }
        .chapter-overlay {
          width: min(560px, 92vw);
          max-height: 72vh;
          overflow: hidden;
          border: 1px solid var(--border);
          border-radius: 12px;
          background: var(--bg-card);
          display: flex;
          flex-direction: column;
        }
        .chapter-overlay-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.9rem 1rem;
          border-bottom: 1px solid var(--border);
        }
        .chapter-overlay-header h3 {
          margin: 0;
          font-size: 1rem;
        }
        .chapter-overlay-list {
          overflow-y: auto;
          padding: 0.5rem;
        }
        .chapter-row {
          width: 100%;
          text-align: left;
          background: transparent;
          border-radius: 8px;
          padding: 0.7rem 0.75rem;
          margin-bottom: 0.35rem;
        }
        .chapter-row:hover,
        .chapter-row.active {
          background: var(--bg-app);
        }
        .chapter-row-main {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 0.5rem;
        }
        .chapter-row-title {
          font-size: 0.95rem;
        }
        .chapter-row-status {
          font-size: 0.75rem;
          border: 1px solid var(--border);
          border-radius: 999px;
          padding: 0.1rem 0.45rem;
          color: var(--text-secondary);
        }
        .chapter-row-status.ready {
          border-color: var(--accent-dim);
          color: var(--accent);
        }
        .chapter-row-time {
          margin-top: 0.2rem;
          font-size: 0.75rem;
          color: var(--text-muted);
        }
      `}</style>
    </div>
  );
}
