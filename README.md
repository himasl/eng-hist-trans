# conv — видео в текст

Сервис расшифровывает речь из **локального видео** или **ссылки** (YouTube и др.) и отдаёт текст. Есть CLI, HTTP API и веб-интерфейс.

**Стек:** Python, ffmpeg, yt-dlp, faster-whisper, FastAPI, Docker.

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

- `WHISPER_MODEL` — `tiny`, `base`, `small` (в Docker по умолчанию `tiny`; локально без env — `base`)
- `language` в API — `"ru"` или не указывать для автоопределения

## Бесплатный деплой (рекомендации)

Проект тяжёлый (ffmpeg + Whisper, долгие запросы). Нужен хостинг с **Docker** и без жёсткого лимита в 10–60 секунд, как у serverless.

| Платформа | Плюсы | Минусы |
|-----------|--------|--------|
| **[Railway](https://railway.app)** | Deploy из GitHub, Dockerfile, просто | ~$5 кредитов/мес бесплатно, потом платно; сервис «засыпает» |
| **[Render](https://render.com)** | Free Web Service + Docker | Free tier засыпает, медленный cold start, лимиты RAM/CPU |
| **[Fly.io](https://fly.io)** | Docker, близко к пользователю | Нужна карта; free allowance на несколько маленьких VM |
| **[Oracle Cloud](https://www.oracle.com/cloud/free/)** | VPS Always Free (ARM), полный контроль | Настройка VPS и Docker вручную, дольше старт |
| **[Google Cloud Run](https://cloud.google.com/run)** | Docker, pay-per-use | Free tier есть; таймаут запроса до 60 мин (настроить), cold start |

**Не подходят:** Vercel, Netlify Functions — нет нормального ffmpeg/Whisper и мало времени на запрос.

### Railway

1. GitHub → New Project → Deploy from repo.
2. Railway подхватит `Dockerfile` и `railway.toml` (healthcheck `/health`).
3. Старт: `start.sh` → uvicorn на порту `$PORT` (Railway задаёт сам).
4. В Variables при OOM: `WHISPER_MODEL=tiny` (уже в Dockerfile) или увеличь RAM в настройках сервиса.
5. **Не задавай** Custom Start Command на `python -m src.main` — это CLI, контейнер сразу падает.

После деплоя открой выданный URL → сайт и `/docs`.

### VPS (Oracle / Hetzner)

```bash
git clone <repo> && cd conv
docker compose up -d app
```

Поставь reverse proxy (Caddy/nginx) с HTTPS — нужно для Telegram Mini App.

## Дальше

Telegram-бот и Mini App на том же API (`/transcribe/*`).
