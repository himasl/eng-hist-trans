from faster_whisper import WhisperModel

_model: WhisperModel | None = None

def _get_model(model_size: str) -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel(model_size, device='cpu', compute_type='int8')
    return _model

def transcribe(audio_path: str, model_size: str = 'base', language: str | None = None) -> str:
    model = _get_model(model_size)
    segments, info = model.transcribe(audio_path, language=language)
    text = ''.join(seg.text for seg in segments)
    return text.strip()
