# Настройка PostgreSQL для Mythic

## 🚀 Быстрая настройка (автоматическая)

```bash
# 1. Запустите скрипт автонастройки
cd mythic_backend
python setup_postgres.py

# 2. Создайте первую миграцию
alembic revision --autogenerate -m "Initial migration"

# 3. Примените миграции
alembic upgrade head

# 4. Запустите приложение
uvicorn app.main:app --reload
```

## 🔧 Ручная настройка

### 1. Установите PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Скачайте с [postgresql.org](https://www.postgresql.org/download/windows/)

### 2. Создайте базу данных и пользователя

```bash
sudo -u postgres psql
```

В psql выполните:
```sql
CREATE USER mythic_user WITH PASSWORD 'mythic_password';
CREATE DATABASE mythic_db OWNER mythic_user;
GRANT ALL PRIVILEGES ON DATABASE mythic_db TO mythic_user;
ALTER USER mythic_user CREATEDB;
\q
```

### 3. Установите Python зависимости

```bash
pip install asyncpg psycopg2-binary
```

### 4. Создайте .env файл

```bash
cp env.example .env
```

Отредактируйте `.env`:
```env
DATABASE_URL=postgresql://mythic_user:mythic_password@localhost:5432/mythic_db
ASYNC_DATABASE_URL=postgresql+asyncpg://mythic_user:mythic_password@localhost:5432/mythic_db
```

### 5. Инициализируйте Alembic (первый раз)

```bash
# Если папка alembic уже существует, пропустите эту команду
alembic init alembic
```

### 6. Создайте и примените миграции

```bash
# Создать миграцию на основе моделей
alembic revision --autogenerate -m "Initial migration"

# Применить миграции
alembic upgrade head
```

## 🔄 Работа с миграциями

### Создание новой миграции
```bash
alembic revision --autogenerate -m "Описание изменений"
```

### Применение миграций
```bash
alembic upgrade head
```

### Откат миграций
```bash
# Откатить на одну миграцию назад
alembic downgrade -1

# Откатить до конкретной ревизии
alembic downgrade <revision_id>
```

### Просмотр истории
```bash
alembic history
alembic current
```

## 🐳 Использование Docker (альтернатива)

Создайте `docker-compose.yml`:
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: mythic_db
      POSTGRES_USER: mythic_user
      POSTGRES_PASSWORD: mythic_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Запустите:
```bash
docker-compose up -d
```

## 🌐 Продакшен (облачные решения)

### Railway
1. Создайте проект на [railway.app](https://railway.app)
2. Добавьте PostgreSQL плагин
3. Скопируйте CONNECTION_URL в переменные окружения

### Render
1. Создайте PostgreSQL базу на [render.com](https://render.com)
2. Используйте внешний CONNECTION_URL

### Supabase
1. Создайте проект на [supabase.com](https://supabase.com)
2. Получите строку подключения из настроек

## ⚠️ Частые проблемы

### Ошибка подключения
```bash
# Проверьте статус PostgreSQL
sudo systemctl status postgresql

# Перезапустите
sudo systemctl restart postgresql
```

### Ошибка аутентификации
Проверьте файл `/etc/postgresql/*/main/pg_hba.conf` и измените:
```
local   all             all                                     peer
```
на:
```
local   all             all                                     md5
```

### Права доступа
```sql
GRANT ALL PRIVILEGES ON DATABASE mythic_db TO mythic_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mythic_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mythic_user;
```

## 📊 Мониторинг

### Подключение к базе
```bash
PGPASSWORD=mythic_password psql -h localhost -U mythic_user -d mythic_db
```

### Полезные SQL команды
```sql
-- Посмотреть все таблицы
\dt

-- Посмотреть структуру таблицы
\d books

-- Посмотреть размер базы данных
SELECT pg_size_pretty(pg_database_size('mythic_db'));

-- Посмотреть активные подключения
SELECT * FROM pg_stat_activity WHERE datname = 'mythic_db';
``` 