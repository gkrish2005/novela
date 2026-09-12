import { useEffect, useRef, useState } from "react";
import { api, Book, Chapter } from "../api/client";
import { usePlayback } from "../hooks/usePlayback";
import { ChapterOverlay } from "./ChapterOverlay";
import { SyncedText } from "./SyncedText";

type Props = {
  book: Book;
  onRefresh: () => void;
};

export function BookView({ book, onRefresh }: Props) {
  const [chapter, setChapter] = useState<Chapter | null>(
    book.chapters.find((c) => c.status === "ready") ?? book.chapters[0] ?? null
  );
  const [speed, setSpeed] = useState(1);
  const [jobId, setJobId] = useState<number | null>(null);
  const [jobStatus, setJobStatus] = useState("");
  const [exporting, setExporting] = useState(false);
  const [showChapters, setShowChapters] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  const [voices, setVoices] = useState<string[]>([]);
  const [hindiPresets, setHindiPresets] = useState<{ id: string; name: string; description: string }[]>([]);
  const [selectedVoiceId, setSelectedVoiceId] = useState("");
  const [selectedPresetId, setSelectedPresetId] = useState("");
  const [lang, setLang] = useState<string>("");
  const [previewingId, setPreviewingId] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    api.listVoices().then((res) => setVoices(res.voices)).catch(() => {});
    api.listHindiPresets().then((res) => setHindiPresets(res)).catch(() => {});
  }, []);

  useEffect(() => {
    if (book) {
      setLang(book.language);
      setSelectedVoiceId(book.voice_id || "");
      setSelectedPresetId(book.voice_prompt || "");
    }
  }, [book, showSettings]);

  useEffect(() => {
    return () => {
      audioRef.current?.pause();
    };
  }, []);

  const pb = usePlayback({
    book,
    chapter,
    speed,
    onSpeedChange: setSpeed,
    onChapterChange: setChapter,
  });

  useEffect(() => {
    setChapter(book.chapters.find((c) => c.status === "ready") ?? book.chapters[0] ?? null);
  }, [book.id]);

  useEffect(() => {
    if (!jobId) return;
    const interval = setInterval(async () => {
      const job = await api.getJob(jobId);
      setJobStatus(`${job.status}: ${job.message} (${Math.round(job.progress)}%)`);
      if (job.status === "done" || job.status === "error") {
        clearInterval(interval);
        setJobId(null);
        onRefresh();
      }
    }, 1500);
    return () => clearInterval(interval);
  }, [jobId]);

  const startNarration = async () => {
    const job = await api.narrate(book.id);
    setJobId(job.id);
    setJobStatus("Starting…");
  };

  const exportBook = async (fmt: "m4b" | "mp3") => {
    setExporting(true);
    try {
      const result = await api.exportBook(book.id, fmt);
      alert(`Exported to:\n${result.path}`);
    } catch (e) {
      alert(e instanceof Error ? e.message : "Export failed");
    } finally {
      setExporting(false);
    }
  };

  const readyCount = book.chapters.filter((c) => c.status === "ready").length;
  const langLabel = book.language === "hi" ? "Hindi" : book.language === "mixed" ? "Mixed" : "English";

  return (
    <div className="book-view">
      <header className="book-header">
        <img className="book-cover" src={api.coverUrl(book.id)} alt="" />
        <div>
          <h1 className="serif-title">{book.title}</h1>
          {book.author && <p className="author">{book.author}</p>}
          <p className="meta">
            {langLabel} · {book.chapters.length} chapters
            {readyCount > 0 && ` · ${readyCount} narrated`}
          </p>
          <div className="actions">
            <button className="btn-primary" onClick={startNarration} disabled={!!jobId}>
              {jobId ? "Narrating…" : readyCount > 0 ? "Re-narrate" : "Generate narration"}
            </button>
            <button className="btn-ghost" onClick={() => setShowSettings(true)}>
              Settings
            </button>
            {readyCount > 0 && (
              <>
                <button className="btn-ghost" onClick={() => setShowChapters(true)}>
                  Chapters
                </button>
                <button className="btn-ghost" disabled={exporting} onClick={() => exportBook("m4b")}>
                  Export .m4b
                </button>
                <button className="btn-ghost" disabled={exporting} onClick={() => exportBook("mp3")}>
                  Export .mp3
                </button>
              </>
            )}
          </div>
          {jobStatus && <p className="job-status">{jobStatus}</p>}
        </div>
      </header>

      {chapter?.status === "ready" && (
        <div className="reader">
          <div className="chapter-tabs">
            {book.chapters.map((ch) => (
              <button
                key={ch.id}
                className={`ch-tab ${ch.id === chapter.id ? "active" : ""} ${ch.status !== "ready" ? "disabled" : ""}`}
                disabled={ch.status !== "ready"}
                onClick={() => setChapter(ch)}
              >
                {ch.title}
              </button>
            ))}
          </div>

          <SyncedText
            text={pb.text}
            words={pb.words}
            activeWordIdx={pb.activeWordIdx}
            onWordClick={pb.seek}
          />

          <div className="inline-controls">
            <button onClick={pb.togglePlay}>{pb.playing ? "Pause" : "Play"}</button>
            <span>{pb.formatTime(pb.currentMs)} / {pb.formatTime(pb.durationMs)}</span>
            {pb.SPEED_PRESETS.map((s) => (
              <button
                key={s}
                className={speed === s ? "active" : ""}
                onClick={() => setSpeed(s)}
              >
                {s}x
              </button>
            ))}
          </div>
        </div>
      )}
      <ChapterOverlay
        open={showChapters}
        chapters={book.chapters}
        activeChapterId={chapter?.id ?? null}
        onClose={() => setShowChapters(false)}
        onSelectReady={(ch) => {
          setChapter(ch);
          setShowChapters(false);
        }}
        onPrioritizePending={async (ch) => {
          const job = await api.prioritizeChapter(ch.id);
          setJobId(job.id);
          setJobStatus("Queued selected chapter next");
          setShowChapters(false);
        }}
      />

      {showSettings && (
        <div className="chapter-overlay-backdrop" onClick={() => setShowSettings(false)}>
          <div className="chapter-overlay" onClick={(e) => e.stopPropagation()} style={{ padding: "1.25rem" }}>
            <div className="chapter-overlay-header" style={{ padding: "0 0 1rem 0" }}>
              <h3>Book Settings</h3>
              <button onClick={() => setShowSettings(false)}>✕</button>
            </div>
            
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem", marginTop: "0.5rem" }}>
              <div>
                <span className="lang-label" style={{ display: "block", marginBottom: "0.5rem" }}>Language</span>
                <select
                  value={lang}
                  onChange={(e) => setLang(e.target.value)}
                  style={{
                    width: "100%",
                    background: "var(--bg-app)",
                    border: "1px solid var(--border)",
                    borderRadius: "6px",
                    color: "var(--text-primary)",
                    padding: "0.5rem",
                    fontFamily: "inherit"
                  }}
                >
                  <option value="auto">Auto-detect</option>
                  <option value="en">English</option>
                  <option value="hi">Hindi</option>
                  <option value="mixed">Mixed</option>
                </select>
              </div>

              {lang !== "hi" && voices.length > 0 && (
                <div>
                  <span className="lang-label" style={{ display: "block", marginBottom: "0.5rem" }}>English voice</span>
                  <div style={{ display: "flex", gap: "0.5rem" }}>
                    <select
                      value={selectedVoiceId}
                      onChange={(e) => setSelectedVoiceId(e.target.value)}
                      style={{
                        flex: 1,
                        background: "var(--bg-app)",
                        border: "1px solid var(--border)",
                        borderRadius: "6px",
                        color: "var(--text-primary)",
                        padding: "0.5rem",
                        fontFamily: "inherit"
                      }}
                    >
                      <option value="">(None - Default af_heart)</option>
                      {voices.map((v) => (
                        <option key={v} value={v}>
                          {v}
                        </option>
                      ))}
                    </select>
                    <button
                      type="button"
                      className="btn-ghost"
                      onClick={() => {
                        if (!selectedVoiceId) return;
                        if (previewingId === selectedVoiceId) {
                          audioRef.current?.pause();
                          setPreviewingId(null);
                        } else {
                          audioRef.current?.pause();
                          const url = api.voicePreviewUrl(selectedVoiceId);
                          const audio = new Audio(url);
                          audio.onended = () => setPreviewingId(null);
                          audioRef.current = audio;
                          audio.play().catch(() => setPreviewingId(null));
                          setPreviewingId(selectedVoiceId);
                        }
                      }}
                      disabled={!selectedVoiceId}
                      style={{ padding: "0.5rem 0.75rem", fontSize: "0.85rem", whiteSpace: "nowrap" }}
                    >
                      {previewingId === selectedVoiceId ? "⏸ Stop" : "▶ Preview"}
                    </button>
                  </div>
                </div>
              )}

              {lang !== "en" && hindiPresets.length > 0 && (
                <div>
                  <span className="lang-label" style={{ display: "block", marginBottom: "0.5rem" }}>Hindi voice preset</span>
                  <select
                    value={selectedPresetId}
                    onChange={(e) => setSelectedPresetId(e.target.value)}
                    style={{
                      width: "100%",
                      background: "var(--bg-app)",
                      border: "1px solid var(--border)",
                      borderRadius: "6px",
                      color: "var(--text-primary)",
                      padding: "0.5rem",
                      fontFamily: "inherit"
                    }}
                  >
                    <option value="">(None - Default clear_warm_female)</option>
                    {hindiPresets.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name}
                      </option>
                    ))}
                  </select>
                  {selectedPresetId && (
                    <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)", display: "block", marginTop: "0.25rem" }}>
                      {hindiPresets.find((p) => p.id === selectedPresetId)?.description}
                    </span>
                  )}
                </div>
              )}

              <div style={{ marginTop: "1rem", display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
                <button className="btn-ghost" onClick={() => setShowSettings(false)}>
                  Cancel
                </button>
                <button
                  className="btn-primary"
                  onClick={async () => {
                    const voiceChanged =
                      lang !== book.language ||
                      selectedVoiceId !== (book.voice_id || "") ||
                      selectedPresetId !== (book.voice_prompt || "");

                    if (voiceChanged && readyCount > 0) {
                      const confirm = window.confirm(
                        "This will re-narrate already-generated chapters in the new voice — continue?"
                      );
                      if (!confirm) return;
                    }

                    await api.updateBook(book.id, {
                      language: lang,
                      voice_id: selectedVoiceId || null,
                      voice_prompt: selectedPresetId || null,
                    });
                    onRefresh();
                    setShowSettings(false);
                  }}
                >
                  Save
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .book-view { padding: 2rem; overflow-y: auto; flex: 1; }
        .book-header { display: flex; gap: 1.5rem; margin-bottom: 2rem; }
        .book-cover {
          width: 140px; height: 140px;
          border-radius: 8px; object-fit: cover;
          background: var(--bg-card);
        }
        .book-header h1 { margin: 0 0 0.25rem; font-size: 2rem; }
        .author { color: var(--text-secondary); margin: 0 0 0.5rem; }
        .meta { color: var(--text-muted); font-size: 0.9rem; margin: 0 0 1rem; }
        .actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }
        .job-status { font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.75rem; }
        .reader {
          background: var(--bg-card);
          border-radius: 12px;
          border: 1px solid var(--border);
          overflow: hidden;
        }
        .chapter-tabs {
          display: flex;
          gap: 0.25rem;
          padding: 0.75rem;
          border-bottom: 1px solid var(--border);
          overflow-x: auto;
        }
        .ch-tab {
          padding: 0.4rem 0.8rem;
          border-radius: 6px;
          font-size: 0.85rem;
          color: var(--text-secondary);
          white-space: nowrap;
        }
        .ch-tab.active { background: var(--bg-app); color: var(--accent); }
        .ch-tab.disabled { opacity: 0.4; }
        .inline-controls {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 1rem 1.5rem;
          border-top: 1px solid var(--border);
          font-size: 0.9rem;
        }
        .inline-controls button.active { color: var(--accent); }
      `}</style>
    </div>
  );
}
