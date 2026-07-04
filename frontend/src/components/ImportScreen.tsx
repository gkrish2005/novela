import { useState } from "react";
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

  const handleFile = async (file: File) => {
    setLoading(true);
    setError("");
    try {
      const lang = language === "auto" ? undefined : language;
      const result = await api.importFile(file, lang);
      setDetected(result.detected_language);
      onImported(result.book_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Import failed");
    } finally {
      setLoading(false);
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
