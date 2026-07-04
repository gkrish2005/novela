const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8742";

export type Chapter = {
  id: number;
  book_id: number;
  index: number;
  title: string;
  audio_path: string | null;
  status: string;
  language: string;
  start_ms: number;
  duration_ms: number;
};

export type Book = {
  id: number;
  title: string;
  author: string | null;
  cover_path: string | null;
  cover_source: string;
  language: string;
  total_duration_ms: number;
  created_at: string;
  chapters: Chapter[];
};

export type Word = {
  word: string;
  start_ms: number;
  end_ms: number;
  char_start: number;
  char_end: number;
  language: string;
};

export type Job = {
  id: number;
  book_id: number;
  status: string;
  progress: number;
  message: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string }>("/health"),
  listBooks: () => request<Book[]>("/books"),
  getBook: (id: number) => request<Book>(`/books/${id}`),
  updateBookLanguage: (id: number, language: string) =>
    request<Book>(`/books/${id}?language=${language}`, { method: "PATCH" }),
  importFile: async (file: File, language?: string) => {
    const form = new FormData();
    form.append("file", file);
    if (language) form.append("language", language);
    return request<{ book_id: number; title: string; detected_language: string; chapter_count: number }>(
      "/import",
      { method: "POST", body: form }
    );
  },
  narrate: (bookId: number) => request<Job>(`/books/${bookId}/narrate`, { method: "POST" }),
  getJob: (jobId: number) => request<Job>(`/jobs/${jobId}`),
  getChapterWords: (chapterId: number) => request<Word[]>(`/chapters/${chapterId}/words`),
  getChapterText: (chapterId: number) => request<{ text: string }>(`/chapters/${chapterId}/text`),
  prioritizeChapter: (chapterId: number) => request<Job>(`/chapters/${chapterId}/prioritize`, { method: "POST" }),
  chapterAudioUrl: (chapterId: number) => `${API_BASE}/chapters/${chapterId}/audio`,
  coverUrl: (bookId: number) => `${API_BASE}/covers/${bookId}?t=${Date.now()}`,
  uploadCover: async (bookId: number, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<Book>(`/books/${bookId}/cover`, { method: "POST", body: form });
  },
  exportBook: (bookId: number, fmt: "m4b" | "mp3") =>
    request<{ path: string }>(`/books/${bookId}/export?fmt=${fmt}`, { method: "POST" }),
  getPlayback: (bookId: number) =>
    request<{ book_id: number; chapter_id: number | null; position_ms: number; speed: number }>(
      `/playback/${bookId}`
    ),
  savePlayback: (bookId: number, data: { chapter_id?: number; position_ms?: number; speed?: number }) => {
    const params = new URLSearchParams();
    if (data.chapter_id != null) params.set("chapter_id", String(data.chapter_id));
    if (data.position_ms != null) params.set("position_ms", String(data.position_ms));
    if (data.speed != null) params.set("speed", String(data.speed));
    return request(`/playback/${bookId}?${params}`, { method: "PUT" });
  },
};

export function formatTime(ms: number): string {
  const totalSec = Math.floor(ms / 1000);
  const m = Math.floor(totalSec / 60);
  const s = totalSec % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export const SPEED_PRESETS = [1, 1.25, 1.5, 1.75, 2] as const;
