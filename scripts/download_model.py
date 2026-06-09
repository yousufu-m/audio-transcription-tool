#!/usr/bin/env python3
"""
Download faster-whisper models to local models/ directory for offline use.
Usage:
    python scripts/download_model.py --model large-v3
    python scripts/download_model.py --model small --model medium
    python scripts/download_model.py --all
"""
import argparse
import subprocess
import sys
from pathlib import Path


AVAILABLE_MODELS = [
    "tiny",
    "base",
    "small",
    "medium",
    "large-v1",
    "large-v2",
    "large-v3",
    "turbo",
    "distil-small.en",
    "distil-medium.en",
    "distil-large-v2",
    "distil-large-v3",
]


def download_model(model_name: str, models_dir: Path) -> bool:
    """Download a single model using huggingface-cli."""
    local_dir = models_dir / f"faster-whisper-{model_name}"
    
    if local_dir.exists():
        print(f"⏭  {model_name}: 已存在 {local_dir}，跳过")
        return True
    
    print(f"⬇  正在下载 {model_name} -> {local_dir} ...")
    try:
        # 使用 huggingface-cli 下载
        cmd = [
            sys.executable, "-m", "huggingface_hub.cli",
            "download",
            f"Systran/faster-whisper-{model_name}",
            "--local-dir", str(local_dir),
            "--local-dir-use-symlinks", "False",
        ]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅  {model_name} 下载完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌  {model_name} 下载失败: {e.stderr.strip()}")
        # 清理不完整目录
        if local_dir.exists():
            import shutil
            shutil.rmtree(local_dir)
        return False
    except FileNotFoundError:
        print("❌  未找到 huggingface_hub，请先安装: pip install huggingface-hub")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download faster-whisper models to local models/ directory for offline transcription.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/download_model.py --model large-v3
  python scripts/download_model.py --model small --model medium
  python scripts/download_model.py --all
  python scripts/download_model.py --list
        """
    )
    parser.add_argument(
        "--model", "-m",
        action="append",
        choices=AVAILABLE_MODELS,
        help=f"Model to download (can specify multiple). Choices: {', '.join(AVAILABLE_MODELS)}"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Download all available models (~15GB total)"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available models and exit"
    )
    parser.add_argument(
        "--models-dir",
        default=None,
        help="Custom models directory (default: ./models relative to script)"
    )
    
    args = parser.parse_args()
    
    # 确定 models 目录
    if args.models_dir:
        models_dir = Path(args.models_dir).resolve()
    else:
        models_dir = Path(__file__).parent.parent / "models"
    
    models_dir.mkdir(parents=True, exist_ok=True)
    
    if args.list:
        print("可用模型:")
        for m in AVAILABLE_MODELS:
            print(f"  {m}")
        return
    
    if not args.model and not args.all:
        parser.print_help()
        print("\n❌  请指定 --model 或 --all")
        sys.exit(1)
    
    # 要下载的模型列表
    if args.all:
        to_download = AVAILABLE_MODELS
        print(f"📦 将下载所有 {len(AVAILABLE_MODELS)} 个模型（约 15GB）")
    else:
        to_download = args.model
        print(f"📦 将下载 {len(to_download)} 个模型: {', '.join(to_download)}")
    
    print(f"📁 目标目录: {models_dir}\n")
    
    # 逐个下载
    success = []
    failed = []
    
    for model in to_download:
        ok = download_model(model, models_dir)
        if ok:
            success.append(model)
        else:
            failed.append(model)
        print()  # 空行分隔
    
    # 汇总
    print("=" * 50)
    print(f"✅ 成功: {len(success)} 个 - {', '.join(success) if success else '无'}")
    if failed:
        print(f"❌ 失败: {len(failed)} 个 - {', '.join(failed)}")
        sys.exit(1)
    else:
        print("\n🎉 所有模型下载完成！现在可以完全离线使用 transcribe.py 了")
        print(f"💡 使用示例: python scripts/transcribe.py audio.mp3 --model large-v3")


if __name__ == "__main__":
    main()