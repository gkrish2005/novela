import { useState } from "react";
import { Book, Chapter, formatTime } from "../api/client";
import { usePlayback } from "../hooks/usePlayback";
import { useMediaSession } from "../hooks/useMediaSession";
import { ChapterOverlay } from "./ChapterOverlay";
import { SyncedText } from "./SyncedText";

type Props = {
  book: Book;
  chapter: Chapter;
  speed: number;
  onSpeedChange: (s: number) => void;
  onChapterChange: (ch: Chapter) => void;
  onClose: () => void;
  showText: boolean;
  onToggleText: () => void;
  coverUrl: string;
  onPrioritizeChapter: (ch: Chapter) => Promise<void> | void;
};

export function FullScreenPlayer({
  book,
  chapter,
  speed,
  onSpeedChange,
  onChapterChange,
  onClose,
  showText,
  onToggleText,
  coverUrl,
  onPrioritizeChapter,
}: Props) {
  const [showChapters, setShowChapters] = useState(false);
  const pb = usePlayback({
    book,
    chapter,
    speed,
    onSpeedChange,
    onChapterChange,
  });

  useMediaSession(book, chapter, pb.playing, pb.togglePlay, pb.togglePlay, pb.nextChapter, pb.prevChapter);

  const progress = pb.durationMs > 0 ? (pb.currentMs / pb.durationMs) * 100 : 0;

  return (
    <div className="fullscreen-player">
      <div className="blur-bg" style={{ backgroundImage: `url(${coverUrl})` }} />
      <div className="fs-overlay" />

      <button className="close-btn" onClick={onClose} aria-label="Close">
        ✕
      </button>

      <input
        className="volume-slider"
        type="range"
        min={0}
        max={1}
        step={0.05}
        defaultValue={1}
        onChange={(e) => {
          const vol = parseFloat(e.target.value);
          document.querySelectorAll("audio").forEach((a) => {
            (a as HTMLAudioElement).volume = vol;
          });
        }}
      />

      <div className="fs-content">
        <div className="art-panel">
          {showText ? (
            <div className="text-panel">
              <SyncedText
                text={pb.text}
                words={pb.words}
                activeWordIdx={pb.activeWordIdx}
                onWordClick={pb.seek}
              />
            </div>
          ) : (
            <img className="large-cover" src={coverUrl} alt="" />
          )}
        </div>

        <div className="controls-panel">
          <h2 className="serif-title track-title">{book.title}</h2>
          <p className="chapter-name">{chapter.title}</p>

          <div className="scrubber-row">
            <span>{formatTime(pb.currentMs)}</span>
            <input
              type="range"
              min={0}
              max={pb.durationMs || 1}
              value={pb.currentMs}
              onChange={(e) => pb.seek(Number(e.target.value))}
              className="scrubber"
            />
            <span>-{formatTime(Math.max(0, pb.durationMs - pb.currentMs))}</span>
          </div>

          <div className="transport">
            <button onClick={pb.prevChapter} title="Previous chapter">⏮</button>
            <button onClick={() => pb.skip(-15000)} title="Back 15s">↺15</button>
            <button className="play-btn" onClick={pb.togglePlay}>
              {pb.playing ? "⏸" : "▶"}
            </button>
            <button onClick={() => pb.skip(15000)} title="Forward 15s">15↻</button>
            <button onClick={pb.nextChapter} title="Next chapter">⏭</button>
          </div>

          <div className="speed-row">
            {pb.SPEED_PRESETS.map((s) => (
              <button
                key={s}
                className={`speed-btn ${speed === s ? "active" : ""}`}
                onClick={() => onSpeedChange(s)}
              >
                {s}x
              </button>
            ))}
            <button className="speed-fine" onClick={() => pb.fineSpeed(-0.05)}>−</button>
            <span className="speed-value">{speed.toFixed(2)}x</span>
            <button className="speed-fine" onClick={() => pb.fineSpeed(0.05)}>+</button>
          </div>
        </div>
      </div>

      <button className="text-toggle" onClick={onToggleText} title="Toggle synced text">
        {showText ? "🖼" : "📝"}
      </button>
      <button className="chapters-toggle" onClick={() => setShowChapters(true)} title="Chapter list">
        ☰
      </button>
      <ChapterOverlay
        open={showChapters}
        chapters={book.chapters}
        activeChapterId={chapter.id}
        onClose={() => setShowChapters(false)}
        onSelectReady={(ch) => {
          onChapterChange(ch);
          setShowChapters(false);
        }}
        onPrioritizePending={async (ch) => {
          await onPrioritizeChapter(ch);
          setShowChapters(false);
        }}
      />

      <style>{`
        .fullscreen-player {
          position: fixed;
          inset: 0;
          z-index: 100;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .blur-bg {
          position: absolute;
          inset: -20px;
          background-size: cover;
          background-position: center;
          filter: blur(60px) brightness(0.35);
          transform: scale(1.1);
        }
        .fs-overlay {
          position: absolute;
          inset: 0;
          background: rgba(8, 8, 10, 0.6);
        }
        .close-btn {
          position: absolute;
          top: 1.25rem;
          left: 1.25rem;
          z-index: 2;
          font-size: 1.25rem;
          color: var(--text-secondary);
          width: 36px;
          height: 36px;
          border-radius: 50%;
          background: rgba(20, 20, 23, 0.8);
        }
        .volume-slider {
          position: absolute;
          top: 1.5rem;
          right: 1.5rem;
          z-index: 2;
          width: 100px;
        }
        .fs-content {
          position: relative;
          z-index: 1;
          display: flex;
          gap: 3rem;
          max-width: 900px;
          width: 90%;
          align-items: flex-start;
        }
        .art-panel { flex-shrink: 0; }
        .large-cover {
          width: 320px;
          height: 320px;
          border-radius: 8px;
          object-fit: cover;
          box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }
        .text-panel {
          width: 320px;
          height: 320px;
          background: rgba(20, 20, 23, 0.85);
          border-radius: 8px;
          overflow: hidden;
        }
        .controls-panel { flex: 1; padding-top: 2rem; }
        .track-title { font-size: 1.75rem; margin: 0 0 0.25rem; }
        .chapter-name { color: var(--text-secondary); margin: 0 0 1.5rem; }
        .scrubber-row {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          font-size: 0.8rem;
          color: var(--text-secondary);
          margin-bottom: 1.25rem;
        }
        .scrubber { flex: 1; }
        .transport {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 1rem;
          margin-bottom: 1.25rem;
        }
        .transport button {
          font-size: 1.25rem;
          color: var(--text-primary);
          padding: 0.5rem;
        }
        .play-btn {
          font-size: 2rem !important;
          color: var(--accent) !important;
        }
        .speed-row {
          display: flex;
          align-items: center;
          gap: 0.4rem;
          flex-wrap: wrap;
        }
        .speed-btn {
          padding: 0.3rem 0.6rem;
          border-radius: 4px;
          font-size: 0.8rem;
          color: var(--text-secondary);
          border: 1px solid transparent;
        }
        .speed-btn.active {
          color: var(--accent);
          border-color: var(--accent);
        }
        .speed-fine, .speed-value {
          font-size: 0.85rem;
          color: var(--text-secondary);
        }
        .text-toggle {
          position: absolute;
          bottom: 1.5rem;
          right: 1.5rem;
          z-index: 2;
          font-size: 1.25rem;
          background: rgba(20, 20, 23, 0.8);
          width: 44px;
          height: 44px;
          border-radius: 50%;
        }
        .chapters-toggle {
          position: absolute;
          bottom: 1.5rem;
          right: 4.7rem;
          z-index: 2;
          font-size: 1.1rem;
          background: rgba(20, 20, 23, 0.8);
          width: 44px;
          height: 44px;
          border-radius: 50%;
        }
      `}</style>
    </div>
  );
}
