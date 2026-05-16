from re import sub
import subprocess
from pathlib import Path

def download_video(url: str, output_dir: str) -> str:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    template = str(out_dir / 'video.%(ext)s')

    cmd = [
        'yt-dlp',
        '--no-playlist',
        '-o', template,
        '-f', 'best[ext=mp4]/best',
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    
    files = sorted(out_dir.glob('video.*'), key=lambda p: p.stat().st_mtime)
    if not files:
        raise RuntimeError('yt-dlp finished but no file found')
    return str(files[0])