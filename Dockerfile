FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg curl ca-certificates unzip \
    && curl -fsSL https://deno.land/install.sh | sh \
    && ln -sf /root/.deno/bin/deno /usr/local/bin/deno \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.deno/bin:${PATH}"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY static/ ./static/
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

ENV PORT=8000
ENV WHISPER_MODEL=tiny

EXPOSE 8000

# Railway / Render: веб-сервер. CLI: docker compose run --entrypoint ...
CMD ["/app/start.sh"]
