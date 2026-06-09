# 🎙️ 音频转文字工具

> **本地离线语音识别**，基于 `faster-whisper` (CTranslate2 加速) + `yt-dlp` 直链下载转写。

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![faster-whisper](https://img.shields.io/badge/faster--whisper-1.2.1-orange.svg)](https://github.com/SYSTRAN/faster-whisper)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-2026.03.17-red.svg)](https://github.com/yt-dlp/yt-dlp)

零云端、隐私优先的中英语音转写工具。支持本地文件、在线链接（小宇宙、B站、YouTube、Spotify 等 1000+ 站点），一键生成带时间戳的 Markdown 文稿与结构化 JSON。

## ✨ 核心特性

- 🔒 **完全离线** — 无需 API Key，音频不出本地，隐私无忧
- 🌐 **链接直转** — 粘贴播客/视频链接，自动下载音频并转写
- 📝 **双格式输出** — 时间戳 Markdown（人读）+ 分段 JSON（机读/后处理）
- ⚡ **实时进度** — 终端显示进度条、已用时间、预计剩余、分段数
- 🇨🇳 **中文优化** — 默认 `large-v3` 模型，中文识别准确率极高
- 📦 **开箱即用** — 模型可随项目分发，虚拟环境隔离，文件夹即工具

## 🚀 快速上手

### 环境要求
- Python 3.10+（推荐 3.11+）
- [ffmpeg](https://ffmpeg.org/download.html) 已加入 PATH（yt-dlp 提取音频需要）

### 安装步骤

```bash
# 1. 克隆或下载本仓库
git clone https://github.com/<你的用户名>/audio-transcription-tool.git
cd audio-transcription-tool

# 2. 创建虚拟环境
python -m venv .venv
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# 3. 安装 Python 依赖
pip install -r scripts/requirements.txt
```

### （可选）预下载模型实现完全离线

**方式 A：便捷脚本（推荐）**
```bash
# 首次需安装 huggingface-hub
pip install huggingface-hub

# 下载单个模型（默认 large-v3，约 3GB）
python scripts/download_model.py --model large-v3

# 同时下载多个模型
python scripts/download_model.py --model small --model medium

# 下载所有模型（约 15GB）
python scripts/download_model.py --all

# 查看可用模型列表
python scripts/download_model.py --list
```

**方式 B：手动 huggingface-cli**
```bash
pip install huggingface-hub
huggingface-cli download Systran/faster-whisper-large-v3 --local-dir models/faster-whisper-large-v3
```

> 脚本会自动检测 `models/faster-whisper-<模型名>/` 目录并优先加载，实现完全离线运行。

## 💡 使用示例

```bash
# 先激活虚拟环境！
# Windows: .\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate

# 本地音频文件转写
python scripts/transcribe.py "audio.mp3"

# 本地视频文件转写
python scripts/transcribe.py "video.mp4"

# 在线链接 → 自动下载 + 转写（小宇宙、B站、YouTube 等）
python scripts/transcribe.py "https://www.xiaoyuzhoufm.com/episode/xxx" --download

# 指定输出目录
python scripts/transcribe.py "audio.mp3" --out-dir "./my_transcripts"

# 英文或自动检测语言
python scripts/transcribe.py "audio.mp3" --language en
python scripts/transcribe.py "audio.mp3" --language auto

# 使用更小模型加速（精度略降）
python scripts/transcribe.py "audio.mp3" --model small

# 自定义标题
python scripts/transcribe.py "audio.mp3" --title "我的播客第1期"
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `input` | (必填) | 本地音频/视频路径，或网页 URL |
| `--out-dir` | `./output` | 输出目录 |
| `--title` | 自动(文件名/视频标题) | 输出文件标题 |
| `--model` | `large-v3` | `tiny`/`base`/`small`/`medium`/`large-v3`/`turbo` 等 |
| `--language` | `zh` | `zh`(中文)、`en`(英文)、`auto`(自动检测) |
| `--beam-size` | `3` | 解码宽度，越大越准但越慢 |
| `--download` | 自动检测 | 强制将输入视为 URL 并下载音频 |

## 📁 输出文件

```
output/
├── 标题.md                 # 带时间戳 Markdown 文稿 (UTF-8 with BOM)
├── 标题.segments.json      # 完整分段 JSON，含元数据，便于后处理
└── _audio_cache/           # 下载的音频缓存（仅 URL 模式）
```

**Markdown 预览：**
```markdown
# 我的播客第1期

## 转写说明
- 音频文件：`audio.mp3`
- 原始链接：本地文件
- 转写时间：2025-01-15T14:30:00
- 转写模型：faster-whisper `large-v3`，CPU int8
- 语言设置：zh
- 检测到语言：zh，置信度：0.998
- 说明：本稿为机器自动识别结果，建议人工校对人名、数字、英文术语和专有名词。

## 机器转写文字稿

**[00:00:00 - 00:00:05]** 欢迎收听本期节目。

**[00:00:05 - 00:00:12]** 今天我们聊聊人工智能的最新进展。
...

## 转写元数据
```json
{
  "title": "我的播客第1期",
  "duration_hhmmss": "00:43:54",
  "segment_count": 412,
  "transcribe_elapsed_hhmmss": "00:18:07",
  ...
}
```

## 🏃 运行时进度显示

```
[1/3] 加载模型 large-v3 ...
[2/3] 分析音频，准备转写 ...
[3/3] 开始转写，音频时长 00:43:54，语言: zh

  [█████████████░░░░░░░░░░░░] 52.3%  00:22:58 / 00:43:54  已用 8m12s  剩余 ~7m28s  (183 段)

完成！共 412 段，实际用时 18m07s
  文字稿：output/标题.md
  分段JSON：output/标题.segments.json
```

## 🎯 模型选择指南

| 模型 | 参数量 | 相对速度 | 中文准确率 | 推荐场景 |
|------|--------|----------|------------|----------|
| `tiny` | 39M | ~8x | ⭐⭐ | 快速预览、极低配设备 |
| `base` | 74M | ~5x | ⭐⭐⭐ | 速度/准确率平衡 |
| `small` | 244M | ~2.5x | ⭐⭐⭐⭐ | **日常使用推荐** |
| `medium` | 769M | ~1.5x | ⭐⭐⭐⭐⭐ | 高准确率需求 |
| `large-v3` | 1550M | 1x (基准) | ⭐⭐⭐⭐⭐ | **默认：中文效果最佳** |
| `turbo` | 809M | ~1.8x | ⭐⭐⭐⭐ | 大模型加速版 |

> CPU int8 量化下，`large-v3` 约为实时 2–3 倍速度。4 核 CPU 转写 1 小时音频约需 20–30 分钟。

## ❓ 常见问题

**首次运行很慢 / 模型下载失败？**
首次运行会从 HuggingFace 下载模型（约 3GB）。建议预先用 `download_model.py` 或 `huggingface-cli` 下载，或使用代理。

**如何完全离线使用？**
确保 `models/faster-whisper-large-v3/` 目录下有完整模型文件，且虚拟环境已安装依赖。脚本会优先加载本地模型目录。

**转写结果有错别字？**
机器转写难免错误（人名、数字、专有名词、英文术语）。建议：
- 用 `.segments.json` 配合编辑器人工校对
- 关键段落二次确认
- 后续可接入 LLM 做纠错润色

**内存不足 / 卡顿？**
尝试 `--model small` 或 `--model base`，或减小 `--beam-size`。

**Windows 下中文路径/文件名乱码？**
脚本使用 UTF-8-BOM 写入。PowerShell 先执行 `chcp 65001`。运行脚本请用 `python scripts/transcribe.py` 而非双击。

## 🔧 进阶用法

### 批量转写

```bash
# Bash/Linux/macOS
for f in ./audio/*.mp3; do
  python scripts/transcribe.py "$f" --out-dir ./transcripts --model large-v3
done

# PowerShell
Get-ChildItem ./audio/*.mp3 | ForEach-Object {
  python scripts/transcribe.py $_.FullName --out-dir ./transcripts --model large-v3
}
```

### 作为模块导入

```python
from scripts.transcribe import transcribe_audio, run_yt_dlp
from pathlib import Path

# 本地文件
md, json = transcribe_audio(
    audio=Path("audio.mp3"),
    out_dir=Path("./output"),
    title="自定义标题",
    url=None,
    model_name="large-v3",
    language="zh",
    beam_size=3,
)

# 在线链接
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

## 📦 支持格式

**音频/视频：** `.m4a`, `.mp3`, `.wav`, `.mp4`, `.aac`, `.flac`, `.ogg`, `.opus`, `.webm`

**在线站点：** 1000+（小宇宙、哔哩哔哩、YouTube、Spotify、Apple Podcasts 等，via yt-dlp）

## 🛠 依赖说明

- `faster-whisper==1.2.1` — CTranslate2 加速的 Whisper 推理
- `yt-dlp==2026.3.17` — 通用视频/音频下载器
- Python 3.10+（推荐 3.11+）
- 系统依赖：`ffmpeg`（yt-dlp 需要，用于音频提取/转码）

## 📄 许可证

MIT License — 免费使用、修改、分发。

模型权重遵循原始 Whisper (MIT)，faster-whisper 遵循 MIT 许可证。

---

**享受离线转写的自由！** 🎙️✨

*如果对你有帮助，请给个 ⭐ Star 支持一下！*