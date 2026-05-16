# conv — видео в текст

Сервис расшифровывает речь из **локального видео** или **ссылки** (YouTube и др.) и отдаёт текст. Есть CLI, HTTP API и веб-интерфейс.

**Стек:** Python, ffmpeg, yt-dlp, faster-whisper, FastAPI.

## Как это работает

```
видеофайл или URL
       ↓
  yt-dlp (если ссылка)
       ↓
  ffmpeg → WAV 16 kHz
       ↓
  Whisper → текст
       ↓
  .txt / .docx (на сайте или через API)
```

## Структура

```
src/core/     — логика: скачивание, аудио, транскрипция, экспорт docx
src/api/      — FastAPI + раздача сайта (static/)
src/main.py   — CLI
static/       — веб-интерфейс
data/         — тестовые видео (монтируется в Docker)
output/       — результаты с флагом -o (CLI)
```

## Запуск (Docker)

Нужны: Docker и Docker Compose.

### Веб и API (основной способ)

```bash
docker compose build app
docker compose up app
```

- Сайт: http://localhost:8000 — вкладки «Видеофайл» / «Ссылка», скачивание `.txt` или `.docx`
- Документация API: http://localhost:8000/docs
- Проверка: `curl http://localhost:8000/health`

Первый запрос может занять **несколько минут** (скачивание модели Whisper).

### CLI (терминал)

```bash
# локальный файл
docker compose run --rm conv /data/test.mp4

# ссылка (URL в кавычках)
docker compose run --rm conv "https://www.youtube.com/watch?v=..."

# сохранить в output/result.txt
docker compose run --rm conv /data/test.mp4 -o
```

Положи тестовое видео в `data/test.mp4`.

## API

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/health` | Статус сервиса |
| `POST` | `/transcribe/file` | Загрузка видео (`multipart/form-data`, поле `file`) |
| `POST` | `/transcribe/url` | JSON: `{"url": "https://..."}` |
| `POST` | `/export/docx` | JSON: `{"text": "..."}` → файл Word |

Ответ транскрипции: `{"text": "..."}`.

## Переменные и настройки

В коде по умолчанию модель Whisper: `base`. Для быстрых тестов можно указать `tiny` в `src/main.py` или в теле запроса API (`model_size`).

Язык: автоопределение; для русского можно передать `"language": "ru"` в API.
