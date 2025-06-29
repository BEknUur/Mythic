FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libfontconfig1 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libxml2 \
    libxslt1.1 \
    fonts-dejavu-core \
    fonts-liberation \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя для безопасности
RUN useradd --create-home --shell /bin/bash mythic

WORKDIR /usr/src/app

# Копирование и установка зависимостей Python
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --timeout 300 --retries 3 -r requirements.txt

# Копирование кода приложения
COPY . .

# Создание директорий для данных
RUN mkdir -p data static
RUN chown -R mythic:mythic /usr/src/app

# Установка Playwright браузеров
RUN playwright install chromium
RUN playwright install-deps chromium

USER mythic

# Том для данных
VOLUME ["/usr/src/app/data"]

# Открытие порта
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
