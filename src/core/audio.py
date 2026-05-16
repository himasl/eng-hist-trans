import subprocess
from pathlib import Path

def extract_audio(video_path: str, output_path: str) -> str:
    video = Path(video_path)
    if not video.is_file():
        raise FileNotFoundError(video)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        'ffmpeg', '-y',
        '-i', str(video),
        '-vn',
        '-acodec','pcm_s16le',
        '-ar', '16000',
        '-ac', '1',
        str(out),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return str(out)