# Makefile for Mythic Docker operations

.PHONY: help build up down restart logs clean

# По умолчанию показываем help
help:
	@echo "🎭 Mythic Docker Commands:"
	@echo ""
	@echo "📦 Основные команды:"
	@echo "  make up          - Запуск всех сервисов"
	@echo "  make down        - Остановка всех сервисов"
	@echo "  make restart     - Перезапуск всех сервисов"
	@echo "  make build       - Пересборка образов"
	@echo "  make rebuild     - Пересборка и запуск"
	@echo ""
	@echo "🔍 Мониторинг:"
	@echo "  make logs        - Просмотр логов всех сервисов"
	@echo "  make logs-be     - Логи только бэкенда"
	@echo "  make logs-fe     - Логи только фронтенда"
	@echo "  make status      - Статус контейнеров"
	@echo "  make health      - Проверка здоровья сервисов"
	@echo ""
	@echo "🗃️ База данных:"
	@echo "  make db          - Запуск только базы данных"
	@echo "  make db-shell    - Подключение к PostgreSQL"
	@echo "  make migrate     - Выполнение миграций"
	@echo "  make backup      - Backup базы данных"
	@echo ""
	@echo "🧹 Очистка:"
	@echo "  make clean       - Очистка неиспользуемых ресурсов"
	@echo "  make clean-all   - Полная очистка Docker"
	@echo "  make reset       - Сброс данных базы"
	@echo ""
	@echo "🚀 Разработка:"
	@echo "  make dev         - Запуск в режиме разработки"
	@echo "  make prod        - Запуск в production режиме"

# 📦 Основные команды
up:
	@echo "🚀 Запуск Mythic..."
	docker-compose up -d

down:
	@echo "🛑 Остановка Mythic..."
	docker-compose down

restart:
	@echo "🔄 Перезапуск Mythic..."
	docker-compose down
	docker-compose up -d

build:
	@echo "🔨 Пересборка образов..."
	docker-compose build

rebuild:
	@echo "🔨 Пересборка и запуск..."
	docker-compose up -d --build

# 🔍 Мониторинг
logs:
	@echo "📝 Логи всех сервисов..."
	docker-compose logs -f

logs-be:
	@echo "📝 Логи бэкенда..."
	docker-compose logs -f backend

logs-fe:
	@echo "📝 Логи фронтенда..."
	docker-compose logs -f frontend

status:
	@echo "📊 Статус контейнеров..."
	docker-compose ps

health:
	@echo "❤️ Проверка здоровья сервисов..."
	@echo "Backend health:"
	@docker-compose exec -T backend curl -f http://localhost:8000/health 2>/dev/null || echo "❌ Backend недоступен"
	@echo ""
	@echo "Frontend health:"
	@docker-compose exec -T frontend wget --spider --quiet http://localhost/ 2>/dev/null && echo "✅ Frontend работает" || echo "❌ Frontend недоступен"

# 🗃️ База данных
db:
	@echo "🗃️ Запуск базы данных..."
	docker-compose up -d database redis

db-shell:
	@echo "🗃️ Подключение к PostgreSQL..."
	docker-compose exec database psql -U mythic -d mythic

migrate:
	@echo "🗃️ Выполнение миграций..."
	docker-compose exec backend alembic upgrade head

backup:
	@echo "💾 Создание backup базы данных..."
	@mkdir -p backups
	docker-compose exec database pg_dump -U mythic mythic > backups/mythic_backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup создан в папке backups/"

# 🧹 Очистка
clean:
	@echo "🧹 Очистка неиспользуемых ресурсов..."
	docker image prune -f
	docker container prune -f
	docker network prune -f

clean-all:
	@echo "🧹 Полная очистка Docker..."
	docker system prune -af --volumes

reset:
	@echo "🔄 Сброс данных базы..."
	docker-compose down -v
	docker volume rm mythic_postgres_data mythic_redis_data 2>/dev/null || true
	@echo "✅ Данные сброшены. Запустите 'make up' для пересоздания"

# 🚀 Разработка
dev:
	@echo "🚀 Запуск в режиме разработки..."
	docker-compose up -d database redis backend
	@echo "✅ Бэкенд запущен на http://localhost:8000"
	@echo "💡 Для фронтенда используйте: cd mythic-frontend && npm run dev"

prod:
	@echo "🚀 Запуск в production режиме..."
	docker-compose --profile production up -d

# 🛠️ Дополнительные команды
shell-be:
	@echo "🛠️ Подключение к контейнеру бэкенда..."
	docker-compose exec backend bash

shell-fe:
	@echo "🛠️ Подключение к контейнеру фронтенда..."
	docker-compose exec frontend sh

install:
	@echo "📦 Первоначальная настройка..."
	@echo "1. Создаем .env файл..."
	@cp .env.example .env 2>/dev/null || echo "⚠️ Создайте файл .env на основе DOCKER_README.md"
	@echo "2. Создаем директории..."
	@mkdir -p mythic_backend/data mythic_backend/static backups
	@echo "3. Пересборка и запуск..."
	@make rebuild
	@echo "4. Выполнение миграций..."
	@sleep 10
	@make migrate
	@echo "✅ Установка завершена!"
	@echo "🌐 Откройте http://localhost:3000"

# Показать текущие переменные окружения
env:
	@echo "🔧 Переменные окружения:"
	@docker-compose config | grep -E "(OPENAI|GEMINI|APIFY|CLERK)" || echo "⚠️ Переменные не найдены" 