import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.core.export import text_to_docx_bytes
from src.core.pipeline import media_to_text

STATIC_DIR = Path(__file__).resolve().parents[2] / "static"

app = FastAPI(title="conv")


class UrlRequest(BaseModel):
    url: str
    model_size: str = "base"
    language: str | None = None


class ExportRequest(BaseModel):
    text: str
    title: str = "Транскрипция"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/transcribe/file")
async def transcribe_file(
    file: UploadFile = File(...),
    model_size: str = "base",
    language: str | None = None,
):
    suffix = Path(file.filename or "video.mp4").suffix or ".mp4"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        text = media_to_text(tmp_path, model_size=model_size, language=language)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)


@app.post("/export/docx")
def export_docx(body: ExportRequest):
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="Текст пустой")
    try:
        data = text_to_docx_bytes(body.text, title=body.title)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="transcript.docx"'},
    )


@app.post("/transcribe/url")
def transcribe_url(body: UrlRequest):
    try:
        text = media_to_text(
            body.url,
            model_size=body.model_size,
            language=body.language,
        )
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
