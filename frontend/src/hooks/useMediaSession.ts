import { useEffect } from "react";
import { Book, Chapter } from "../api/client";

export function useMediaSession(
  book: Book | null,
  chapter: Chapter | null,
  playing: boolean,
  onPlay: () => void,
  onPause: () => void,
  onNext: () => void,
  onPrev: () => void
) {
  useEffect(() => {
    if (!book || !chapter || !("mediaSession" in navigator)) return;

    navigator.mediaSession.metadata = new MediaMetadata({
      title: chapter.title,
      artist: book.author ?? "Novela",
      album: book.title,
    });

    navigator.mediaSession.setActionHandler("play", onPlay);
    navigator.mediaSession.setActionHandler("pause", onPause);
    navigator.mediaSession.setActionHandler("previoustrack", onPrev);
    navigator.mediaSession.setActionHandler("nexttrack", onNext);

    return () => {
      navigator.mediaSession.setActionHandler("play", null);
      navigator.mediaSession.setActionHandler("pause", null);
      navigator.mediaSession.setActionHandler("previoustrack", null);
      navigator.mediaSession.setActionHandler("nexttrack", null);
    };
  }, [book?.id, chapter?.id, onPlay, onPause, onNext, onPrev]);

  useEffect(() => {
    if (!("mediaSession" in navigator)) return;
    navigator.mediaSession.playbackState = playing ? "playing" : "paused";
  }, [playing]);
}
