# Настройка Clerk для аутентификации

## 1. Создайте аккаунт в Clerk

1. Перейдите на [clerk.com](https://clerk.com) и создайте бесплатный аккаунт
2. Создайте новое приложение
3. Выберите провайдеров аутентификации (рекомендуется: Email, Google, GitHub)

## 2. Получите ключи API

В дашборде Clerk найдите:
- **Publishable Key** (начинается с `pk_test_` для тестового окружения)
- **Secret Key** (начинается с `sk_test_` для тестового окружения)

## 3. Настройте фронтенд

Создайте файл `.env` в папке `mythic-frontend/`:

```bash
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
```

## 4. Настройте бэкенд

Создайте файл `.env` в папке `mythic_backend/`:

```bash
CLERK_SECRET_KEY=sk_test_your_secret_key_here
CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
```

## 5. Установите зависимости бэкенда

```bash
cd mythic_backend
pip install python-jose[cryptography] requests
```

## 6. Перезапустите приложения

1. Перезапустите фронтенд:
```bash
cd mythic-frontend
npm run dev
```

2. Перезапустите бэкенд:
```bash
cd mythic_backend
python -m app.main
```

## Как это работает

- **Публичное создание**: Любой может создавать книги через форму
- **Защищенный просмотр**: Только авторизованные пользователи могут видеть процесс создания и результат
- **Безопасные ссылки**: Ссылки на книги содержат JWT токены для доступа

## Готово!

Теперь ваше приложение защищено аутентификацией Clerk. Пользователи должны войти в систему для просмотра своих книг. 