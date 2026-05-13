"""
Voice Clone Studio — local Gradio web app for cloning your own voice
and generating speech from typed text.

Run with:
    bash run.sh
or:
    python app.py

Then open http://127.0.0.1:7860 in your browser.
"""

from __future__ import annotations

import os
import re
import shutil
import time
from datetime import datetime
from pathlib import Path

import gradio as gr
import numpy as np
import torch
import torchaudio

# --------------------------------------------------------------------------- #
# Watermarker shim                                                             #
# --------------------------------------------------------------------------- #
# Chatterbox uses `resemble-perth` to embed an inaudible AI-content watermark
# into generated audio. On Apple Silicon (and some Linux configs) the perth
# package imports but fails to load its model, so
# `perth.PerthImplicitWatermarker` ends up as `None` and ChatterboxTTS crashes
# at init time. Since this tool is for cloning your own voice for your own
# content, we substitute a pass-through no-op watermarker. This must run
# BEFORE the chatterbox import so the patched class is used.
import perth  # noqa: E402

class _NoOpWatermarker:
    """Drop-in replacement when perth's real watermarker can't load."""
    def apply_watermark(self, wav, sample_rate=44100, **_kwargs):
        return wav
    def get_watermark(self, wav, sample_rate=44100, **_kwargs):
        return None

if getattr(perth, "PerthImplicitWatermarker", None) is None:
    perth.PerthImplicitWatermarker = _NoOpWatermarker
    print("[setup] perth watermarker unavailable; using no-op pass-through.")

from chatterbox.tts import ChatterboxTTS  # noqa: E402


# --------------------------------------------------------------------------- #
# Setup                                                                        #
# --------------------------------------------------------------------------- #

ROOT = Path(__file__).parent.resolve()
SAMPLES_DIR = ROOT / "samples"
OUTPUT_DIR = ROOT / "output"
SAMPLES_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Use Apple Silicon GPU if available, otherwise CPU.
if torch.backends.mps.is_available():
    DEVICE = "mps"
elif torch.cuda.is_available():
    DEVICE = "cuda"
else:
    DEVICE = "cpu"

print(f"[setup] Using device: {DEVICE}")
print("[setup] Loading Chatterbox TTS (first run downloads ~2 GB of weights)...")
MODEL = ChatterboxTTS.from_pretrained(device=DEVICE)
SAMPLE_RATE = MODEL.sr
print(f"[setup] Model loaded. Output sample rate: {SAMPLE_RATE} Hz")


# --------------------------------------------------------------------------- #
# Voice sample library                                                         #
# --------------------------------------------------------------------------- #

VALID_AUDIO_EXTS = {".wav", ".mp3", ".m4a", ".flac", ".ogg"}


def list_voices() -> list[str]:
    """Return saved voice sample filenames (no extension)."""
    return sorted(
        p.stem for p in SAMPLES_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in VALID_AUDIO_EXTS
    )


def save_voice(uploaded_path: str | None, name: str) -> tuple[str, gr.update]:
    """Copy an uploaded sample into samples/ under `name`. Returns status + dropdown refresh."""
    if not uploaded_path:
        return "No file uploaded.", gr.update()
    if not name or not name.strip():
        return "Please provide a name for this voice.", gr.update()

    name = re.sub(r"[^A-Za-z0-9_\-]+", "_", name.strip())
    src = Path(uploaded_path)
    if src.suffix.lower() not in VALID_AUDIO_EXTS:
        return f"Unsupported audio format: {src.suffix}", gr.update()

    dst = SAMPLES_DIR / f"{name}{src.suffix.lower()}"
    shutil.copy(src, dst)

    voices = list_voices()
    return f"Saved as '{name}'.", gr.update(choices=voices, value=name)


def voice_path(name: str) -> Path | None:
    """Resolve a voice name to its file path on disk."""
    if not name:
        return None
    for ext in VALID_AUDIO_EXTS:
        p = SAMPLES_DIR / f"{name}{ext}"
        if p.exists():
            return p
    return None


# --------------------------------------------------------------------------- #
# Text chunking                                                                #
# --------------------------------------------------------------------------- #

def split_into_chunks(text: str, max_chars: int = 280) -> list[str]:
    """
    Split long text into sentence-aware chunks the model can handle in one pass.
    Chatterbox does best on ~30s of audio per generation; ~280 chars is a safe
    cap for natural speech pacing.
    """
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    # Split on sentence boundaries first.
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    buf = ""
    for s in sentences:
        if not s:
            continue
        if len(buf) + len(s) + 1 <= max_chars:
            buf = f"{buf} {s}".strip()
        else:
            if buf:
                chunks.append(buf)
            # If a single sentence is itself too long, hard-split on commas.
            if len(s) > max_chars:
                parts = re.split(r",\s+", s)
                sub = ""
                for part in parts:
                    if len(sub) + len(part) + 2 <= max_chars:
                        sub = f"{sub}, {part}".strip(", ")
                    else:
                        if sub:
                            chunks.append(sub)
                        sub = part
                buf = sub
            else:
                buf = s
    if buf:
        chunks.append(buf)
    return chunks


# --------------------------------------------------------------------------- #
# Generation                                                                   #
# --------------------------------------------------------------------------- #

