FROM python:3.11-slim

# ---- system deps ----------------------------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libpango-1.0-0 libpangoft2-1.0-0 libfontconfig1 libcairo2 \
      libgdk-pixbuf2.0-0 libgtk-3-0 libxml2 libxslt1.1 \
      curl wget && \
    rm -rf /var/lib/apt/lists/*

# ---- python deps ----------------------------------------------------
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---- source code ----------------------------------------------------
COPY . .

# playwright (используется только если реально нужен браузер)
RUN playwright install-deps chromium && playwright install chromium

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
