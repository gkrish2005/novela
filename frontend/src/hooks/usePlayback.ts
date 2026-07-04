import { useCallback, useEffect, useRef, useState } from "react";
import { api, Book, Chapter, Word, SPEED_PRESETS, formatTime } from "../api/client";

type Props = {
  book: Book | null;
  chapter: Chapter | null;
  speed: number;
  onSpeedChange: (s: number) => void;
  onChapterChange: (ch: Chapter) => void;
  showSyncedText?: boolean;
  onSeek?: (ms: number) => void;
  externalSeekMs?: number | null;
};

export function usePlayback({
  book,
  chapter,
  speed,
  onSpeedChange,
  onChapterChange,
  externalSeekMs,
}: Props) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [playing, setPlaying] = useState(false);
  const [currentMs, setCurrentMs] = useState(0);
  const [durationMs, setDurationMs] = useState(0);
  const [words, setWords] = useState<Word[]>([]);
  const [text, setText] = useState("");
  const [activeWordIdx, setActiveWordIdx] = useState(-1);
  const rafRef = useRef<number>();

  useEffect(() => {
    if (!chapter) return;
    api.getChapterWords(chapter.id).then(setWords).catch(() => setWords([]));
    api.getChapterText(chapter.id).then((r) => setText(r.text)).catch(() => setText(""));
  }, [chapter?.id]);

  useEffect(() => {
    if (!chapter) return;
    const audio = new Audio(api.chapterAudioUrl(chapter.id));
    audio.preservesPitch = true;
    audio.playbackRate = speed;
    audioRef.current = audio;

    const onMeta = () => setDurationMs(audio.duration * 1000);
    const onEnded = () => {
      setPlaying(false);
      if (book) {
        const idx = book.chapters.findIndex((c) => c.id === chapter.id);
        const next = book.chapters[idx + 1];
        if (next?.status === "ready") onChapterChange(next);
      }
    };
    audio.addEventListener("loadedmetadata", onMeta);
    audio.addEventListener("ended", onEnded);
    audio.load();

    return () => {
      audio.pause();
      audio.removeEventListener("loadedmetadata", onMeta);
      audio.removeEventListener("ended", onEnded);
      audioRef.current = null;
    };
  }, [chapter?.id]);

  useEffect(() => {
    if (audioRef.current) audioRef.current.playbackRate = speed;
  }, [speed]);

  useEffect(() => {
    if (externalSeekMs != null && audioRef.current) {
      audioRef.current.currentTime = externalSeekMs / 1000;
      setCurrentMs(externalSeekMs);
    }
  }, [externalSeekMs]);

  const tick = useCallback(() => {
    const audio = audioRef.current;
    if (audio) {
      const ms = audio.currentTime * 1000;
      setCurrentMs(ms);
      const idx = words.findIndex((w) => ms >= w.start_ms && ms < w.end_ms);
      setActiveWordIdx(idx);
    }
    rafRef.current = requestAnimationFrame(tick);
  }, [words]);

  useEffect(() => {
    if (playing) {
      rafRef.current = requestAnimationFrame(tick);
    }
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [playing, tick]);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (playing) {
      audio.pause();
      setPlaying(false);
    } else {
      audio.play().then(() => setPlaying(true)).catch(console.error);
    }
  };

  const seek = (ms: number) => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.currentTime = ms / 1000;
    setCurrentMs(ms);
  };

  const skip = (deltaMs: number) => seek(Math.max(0, currentMs + deltaMs));

  const prevChapter = () => {
    if (!book || !chapter) return;
    const idx = book.chapters.findIndex((c) => c.id === chapter.id);
    if (idx > 0) onChapterChange(book.chapters[idx - 1]);
  };

  const nextChapter = () => {
    if (!book || !chapter) return;
    const idx = book.chapters.findIndex((c) => c.id === chapter.id);
    if (idx < book.chapters.length - 1) onChapterChange(book.chapters[idx + 1]);
  };

  const fineSpeed = (delta: number) => {
    const next = Math.min(3, Math.max(0.5, Math.round((speed + delta) * 100) / 100));
    onSpeedChange(next);
  };

  return {
    playing,
    currentMs,
    durationMs,
    words,
    text,
    activeWordIdx,
    togglePlay,
    seek,
    skip,
    prevChapter,
    nextChapter,
    fineSpeed,
    formatTime,
    SPEED_PRESETS,
  };
}
