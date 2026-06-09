import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from faster_whisper import WhisperModel


AUDIO_SUFFIXES = {".m4a", ".mp3", ".wav", ".mp4", ".aac", ".flac", ".ogg", ".opus", ".webm"}


def fmt_time(seconds: float) -> str:
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def fmt_elapsed(seconds: float) -> str:
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h{m:02d}m{s:02d}s"
    if m:
        return f"{m}m{s:02d}s"
    return f"{s}s"


def progress_bar(ratio: float, width: int = 25) -> str:
    filled = int(ratio * width)
    return "[" + "█" * filled + "░" * (width - filled) + "]"


def safe_name(text: str, limit: int = 90) -> str:
    text = re.sub(r'[<>:\"/\\\\|?*\r\n\t]+', "_", text).strip(" ._")
    return (text[:limit].rstrip(" ._") or "audio_transcript")


def run_yt_dlp(url: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    template = str(out_dir / "%(title).120B.%(ext)s")
    cmd = [
        sys.executable,
        "-m",
        "yt_dlp",
        "-f",
        "ba/bestaudio/0",
        "--no-playlist",
        "--write-info-json",
        "-o",
        template,
        url,
    ]
    subprocess.run(cmd, check=True)
    candidates = sorted(
        [p for p in out_dir.iterdir() if p.suffix.lower() in AUDIO_SUFFIXES],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise RuntimeError("yt-dlp finished but no audio file was found.")
    return candidates[0]


def transcribe_audio(
    audio: Path,
    out_dir: Path,
    title: str | None,
    url: str | None,
    model_name: str,
    language: str | None,
    beam_size: int,
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    final_title = title or audio.stem
    base_name = safe_name(final_title)
    out_md = out_dir / f"{base_name}.md"
    out_json = out_dir / f"{base_name}.segments.json"
    generated_at = datetime.now().isoformat(timespec="seconds")

    print(f"[1/3] 加载模型 {model_name} ...", flush=True)
    # 优先使用本地模型目录
    local_model_dir = Path(__file__).parent.parent / "models" / f"faster-whisper-{model_name}"
    if local_model_dir.exists():
        model = WhisperModel(str(local_model_dir), device="cpu", compute_type="int8")
    else:
        model = WhisperModel(model_name, device="cpu", compute_type="int8")

    print(f"[2/3] 分析音频，准备转写 ...", flush=True)
    segments_iter, info = model.transcribe(
        str(audio),
        language=language,
        beam_size=beam_size,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 700},
        condition_on_previous_text=True,
    )

    total = info.duration
    print(f"[3/3] 开始转写，音频时长 {fmt_time(total)}，语言: {info.language}\n", flush=True)

    header = [
        f"# {final_title}",
        "",
        "## 转写说明",
        "",
        f"- 音频文件：`{audio}`",
        f"- 原始链接：{url}" if url else "- 原始链接：本地文件",
        f"- 转写时间：{generated_at}",
        f"- 转写模型：faster-whisper `{model_name}`，CPU int8",
        f"- 语言设置：{language or '自动检测'}",
        f"- 检测到语言：{info.language}，置信度：{info.language_probability:.3f}",
        "- 说明：本稿为机器自动识别结果，建议人工校对人名、数字、英文术语和专有名词。",
        "",
        "## 机器转写文字稿",
        "",
    ]
    out_md.write_text("\n".join(header), encoding="utf-8-sig")

    segments = []
    wall_start = time.monotonic()

    with out_md.open("a", encoding="utf-8-sig", newline="\n") as md:
        for seg in segments_iter:
            text = seg.text.strip()
            if not text:
                continue
            item = {"start": seg.start, "end": seg.end, "text": text}
            segments.append(item)
            md.write(f"**[{fmt_time(seg.start)} - {fmt_time(seg.end)}]** {text}\n\n")
            md.flush()

            # 实时进度
            elapsed = time.monotonic() - wall_start
            ratio = min(seg.end / total, 1.0) if total > 0 else 0
            pct = ratio * 100
            bar = progress_bar(ratio)
            if ratio > 0.005:
                eta = elapsed / ratio * (1 - ratio)
                eta_str = f"  剩余 ~{fmt_elapsed(eta)}"
            else:
                eta_str = ""
            line = (
                f"\r  {bar} {pct:5.1f}%  "
                f"{fmt_time(seg.end)} / {fmt_time(total)}  "
                f"已用 {fmt_elapsed(elapsed)}{eta_str}  "
                f"({len(segments)} 段)"
            )
            print(line, end="", flush=True)

            if len(segments) % 50 == 0:
                write_segments(
                    out_json, audio, final_title, url,
                    model_name, language, info, generated_at, segments,
                )

    # 换行，结束进度条
    print(flush=True)

    write_segments(
        out_json, audio, final_title, url,
        model_name, language, info, generated_at, segments,
    )

    total_elapsed = time.monotonic() - wall_start
    metadata = {
        "title": final_title,
        "audio": str(audio),
        "url": url,
        "model": model_name,
        "language_setting": language or "auto",
        "detected_language": info.language,
        "language_probability": info.language_probability,
        "duration_seconds": info.duration,
        "duration_hhmmss": fmt_time(info.duration),
        "segment_count": len(segments),
        "transcribe_elapsed_seconds": round(total_elapsed, 1),
        "transcribe_elapsed_hhmmss": fmt_time(total_elapsed),
        "generated_at": generated_at,
    }
    with out_md.open("a", encoding="utf-8-sig", newline="\n") as md:
        md.write("\n## 转写元数据\n\n")
        md.write("```json\n")
        md.write(json.dumps(metadata, ensure_ascii=False, indent=2))
        md.write("\n```\n")

    print(f"\n完成！共 {len(segments)} 段，实际用时 {fmt_elapsed(total_elapsed)}")
    print(f"  文字稿：{out_md}")
    print(f"  分段JSON：{out_json}")
    return out_md, out_json


def write_segments(
    path: Path,
    audio: Path,
    title: str,
    url: str | None,
    model_name: str,
    language: str | None,
    info,
    generated_at: str,
    segments: list[dict],
) -> None:
    payload = {
        "title": title,
        "audio": str(audio),
        "url": url,
        "model": model_name,
        "language_setting": language or "auto",
        "detected_language": info.language,
        "language_probability": info.language_probability,
        "duration_seconds": info.duration,
        "duration_hhmmss": fmt_time(info.duration),
        "segment_count": len(segments),
        "generated_at": generated_at,
        "segments": segments,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe local audio or downloadable media URL.")
    parser.add_argument("input", help="Local audio/video path or URL.")
    parser.add_argument("--out-dir", default="./output")
    parser.add_argument("--title", default=None)
    parser.add_argument("--model", default="large-v3", help="tiny, base, small, medium, large-v3, turbo, etc.")
    parser.add_argument("--language", default="zh", help="Use zh for Chinese; use auto for auto-detect.")
    parser.add_argument("--beam-size", type=int, default=3)
    parser.add_argument("--download", action="store_true", help="Treat input as URL and download audio first.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    source = args.input
    url = source if re.match(r"^https?://", source, re.I) else None

    if args.download or url:
        audio = run_yt_dlp(source, out_dir / "_audio_cache")
    else:
        audio = Path(source)
        if not audio.exists():
            raise FileNotFoundError(audio)

    language = None if args.language.lower() in {"auto", "none", ""} else args.language
    transcribe_audio(
        audio=audio,
        out_dir=out_dir,
        title=args.title,
        url=url,
        model_name=args.model,
        language=language,
        beam_size=args.beam_size,
    )


if __name__ == "__main__":
    main()