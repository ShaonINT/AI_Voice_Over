# Voice Clone Studio

**Generate YouTube voiceovers in your own voice from typed text — locally, on your Mac, for free.**

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Platform: macOS Apple Silicon](https://img.shields.io/badge/platform-macOS%20Apple%20Silicon-lightgrey.svg)
![Engine: Chatterbox TTS](https://img.shields.io/badge/engine-Chatterbox%20TTS-orange.svg)
![Status: Working](https://img.shields.io/badge/status-working-success.svg)

![Voice Clone Studio interface](docs/screenshot.svg)

## What it does

Voice Clone Studio is a self-hosted web app that learns the sound of your voice from a single short recording, then reads any text you type back to you in that voice. It's designed for YouTube creators who don't enjoy speaking on camera, want a consistent narration voice across videos, or need to produce voiceovers faster than recording manually.

Everything runs on your own computer. No API keys, no usage limits, no subscription. The audio it generates is licensed for commercial use, including monetized YouTube content.

![alt text](screenshot.png)

## Highlights

- **One reference sample, unlimited output.** Record yourself reading naturally for 20–30 seconds. After that, type anything and hear it in your voice.
- **Long scripts work.** The app auto-chunks your text into sentence-sized pieces, generates each, and stitches them together with natural pauses. A 5-minute video script is fine.
- **Voice library.** Save multiple versions of your voice — calm explainer, upbeat host, dramatic narrator — and switch between them per project.
- **Tunable delivery.** Expressiveness and pacing sliders let you push the same voice toward warmer, snappier, or more measured.
- **Local and private.** No audio leaves your machine. Your reference samples never touch a server.
- **Commercial-friendly.** Built on Chatterbox TTS (MIT license). Use the generated audio in monetized videos without legal worry.

## Requirements

- Mac with Apple Silicon (M1, M2, M3, or M4 chip)
- macOS 13 (Ventura) or newer
- About 4 GB of free disk space (model weights + virtual environment)
- 8 GB of RAM minimum, 16 GB recommended
- A microphone or recording app for capturing your initial voice sample

The app uses Apple's Metal Performance Shaders (MPS) for GPU acceleration on Apple Silicon. Intel Macs and other platforms aren't officially supported but may work with code changes.

## Installation

Open Terminal and run:

```bash
git clone https://github.com/ShaonINT/AI_Voice_Over.git
cd AI_Voice_Over
bash setup.sh
```

The setup script:

1. Installs Homebrew if it's missing
2. Installs `ffmpeg` and Python 3.11
3. Creates an isolated Python virtual environment
4. Installs Chatterbox TTS, Gradio, and PyTorch

The first launch downloads about 2 GB of model weights from Hugging Face. Subsequent launches start in seconds.

## Daily use

```bash
cd AI_Voice_Over
bash run.sh
```

This starts the server and opens [http://127.0.0.1:7860](http://127.0.0.1:7860) in your browser. Leave the Terminal window open while you use the app; press `Ctrl+C` to stop the server when you're done.

### Workflow

1. **Record a voice sample.** Open the *Voice Library* tab. Either upload an existing recording or click the microphone icon to record one in the browser. Give it a short name like `me_calm` and click *Save to library*. See [VOICE_SAMPLES_GUIDE.md](VOICE_SAMPLES_GUIDE.md) before recording — sample quality is the single biggest factor in output quality.
2. **Write or paste a script.** Open the *Generate* tab. Type into the script box, or paste a full YouTube script. There's no length limit; long scripts get chunked automatically.
3. **Pick a voice.** Select the sample you just saved from the *Voice* dropdown.
4. **Generate.** Click *Generate*. A progress bar shows each chunk as it's produced. For a typical 90-second voiceover, expect 15–30 seconds of generation time on an M2.
5. **Download.** The audio appears in the right panel with a play button and a download icon. Files are also written to the `output/` folder automatically, named with a timestamp and voice name, so you can drag them straight into your video editor.

## How it works

Voice Clone Studio is a thin Gradio web UI wrapped around [Chatterbox TTS](https://github.com/resemble-ai/chatterbox), an open-source zero-shot voice cloning model from Resemble AI. The model takes two inputs — a reference audio clip and a text string — and generates speech in the style of the reference. Because it's zero-shot, no per-voice training is needed: you give it 20 seconds of you talking, and it can read anything in your voice from that moment on.

The model has two pieces under the hood. A T3 transformer converts your text into a sequence of speech tokens, conditioned on a voice embedding extracted from your reference clip. An S3Gen flow-matching decoder then converts those tokens into a 24 kHz audio waveform. Both components run on your Mac's GPU via PyTorch's MPS backend.

For long inputs, the app splits your text on sentence boundaries (then commas as a fallback) into chunks of about 280 characters each, generates each chunk independently using the same reference voice, and concatenates the results with short silences between chunks. This sidesteps the model's per-generation length limit and produces audio that sounds continuous.

## Repository structure

```
.
├── app.py                    # Gradio web app
├── setup.sh                  # One-time installer
├── run.sh                    # Launcher
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── VOICE_SAMPLES_GUIDE.md    # How to record a good reference sample
├── LICENSE                   # MIT
├── docs/
│   └── screenshot.svg        # UI screenshot (replace with a real PNG anytime)
├── samples/                  # Your voice reference clips (gitignored)
└── output/                   # Generated audio files (gitignored)
```

Voice samples and generated audio are deliberately excluded from version control — they're personal data and shouldn't end up on GitHub.

## Troubleshooting

**`gh auth setup-git` permission errors during install.** Run `sudo chown -R "$(whoami)" ~/.config` and try again. This happens when `~/.config` was created by a `sudo` command at some point.

**Chatterbox crashes with `TypeError: 'NoneType' object is not callable` during model load.** This means the `resemble-perth` watermarking library failed to load its weights. The app's built-in shim handles this — if you're seeing this error, you may be running an older version of `app.py`. Pull the latest from the repo.

**Generation is slow on first run.** The first call after launch warms up the MPS backend; subsequent generations are faster. If it's still slow after a few runs, you may be on CPU instead of MPS — check the startup log for `Using device: mps`.

**Output sounds nothing like me.** Re-record your reference sample using the guidance in [VOICE_SAMPLES_GUIDE.md](VOICE_SAMPLES_GUIDE.md). Common culprits: background noise, heavily compressed audio (Bluetooth headset, etc.), too-short clips, or a tone that doesn't match the kind of speech you're asking it to generate.

## Replacing the screenshot

The `docs/screenshot.svg` file is a placeholder mockup. To replace it with a real screenshot of your running app:

1. Launch the app with `bash run.sh`
2. On Mac: press `Shift + Cmd + 4`, then `Space`, then click the browser window — saves a PNG to your Desktop
3. Move that PNG to `docs/screenshot.png`
4. In this README, change the line `![Voice Clone Studio interface](docs/screenshot.svg)` to `![Voice Clone Studio interface](docs/screenshot.png)`
5. Commit and push

## Ethics

Only clone your own voice, or someone who has given you explicit written permission. Voice cloning without consent is harmful and, in many jurisdictions, illegal.

If you publish AI-generated audio to YouTube, follow YouTube's [synthetic content disclosure policy](https://support.google.com/youtube/answer/14328491) — meaningfully altered or synthetic content must be disclosed in some categories.

## License

Voice Clone Studio is released under the [MIT license](LICENSE). The Chatterbox TTS model it wraps is also MIT licensed by Resemble AI, which means audio you generate is yours to use commercially, including in monetized YouTube videos.

## Acknowledgments

- [Resemble AI](https://www.resemble.ai/) for releasing [Chatterbox TTS](https://github.com/resemble-ai/chatterbox) under an open license
- The [Gradio](https://www.gradio.app/) team for making local web UIs almost effortless
- Everyone working on open-source TTS, which keeps tools like this free for creators
