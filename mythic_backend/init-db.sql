-- Инициализация базы данных Mythic
-- Этот файл выполняется при первом запуске PostgreSQL контейнера

-- Создание базы данных (если еще не создана)
SELECT 'CREATE DATABASE mythic' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'mythic')\gexec

-- Подключение к базе данных mythic
\c mythic;

-- Создание расширений
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Создание пользователя для приложения (если не существует)
DO $$ 
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'mythic') THEN
      CREATE USER mythic WITH PASSWORD 'mythic_password_2024';
   END IF;
END
$$;

-- Предоставление прав пользователю
GRANT ALL PRIVILEGES ON DATABASE mythic TO mythic;
GRANT ALL PRIVILEGES ON SCHEMA public TO mythic;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mythic;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mythic;

-- Создание основных таблиц (будет выполнено Alembic, но базовая структура на всякий случай)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clerk_user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255),
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS processing_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    clerk_user_id VARCHAR(255) NOT NULL,
    instagram_url TEXT,
    status VARCHAR(50) DEFAULT 'processing',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS books (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    clerk_user_id VARCHAR(255) NOT NULL,
    run_id VARCHAR(255),
    title VARCHAR(500) NOT NULL,
    profile_username VARCHAR(255),
    profile_full_name VARCHAR(255),
    has_pdf BOOLEAN DEFAULT FALSE,
    has_html BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для производительности
CREATE INDEX IF NOT EXISTS idx_users_clerk_user_id ON users(clerk_user_id);
CREATE INDEX IF NOT EXISTS idx_processing_sessions_run_id ON processing_sessions(run_id);
CREATE INDEX IF NOT EXISTS idx_processing_sessions_clerk_user_id ON processing_sessions(clerk_user_id);
CREATE INDEX IF NOT EXISTS idx_books_clerk_user_id ON books(clerk_user_id);
CREATE INDEX IF NOT EXISTS idx_books_run_id ON books(run_id);
CREATE INDEX IF NOT EXISTS idx_books_created_at ON books(created_at);

-- Функция для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггеры для автоматического обновления updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_books_updated_at ON books;
CREATE TRIGGER update_books_updated_at 
    BEFORE UPDATE ON books 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Комментарии к таблицам
COMMENT ON TABLE users IS 'Пользователи приложения Mythic';
COMMENT ON TABLE processing_sessions IS 'Сессии обработки Instagram профилей';
COMMENT ON TABLE books IS 'Созданные романтические книги пользователей';

-- Успешная инициализация
INSERT INTO users (clerk_user_id, email, username, first_name, last_name) 
VALUES ('system', 'system@mythic.app', 'system', 'System', 'User')
ON CONFLICT (clerk_user_id) DO NOTHING;

-- Логирование успешной инициализации
DO $$ 
BEGIN
   RAISE NOTICE 'База данных Mythic успешно инициализирована!';
END
$$; 