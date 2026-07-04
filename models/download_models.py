"""
One-time model download for Novela.

Downloads TTS + alignment weights into models/ so the app can run fully
offline afterward. See docs/PRD.md section 9 for the offline-capability
breakdown.

All three models below are PUBLIC, non-gated Hugging Face models — no account
or access token is required. Weights are fetched automatically the first time
each library's from_pretrained()/pipeline call runs; setting HF_HOME below
keeps everything self-contained under models/ instead of the default
~/.cache/huggingface, so this folder alone is what needs to exist for the app
to work fully offline afterward.

Real package/model sources (confirmed):
  - Kokoro (English, also has thinner Hindi coverage via lang_code='h')
      pip install kokoro>=0.9.4 soundfile
      requires the system package espeak-ng (brew install espeak-ng on macOS)
  - AI4Bharat Indic Parler-TTS (Hindi default)
      pip install git+https://github.com/huggingface/parler-tts.git
      model id: ai4bharat/indic-parler-tts
  - WhisperX (alignment, both languages)
      pip install whisperx
"""

import os
import pathlib

MODELS_DIR = pathlib.Path(__file__).parent

# Keep all downloaded weights self-contained under models/ rather than the
# default ~/.cache/huggingface, so this folder is the single thing a fresh
# machine/recipient needs to populate for full offline operation.
os.environ.setdefault("HF_HOME", str(MODELS_DIR / "hf_cache"))


def download_kokoro() -> None:
    from kokoro import KPipeline  # noqa: F401  (import triggers weight download)

    KPipeline(lang_code="a")  # American English voicepack
    print("[ok] Kokoro weights cached.")


def download_indic_parler_tts() -> None:
    from parler_tts import ParlerTTSForConditionalGeneration
    from transformers import AutoTokenizer

    model_id = "ai4bharat/indic-parler-tts"
    ParlerTTSForConditionalGeneration.from_pretrained(model_id)
    AutoTokenizer.from_pretrained(model_id)
    print("[ok] Indic Parler-TTS weights cached.")


def download_whisperx() -> None:
    import whisperx

    whisperx.load_model("large-v2", device="cpu")  # swap device at runtime
    print("[ok] WhisperX weights cached.")


def main() -> None:
    print(f"Downloading model weights into {MODELS_DIR / 'hf_cache'} ...\n")
    download_kokoro()
    download_indic_parler_tts()
    download_whisperx()
    print("\nAll models downloaded. The app can now run fully offline.")


if __name__ == "__main__":
    main()
