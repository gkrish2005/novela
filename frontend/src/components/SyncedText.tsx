import { useEffect, useRef } from "react";
import { Word } from "../api/client";

type Props = {
  text: string;
  words: Word[];
  activeWordIdx: number;
  onWordClick: (startMs: number) => void;
};

export function SyncedText({ text, words, activeWordIdx, onWordClick }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const activeRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    activeRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  }, [activeWordIdx]);

  if (words.length === 0) {
    return (
      <div className="synced-text">
        <p>{text}</p>
      </div>
    );
  }

  const parts: React.ReactNode[] = [];
  let cursor = 0;

  words.forEach((w, i) => {
    if (w.char_start > cursor) {
      parts.push(<span key={`gap-${i}`}>{text.slice(cursor, w.char_start)}</span>);
    }
    parts.push(
      <span
        key={`w-${i}`}
        ref={i === activeWordIdx ? activeRef : undefined}
        className={i === activeWordIdx ? "word-highlight" : ""}
        onClick={() => onWordClick(w.start_ms)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === "Enter" && onWordClick(w.start_ms)}
      >
        {text.slice(w.char_start, w.char_end)}
      </span>
    );
    cursor = w.char_end;
  });
  if (cursor < text.length) {
    parts.push(<span key="tail">{text.slice(cursor)}</span>);
  }

  return (
    <div className="synced-text" ref={containerRef}>
      <p>{parts}</p>
      <style>{`
        .synced-text {
          overflow-y: auto;
          max-height: 100%;
          padding: 1.5rem;
          line-height: 1.8;
          font-size: 1.1rem;
        }
        .synced-text span[role="button"] {
          cursor: pointer;
        }
        .synced-text span[role="button"]:hover {
          text-decoration: underline;
          text-decoration-color: var(--accent-dim);
        }
      `}</style>
    </div>
  );
}
