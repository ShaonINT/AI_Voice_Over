# Voice Clone Studio

A local, browser-based tool to generate speech in your own voice from typed text.
Built for a Mac (Apple Silicon) using open-source models. No subscriptions, no
data leaves your machine.

## What it does

1. You record a short sample of your own voice (one-time, ~20 seconds).
2. You type or paste a script into a web page.
3. The tool generates an audio file that sounds like you reading it.
4. You download the audio and drop it into your YouTube video editor.

## What's under the hood

- **Chatterbox TTS** by Resemble AI — MIT-licensed, so audio you generate can be
  used in monetized YouTube videos. Voice cloning works from a single short
  reference sample.
- **Gradio** — gives the tool a simple web UI in your browser.
- **PyTorch with MPS** — runs the model on your Mac's Apple Silicon GPU, so
  generation is fast.

## First-time setup

You only do this once. Open Terminal, then:

```bash
cd "/Users/shaonbiswas/Documents/Python Projects/Voice Clone"
bash setup.sh
```

The script will:
- Install Homebrew if missing
- Install `ffmpeg` (audio processing) and Python 3.11
- Create a Python virtual environment in `.venv/`
- Install Chatterbox, Gradio, and PyTorch
- Print "Setup complete" when finished

First run downloads about 2 GB of model weights. Subsequent runs are instant.

## Daily use

```bash
cd "/Users/shaonbiswas/Documents/Python Projects/Voice Clone"
bash run.sh
```

That opens the web UI at http://127.0.0.1:7860 in your browser. Leave the
Terminal window open while you use it; close it (Ctrl+C) when you're done.

## Recording your voice sample

This is the single most important quality factor. Read
[VOICE_SAMPLES_GUIDE.md](VOICE_SAMPLES_GUIDE.md) before you record.

Short version: 20–30 seconds of you reading naturally, in a quiet room, into
any decent microphone (even an iPhone is fine), saved as a WAV or MP3.

## Folders

- `samples/` — your reference voice recordings live here
- `output/` — generated audio gets written here
- `app.py` — the web app
- `setup.sh` / `run.sh` — installer and launcher

## Ethics note

Only clone your own voice, or someone who has explicitly given you written
permission. YouTube's rules require you to disclose meaningfully altered
synthetic content in some categories — check their current policy before
uploading.
