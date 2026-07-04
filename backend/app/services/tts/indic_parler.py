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
DESCRIPTION = (
    "A female speaker with a clear, warm Hindi voice delivers the narration "
    "at a moderate pace in a quiet environment."
)


def _device() -> str:
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


def synthesize_hindi(text: str, output_path: Path) -> None:
    model, tokenizer, description_tokenizer = _load()
    device = _device()

    desc_ids = description_tokenizer(DESCRIPTION, return_tensors="pt").input_ids.to(device)
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
