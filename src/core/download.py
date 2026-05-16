import os
import subprocess
from pathlib import Path


def _yt_dlp_cmd(url: str, template: str) -> list[str]:
    cmd = [
        "yt-dlp",
        "--no-playlist",
        "--extractor-args",
        "youtube:player_client=android,web",
        "-o",
        template,
        "-f",
        "best[ext=mp4]/best",
        "--retries",
        "3",
        url,
    ]
    cookies_file = os.getenv("YT_COOKIES_FILE")
    if cookies_file and Path(cookies_file).is_file():
        cmd.insert(1, "--cookies")
        cmd.insert(2, cookies_file)
    return cmd


def download_video(url: str, output_dir: str) -> str:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    template = str(out_dir / "video.%(ext)s")

    result = subprocess.run(_yt_dlp_cmd(url, template), capture_output=True, text=True)
    if result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()
        if "Sign in to confirm" in err or "not a bot" in err:
            raise RuntimeError(
                "YouTube заблокировал скачивание с сервера. "
                "Загрузите видео файлом или задайте YT_COOKIES_FILE (см. README)."
            ) from None
        raise RuntimeError(err)

    files = sorted(out_dir.glob("video.*"), key=lambda p: p.stat().st_mtime)
    if not files:
        raise RuntimeError("yt-dlp finished but no file found")
    return str(files[0])
