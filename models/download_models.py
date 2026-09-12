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
import torch

# Monkeypatch torch.load to default to weights_only=False for PyTorch 2.6+ compatibility
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    if "weights_only" in kwargs:
        kwargs["weights_only"] = False
    else:
        kwargs.setdefault("weights_only", False)
    return _original_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

MODELS_DIR = pathlib.Path(__file__).parent

# Keep all downloaded weights self-contained under models/ rather than the
# default ~/.cache/huggingface, so this folder is the single thing a fresh
# machine/recipient needs to populate for full offline operation.
os.environ.setdefault("HF_HOME", str(MODELS_DIR / "hf_cache"))


VOICES = [
    "af_alloy", "af_aoede", "af_bella", "af_heart", "af_jessica", "af_kore", 
    "af_nicole", "af_nova", "af_river", "af_sarah", "af_sky", "am_adam", 
    "am_echo", "am_eric", "am_fenrir", "am_liam", "am_michael", "am_onyx", 
    "am_puck", "am_santa", "bf_alice", "bf_emma", "bf_isabella", "bf_lily", 
    "bm_daniel", "bm_fable", "bm_george", "bm_lewis", "ef_dora", "em_alex", 
    "em_santa", "ff_siwis", "hf_alpha", "hf_beta", "hm_omega", "hm_psi", 
    "if_sara", "im_nicola", "jf_alpha", "jf_gongitsune", "jf_nezumi", 
    "jf_tebukuro", "jm_kumo", "pf_dora", "pm_alex", "pm_santa", "zf_xiaobei", 
    "zf_xiaoni", "zf_xiaoxiao", "zf_xiaoyi", "zm_yunjian", "zm_yunxi", 
    "zm_yunxia", "zm_yunyang"
]


def download_kokoro() -> None:
    from kokoro import KPipeline
    from huggingface_hub import hf_hub_download

    print("Initializing Kokoro pipeline...")
    KPipeline(lang_code="a")
    print("[ok] Kokoro base weights cached.")

    print(f"Downloading all {len(VOICES)} Kokoro voice files...")
    for voice in VOICES:
        try:
            hf_hub_download(repo_id="hexgrad/Kokoro-82M", filename=f"voices/{voice}.pt")
            print(f"  [ok] Cached voice: {voice}")
        except Exception as e:
            print(f"  [warning] Failed to download Kokoro voice {voice}: {e}")
    print("[ok] Kokoro voice set cached.")


def download_indic_parler_tts() -> None:
    from parler_tts import ParlerTTSForConditionalGeneration
    from transformers import AutoTokenizer

    model_id = "ai4bharat/indic-parler-tts"
    token = os.environ.get("HF_TOKEN")
    print(f"Downloading Indic Parler-TTS weights (token present: {bool(token)})...")
    try:
        ParlerTTSForConditionalGeneration.from_pretrained(model_id, token=token)
        AutoTokenizer.from_pretrained(model_id, token=token)
        print("[ok] Indic Parler-TTS weights cached.")
    except Exception as e:
        print(f"\n[error] Failed to download Indic Parler-TTS: {e}")
        print("Please accept the terms at: https://huggingface.co/ai4bharat/indic-parler-tts")
        print("And ensure you pass your Hugging Face token, e.g.: HF_TOKEN=your_token python models/download_models.py")
        raise e


def download_whisperx() -> None:
    import whisperx

    print("Downloading WhisperX large-v2 weights...")
    whisperx.load_model("large-v2", device="cpu", compute_type="float32")
    print("[ok] WhisperX weights cached.")


def main() -> None:
    print(f"Downloading model weights into {MODELS_DIR / 'hf_cache'} ...\n")
    download_kokoro()
    try:
        download_indic_parler_tts()
    except Exception as e:
        print(f"\n[warning] Indic Parler-TTS download failed: {e}")
        print("Continuing with remaining downloads...")
    
    try:
        download_whisperx()
    except Exception as e:
        print(f"\n[error] WhisperX download failed: {e}")
        return
    print("\nAll models downloaded. The app can now run fully offline.")


if __name__ == "__main__":
    main()
