# 🚀 Быстрый запуск Mythic

## Что это?
Mythic - система для создания романтических книг-подарков на основе Instagram профилей.

## За 3 минуты

### 1️⃣ Создать .env файл
```bash
cp DOCKER_README.md .env
# Отредактируйте .env - добавьте свои API ключи
```

### 2️⃣ Запустить
```bash
# Если есть make
make up

# Или без make
docker-compose up -d
```

### 3️⃣ Открыть
- **Приложение**: http://localhost:3000
- **API**: http://localhost:8000/docs

## Команды

```bash
make help          # Показать все команды
make up            # Запустить все
make down          # Остановит все
make logs          # Посмотреть логи
make status        # Статус контейнеров
make clean         # Очистить кэш
```

## Первый раз?

```bash
make install       # Автоматическая настройка
```

## Проблемы?

1. **Порты заняты** - измените в `docker-compose.yaml`
2. **Нет прав** - добавьте себя в группу docker: `sudo usermod -aG docker $USER`
3. **Нет места** - `make clean-all`

## Что дальше?

Прочитайте подробную документацию в `DOCKER_README.md`

---
💝 Создавайте красивые книги для любимых! 