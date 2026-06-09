# 🎙️ Audio Transcription Tool

> **Local offline speech-to-text** powered by `faster-whisper` (CTranslate2) + `yt-dlp` for direct URL transcription.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![faster-whisper](https://img.shields.io/badge/faster--whisper-1.2.1-orange.svg)](https://github.com/SYSTRAN/faster-whisper)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-2026.03.17-red.svg)](https://github.com/yt-dlp/yt-dlp)

Zero-cloud, privacy-first audio transcription for Chinese/English content. Transcribe local files or directly from URLs (Xiaoyuzhou, Bilibili, YouTube, 1000+ sites).

## ✨ Features

- 🔒 **Fully offline** — No API keys, no cloud, your audio never leaves your machine
- 🌐 **URL → Text** — Paste a podcast/video link, get transcript automatically
- 📝 **Dual output** — Timestamped Markdown + structured JSON segments
- ⚡ **Real-time progress** — Live progress bar with ETA in terminal
- 🇨🇳 **Chinese-optimized** — Default `large-v3` model excels at Mandarin
- 📦 **Portable** — Vendored models, isolated venv, share as a folder

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ (3.11+ recommended)
- [ffmpeg](https://ffmpeg.org/download.html) in PATH (for yt-dlp audio extraction)

### Install

```bash
# Clone or download this repo
git clone https://github.com/<your-username>/audio-transcription-tool.git
cd audio-transcription-tool

# Create virtual environment
python -m venv .venv
# Windows:
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r scripts/requirements.txt
```

### (Optional) Pre-download Model for Offline Use

```bash
# Download ~3GB model to local models/ directory
pip install huggingface-hub
huggingface-cli download Systran/faster-whisper-large-v3 --local-dir models/faster-whisper-large-v3
```

> The script auto-detects `models/faster-whisper-<model>/` and uses it preferentially.

## 💡 Usage

```bash
# Activate venv first!
# Windows: .\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate

# Local audio/video file
python scripts/transcribe.py "audio.mp3"

# Local video file
python scripts/transcribe.py "video.mp4"

# URL → download + transcribe (Xiaoyuzhou, Bilibili, YouTube, etc.)
python scripts/transcribe.py "https://www.xiaoyuzhoufm.com/episode/xxx" --download

# Custom output directory
python scripts/transcribe.py "audio.mp3" --out-dir "./my_transcripts"

# English or auto-detect language
python scripts/transcribe.py "audio.mp3" --language en
python scripts/transcribe.py "audio.mp3" --language auto

# Faster model (less accurate)
python scripts/transcribe.py "audio.mp3" --model small

# Custom title
python scripts/transcribe.py "audio.mp3" --title "My Podcast Ep.1"
```

### Arguments

| Arg | Default | Description |
|-----|---------|-------------|
| `input` | (required) | Local file path or URL |
| `--out-dir` | `./output` | Output directory |
| `--title` | Auto | Output file title |
| `--model` | `large-v3` | `tiny`/`base`/`small`/`medium`/`large-v3`/`turbo` |
| `--language` | `zh` | `zh` (Chinese), `en` (English), `auto` (detect) |
| `--beam-size` | `3` | Decode beam width (higher = slower, more accurate) |
| `--download` | Auto | Force treat input as URL |

## 📁 Output Files

```
output/
├── Title.md                 # Timestamped Markdown transcript (UTF-8 BOM)
├── Title.segments.json      # Full segments + metadata for post-processing
└── _audio_cache/            # Downloaded audio (URL mode only)
```

**Markdown preview:**
```markdown
# My Podcast Episode 1

## Transcription Info
- Audio file: `audio.mp3`
- Source: Local file
- Transcribed: 2025-01-15T14:30:00
- Model: faster-whisper `large-v3`, CPU int8
- Language: zh
- Detected: zh (confidence: 0.998)

## Transcript

**[00:00:00 - 00:00:05]** Welcome to the show.

**[00:00:05 - 00:00:12]** Today we discuss AI advances.
...

## Metadata
```json
{
  "title": "My Podcast Episode 1",
  "duration_hhmmss": "00:43:54",
  "segment_count": 412,
  "transcribe_elapsed_hhmmss": "00:18:07",
  ...
}
```

## 🏃 Live Progress

```
[1/3] Loading model large-v3 ...
[2/3] Analyzing audio ...
[3/3] Transcribing, duration 00:43:54, lang: zh

  [█████████████░░░░░░░░░░░░] 52.3%  00:22:58 / 00:43:54  Elapsed 8m12s  ETA ~7m28s  (183 segs)

Done! 412 segments, 18m07s
  Transcript: output/Title.md
  Segments:   output/Title.segments.json
```

## 🎯 Model Selection Guide

| Model | Params | Speed (vs large-v3) | Chinese Accuracy | Best For |
|-------|--------|---------------------|------------------|----------|
| `tiny` | 39M | ~8x | ⭐⭐ | Quick preview, very low-end |
| `base` | 74M | ~5x | ⭐⭐⭐ | Speed/accuracy balance |
| `small` | 244M | ~2.5x | ⭐⭐⭐⭐ | **Daily use recommended** |
| `medium` | 769M | ~1.5x | ⭐⭐⭐⭐⭐ | High accuracy needs |
| `large-v3` | 1550M | 1x (baseline) | ⭐⭐⭐⭐⭐ | **Default: best Chinese** |
| `turbo` | 809M | ~1.8x | ⭐⭐⭐⭐ | Large-model speedup |

> CPU int8: `large-v3` ≈ 2–3× realtime. 1hr audio ≈ 20–30min on 4-core CPU.

## ❓ FAQ

**Slow first run / model download fails?**
First run downloads ~3GB from HuggingFace. Pre-download via `huggingface-cli` (see above) or use a proxy.

**Fully offline?**
Yes — ensure `models/faster-whisper-large-v3/` exists with all model files and venv deps installed.

**Typos in transcript?**
Machine errors happen (names, numbers, jargon). Use `.segments.json` for manual review, or pipe to an LLM for correction.

**OOM / sluggish?**
Try `--model small` or `--model base`, reduce `--beam-size`.

**Windows Chinese path garbled?**
Script writes UTF-8-BOM. Run `chcp 65001` in PowerShell first. Use `python scripts/transcribe.py` not double-click.

## 🔧 Advanced

### Batch Transcribe

```bash
# Bash
for f in ./audio/*.mp3; do
  python scripts/transcribe.py "$f" --out-dir ./transcripts --model large-v3
done

# PowerShell
Get-ChildItem ./audio/*.mp3 | ForEach-Object {
  python scripts/transcribe.py $_.FullName --out-dir ./transcripts --model large-v3
}
```

### Import as Module

```python
from scripts.transcribe import transcribe_audio, run_yt_dlp
from pathlib import Path

# Local file
md, json = transcribe_audio(
    audio=Path("audio.mp3"),
    out_dir=Path("./output"),
    title="Custom Title",
    url=None,
    model_name="large-v3",
    language="zh",
    beam_size=3,
)

# URL
audio_path = run_yt_dlp("https://example.com/video", Path("./output/_audio_cache"))
md, json = transcribe_audio(
    audio=audio_path,
    out_dir=Path("./output"),
    title=None,
    url="https://example.com/video",
    model_name="large-v3",
    language="zh",
    beam_size=3,
)
```

## 📦 Supported Formats

**Audio/Video:** `.m4a`, `.mp3`, `.wav`, `.mp4`, `.aac`, `.flac`, `.ogg`, `.opus`, `.webm`

**URL Sites:** 1000+ via yt-dlp (Xiaoyuzhou, Bilibili, YouTube, Spotify, Apple Podcasts, etc.)

## 🛠 Dependencies

- `faster-whisper==1.2.1` — CTranslate2 accelerated Whisper
- `yt-dlp==2026.3.17` — Universal video/audio downloader
- Python 3.10+ (3.11+ recommended)
- System: `ffmpeg` (required by yt-dlp)

## 📄 License

MIT License — Free to use, modify, distribute.

Model weights follow original Whisper (MIT). faster-whisper is MIT licensed.

---

**Enjoy offline transcription freedom!** 🎙️✨

*Star ⭐ this repo if it helps you!*