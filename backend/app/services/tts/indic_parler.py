"""AI4Bharat Indic Parler-TTS for Hindi."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf
import torch

_model = None
_tokenizer = None
_description_tokenizer = None

MODEL_ID = "ai4bharat/indic-parler-tts"

HINDI_PRESETS = {
    "clear_warm_female": (
        "A female speaker with a clear, warm Hindi voice delivers the narration "
        "at a moderate pace in a quiet environment."
    ),
    "deep_expressive_male": (
        "A male speaker with a deep, expressive Hindi voice delivers the narration "
        "at a moderate pace in a quiet environment."
    ),
    "slow_soft_female": (
        "A female speaker with a soft, slow Hindi voice delivers the narration "
        "in a quiet environment."
    )
}

DEFAULT_DESCRIPTION = HINDI_PRESETS["clear_warm_female"]


def _device() -> str:
    import platform
    if platform.system() == "Darwin":
        return "cpu"
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def _load():
    global _model, _tokenizer, _description_tokenizer
    if _model is None:
        from parler_tts import ParlerTTSForConditionalGeneration
        from transformers import AutoTokenizer

        _model = ParlerTTSForConditionalGeneration.from_pretrained(MODEL_ID)
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        _description_tokenizer = AutoTokenizer.from_pretrained(_model.config.text_encoder._name_or_path)
        _model = _model.to(_device())
    return _model, _tokenizer, _description_tokenizer


def synthesize_hindi(text: str, output_path: Path, voice_prompt: str | None = None) -> None:
    model, tokenizer, description_tokenizer = _load()
    device = _device()

    prompt = HINDI_PRESETS.get(voice_prompt, voice_prompt) if voice_prompt else DEFAULT_DESCRIPTION
    desc_ids = description_tokenizer(prompt, return_tensors="pt").input_ids.to(device)
    prompt_ids = tokenizer(text, return_tensors="pt").input_ids.to(device)

    with torch.no_grad():
        generation = model.generate(input_ids=desc_ids, prompt_input_ids=prompt_ids)

    audio = generation.cpu().numpy().squeeze()
    if audio.ndim > 1:
        audio = audio[0]
    audio = np.asarray(audio, dtype=np.float32)
    sample_rate = model.config.sampling_rate

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(output_path), audio, sample_rate)
