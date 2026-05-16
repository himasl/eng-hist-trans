import os
import tempfile
from pathlib import Path
from src.core.audio import extract_audio
from src.core.transcribe import transcribe
from src.core.download import download_video

def is_url(source: str) -> bool:
    return source.startswith(("http://", "https://"))

def video_to_text(video_path: str, **kwargs) -> str:
    return media_to_text(video_path, **kwargs)

def media_to_text(
    source: str,
    model_size: str | None = None,
    language: str | None = None,
) -> str:
    if model_size is None:
        model_size = os.getenv("WHISPER_MODEL", "base")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        if is_url(source):
            video_path = download_video(source, str(tmp_path))
        else:
            video_path = source

        wav_path = tmp_path / 'audio.wav'
        extract_audio(video_path, str(wav_path))
        return transcribe(str(wav_path), model_size=model_size, language=language)