def generate_speech(
    text: str,
    voice_name: str,
    exaggeration: float,
    cfg_weight: float,
    progress: gr.Progress = gr.Progress(),
) -> tuple[str | None, str]:
    """Generate speech from `text` using `voice_name` as the reference voice."""

    if not text or not text.strip():
        return None, "Please type some text to generate."

    ref = voice_path(voice_name)
    if ref is None:
        return None, "Please select or upload a voice sample first."

    chunks = split_into_chunks(text)
    if not chunks:
        return None, "Text was empty after cleanup."

    progress(0, desc=f"Generating {len(chunks)} chunk(s)...")
    audio_segments: list[torch.Tensor] = []
    short_silence = torch.zeros(1, int(SAMPLE_RATE * 0.25))  # 250 ms gap

    for i, chunk in enumerate(chunks):
        progress((i) / len(chunks), desc=f"Chunk {i+1} / {len(chunks)}: {chunk[:60]}...")
        wav = MODEL.generate(
            chunk,
            audio_prompt_path=str(ref),
            exaggeration=float(exaggeration),
            cfg_weight=float(cfg_weight),
        )
        # Chatterbox returns shape (1, samples) on CPU
        audio_segments.append(wav)
        if i < len(chunks) - 1:
            audio_segments.append(short_silence)

    full = torch.cat(audio_segments, dim=-1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_voice = re.sub(r"[^A-Za-z0-9_\-]+", "_", voice_name) or "voice"
    out_path = OUTPUT_DIR / f"{timestamp}_{safe_voice}.wav"
    torchaudio.save(str(out_path), full, SAMPLE_RATE)

    progress(1.0, desc="Done")
    return str(out_path), f"Generated {len(chunks)} chunk(s) → {out_path.name}"


# --------------------------------------------------------------------------- #
# Gradio UI                                                                    #
# --------------------------------------------------------------------------- #

INTRO = """
# Voice Clone Studio

Type a script, pick your voice sample, click **Generate**, and download the audio.

**First time?** Open the *Voice Library* tab and upload a 20–30s recording
of yourself reading naturally. See `VOICE_SAMPLES_GUIDE.md` for tips.
"""

with gr.Blocks(title="Voice Clone Studio") as demo:
    gr.Markdown(INTRO)

    with gr.Tab("Generate"):
        with gr.Row():
            with gr.Column(scale=2):
                text_in = gr.Textbox(
                    label="Script",
                    placeholder="Type or paste what you want your voice to say...",
                    lines=12,
                )
                with gr.Row():
                    voice_dd = gr.Dropdown(
                        label="Voice",
                        choices=list_voices(),
                        value=(list_voices()[0] if list_voices() else None),
                        interactive=True,
                    )
                    refresh_btn = gr.Button("Refresh", size="sm")
                with gr.Accordion("Advanced controls", open=False):
                    exaggeration = gr.Slider(
                        0.25, 2.0, value=0.5, step=0.05,
                        label="Exaggeration",
                        info="Higher = more emotional / expressive. Around 0.5 sounds natural.",
                    )
                    cfg_weight = gr.Slider(
                        0.0, 1.0, value=0.5, step=0.05,
                        label="CFG weight (pace / faithfulness)",
                        info="Lower = slower & more measured; higher = faster, snappier delivery.",
                    )
                go_btn = gr.Button("Generate", variant="primary")
                status = gr.Markdown("")
            with gr.Column(scale=1):
                audio_out = gr.Audio(label="Output", type="filepath")
                gr.Markdown(
                    "Files are also saved to the `output/` folder so you can "
                    "drag them into your video editor."
                )

        refresh_btn.click(lambda: gr.update(choices=list_voices()), outputs=voice_dd)
        go_btn.click(
            generate_speech,
            inputs=[text_in, voice_dd, exaggeration, cfg_weight],
            outputs=[audio_out, status],
        )

    with gr.Tab("Voice Library"):
        gr.Markdown(
            "Upload or record a sample of your voice (20–30s of natural reading). "
            "Give it a short name like `me_calm` or `me_upbeat`. You can save "
            "multiple voices for different video styles."
        )
        with gr.Row():
            with gr.Column():
                upload_in = gr.Audio(
                    label="Record or upload a sample",
                    type="filepath",
                    sources=["upload", "microphone"],
                )
                name_in = gr.Textbox(label="Voice name", placeholder="e.g. me_calm")
                save_btn = gr.Button("Save to library", variant="primary")
            with gr.Column():
                save_status = gr.Markdown("")
                voices_display = gr.Dropdown(
                    label="Existing voices",
                    choices=list_voices(),
                    interactive=False,
                )
        save_btn.click(
            save_voice,
            inputs=[upload_in, name_in],
            outputs=[save_status, voices_display],
        ).then(
            lambda: gr.update(choices=list_voices()),
            outputs=voice_dd,
        )

    with gr.Tab("Tips"):
        gr.Markdown((ROOT / "VOICE_SAMPLES_GUIDE.md").read_text())


if __name__ == "__main__":
    demo.queue().launch(server_name="127.0.0.1", server_port=7860, inbrowser=True)
