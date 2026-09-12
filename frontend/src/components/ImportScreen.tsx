import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";

type Props = {
  onImported: (bookId: number) => void;
};

export function ImportScreen({ onImported }: Props) {
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [language, setLanguage] = useState<"auto" | "en" | "hi">("auto");
  const [detected, setDetected] = useState<string | null>(null);

  const [voices, setVoices] = useState<string[]>([]);
  const [hindiPresets, setHindiPresets] = useState<{ id: string; name: string; description: string }[]>([]);
  const [selectedVoiceId, setSelectedVoiceId] = useState<string>("");
  const [selectedPresetId, setSelectedPresetId] = useState<string>("");
  const [previewingId, setPreviewingId] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    api.listVoices()
      .then((res) => {
        setVoices(res.voices);
        if (res.voices.length > 0) setSelectedVoiceId(res.voices[0]);
      })
      .catch(() => {});
    api.listHindiPresets()
      .then((res) => {
        setHindiPresets(res);
        if (res.length > 0) setSelectedPresetId(res[0].id);
      })
      .catch(() => {});
  }, []);

  const playPreview = (voiceId: string) => {
    if (previewingId === voiceId) {
      audioRef.current?.pause();
      setPreviewingId(null);
    } else {
      audioRef.current?.pause();
      const url = api.voicePreviewUrl(voiceId);
      const audio = new Audio(url);
      audio.onended = () => setPreviewingId(null);
      audioRef.current = audio;
      audio.play().catch(() => setPreviewingId(null));
      setPreviewingId(voiceId);
    }
  };

  useEffect(() => {
    return () => {
      audioRef.current?.pause();
    };
  }, []);

  const isTauriEnv = typeof window !== "undefined" && (window as any).__TAURI_INTERNALS__ !== undefined;

  const handleFile = async (file: File) => {
    setLoading(true);
    setError("");
    try {
      const lang = language === "auto" ? undefined : language;
      const vId = language !== "hi" ? selectedVoiceId : undefined;
      const vPrompt = language !== "en" ? selectedPresetId : undefined;
      const result = await api.importFile(file, lang, vId, vPrompt);
      setDetected(result.detected_language);
      onImported(result.book_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Import failed");
    } finally {
      setLoading(false);
    }
  };

  const handleLocalFile = async (path: string) => {
    setLoading(true);
    setError("");
    try {
      const lang = language === "auto" ? undefined : language;
      const vId = language !== "hi" ? selectedVoiceId : undefined;
      const vPrompt = language !== "en" ? selectedPresetId : undefined;
      const result = await api.importLocalFile(path, lang, vId, vPrompt);
      setDetected(result.detected_language);
      onImported(result.book_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Import failed");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!isTauriEnv) return;

    let active = true;
    let unlistenDrop: any = null;
    let unlistenOver: any = null;
    let unlistenLeave: any = null;

    import("@tauri-apps/api/event").then(({ listen }) => {
      if (!active) return;

      listen<any>("tauri://drag-drop", (event) => {
        setDragging(false);
        const filePath = event.payload.paths?.[0];
        if (filePath) {
          handleLocalFile(filePath);
        }
      }).then((fn) => { unlistenDrop = fn; });

      listen<any>("tauri://drag-over", () => {
        setDragging(true);
      }).then((fn) => { unlistenOver = fn; });

      listen<any>("tauri://drag-leave", () => {
        setDragging(false);
      }).then((fn) => { unlistenLeave = fn; });
    });

    return () => {
      active = false;
      if (unlistenDrop) unlistenDrop();
      if (unlistenOver) unlistenOver();
      if (unlistenLeave) unlistenLeave();
    };
  }, [language, selectedVoiceId, selectedPresetId]);


  const handleTauriFilePicker = async () => {
    try {
      const { open } = await import("@tauri-apps/plugin-dialog");
      const filePath = await open({
        multiple: false,
        filters: [
          {
            name: "Books",
            extensions: ["pdf", "epub", "txt", "docx", "md"]
          }
        ]
      });
      if (filePath && typeof filePath === "string") {
        await handleLocalFile(filePath);
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : typeof err === "string" ? err : JSON.stringify(err);
      setError(msg);
    }
  };


  return (
    <div className="import-screen">
      <div className="import-card">
        <h2 className="serif-title">Import a book</h2>
        <p className="import-copy">
          Novela detects English or Hindi automatically and narrates each in its own
          voice — it doesn&apos;t translate.
        </p>

        <div className="lang-toggle">
          <span className="lang-label">
            {detected
              ? `Detected: ${detected === "hi" ? "Hindi" : detected === "mixed" ? "Mixed" : "English"} — tap to correct`
              : "Language override (optional)"}
          </span>
          <div className="lang-buttons">
            {(["auto", "en", "hi"] as const).map((l) => (
              <button
                key={l}
                className={`lang-btn ${language === l ? "active" : ""}`}
                onClick={() => setLanguage(l)}
                title={l === "auto" ? "Use auto-detection" : `Force ${l === "en" ? "English" : "Hindi"}`}
              >
                {l === "auto" ? "Auto" : l === "en" ? "EN" : "HI"}
              </button>
            ))}
          </div>
        </div>

        {language !== "hi" && voices.length > 0 && (
          <div className="voice-field" style={{ marginBottom: "1.25rem" }}>
            <span className="lang-label">English voice</span>
            <div className="voice-picker-row" style={{ display: "flex", gap: "0.5rem" }}>
              <select
                value={selectedVoiceId}
                onChange={(e) => setSelectedVoiceId(e.target.value)}
                className="voice-select"
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
                {voices.map((v) => (
                  <option key={v} value={v}>
                    {v}
                  </option>
                ))}
              </select>
              <button
                type="button"
                className="btn-ghost"
                onClick={() => playPreview(selectedVoiceId)}
                style={{ padding: "0.5rem 0.75rem", fontSize: "0.85rem", whiteSpace: "nowrap" }}
              >
                {previewingId === selectedVoiceId ? "⏸ Stop" : "▶ Preview"}
              </button>
            </div>
          </div>
        )}

        {language !== "en" && hindiPresets.length > 0 && (
          <div className="voice-field" style={{ marginBottom: "1.5rem" }}>
            <span className="lang-label">Hindi voice preset</span>
            <select
              value={selectedPresetId}
              onChange={(e) => setSelectedPresetId(e.target.value)}
              className="voice-select"
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
              {hindiPresets.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
            <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)", display: "block", marginTop: "0.25rem" }}>
              {hindiPresets.find((p) => p.id === selectedPresetId)?.description}
            </span>
          </div>
        )}

        <div
          className={`drop-zone ${dragging ? "dragging" : ""}`}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            const file = e.dataTransfer.files[0];
            if (file) handleFile(file);
          }}
        >
          <p>Drop a PDF, TXT, EPUB, or DOCX here</p>
          {isTauriEnv ? (
            <button
              className="btn-primary file-label"
              disabled={loading}
              onClick={handleTauriFilePicker}
              style={{ display: "inline-block" }}
            >
              {loading ? "Importing…" : "Choose file"}
            </button>
          ) : (
            <label className="btn-primary file-label">
              {loading ? "Importing…" : "Choose file"}
              <input
                type="file"
                hidden
                accept=".pdf,.txt,.md,.epub,.docx"
                disabled={loading}
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFile(file);
                }}
              />
            </label>
          )}
        </div>


        {error && <p className="error">{error}</p>}
      </div>

      <style>{`
        .import-screen {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 2rem;
        }
        .import-card {
          max-width: 520px;
          width: 100%;
          background: var(--bg-card);
          border-radius: 12px;
          padding: 2rem;
          border: 1px solid var(--border);
        }
        .import-card h2 {
          margin: 0 0 0.75rem;
          font-size: 1.75rem;
        }
        .import-copy {
          color: var(--text-secondary);
          line-height: 1.5;
          margin: 0 0 1.5rem;
          font-size: 0.95rem;
        }
        .lang-toggle { margin-bottom: 1.5rem; }
        .lang-label {
          display: block;
          font-size: 0.8rem;
          color: var(--text-secondary);
          margin-bottom: 0.5rem;
        }
        .lang-buttons { display: flex; gap: 0.5rem; }
        .lang-btn {
          padding: 0.4rem 0.9rem;
          border-radius: 6px;
          border: 1px solid var(--border);
          color: var(--text-secondary);
        }
        .lang-btn.active {
          border-color: var(--accent);
          color: var(--accent);
        }
        .drop-zone {
          border: 2px dashed var(--border);
          border-radius: 10px;
          padding: 2.5rem 1.5rem;
          text-align: center;
          transition: border-color 0.15s;
        }
        .drop-zone.dragging { border-color: var(--accent); }
        .drop-zone p { color: var(--text-secondary); margin-bottom: 1rem; }
        .file-label { display: inline-block; cursor: pointer; }
        .error { color: #e07070; margin-top: 1rem; font-size: 0.9rem; }
      `}</style>
    </div>
  );
}
