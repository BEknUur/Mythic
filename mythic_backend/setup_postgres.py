#!/usr/bin/env python3
"""
Скрипт для настройки PostgreSQL базы данных для Mythic приложения
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, check=True):
    """Выполнить команду в терминале"""
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка выполнения команды: {command}")
        print(f"Код ошибки: {e.returncode}")
        print(f"Вывод: {e.stderr}")
        return None, e.stderr

def check_postgres_installed():
    """Проверить, установлен ли PostgreSQL"""
    stdout, stderr = run_command("psql --version", check=False)
    if stdout:
        print(f"✅ PostgreSQL найден: {stdout}")
        return True
    else:
        print("❌ PostgreSQL не найден")
        return False

def install_postgres_ubuntu():
    """Установить PostgreSQL на Ubuntu/Debian"""
    print("🔄 Устанавливаю PostgreSQL...")
    
    commands = [
        "sudo apt update",
        "sudo apt install -y postgresql postgresql-contrib",
        "sudo systemctl start postgresql",
        "sudo systemctl enable postgresql"
    ]
    
    for cmd in commands:
        print(f"Выполняю: {cmd}")
        stdout, stderr = run_command(cmd)
        if stderr and "error" in stderr.lower():
            print(f"⚠️ Предупреждение: {stderr}")

def setup_database():
    """Создать базу данных и пользователя"""
    print("\n🔄 Настраиваю базу данных...")
    
    # SQL команды для создания пользователя и базы данных
    sql_commands = """
    CREATE USER mythic_user WITH PASSWORD 'mythic_password';
    CREATE DATABASE mythic_db OWNER mythic_user;
    GRANT ALL PRIVILEGES ON DATABASE mythic_db TO mythic_user;
    ALTER USER mythic_user CREATEDB;
    """
    
    # Записываем SQL в временный файл
    sql_file = Path("/tmp/setup_mythic.sql")
    sql_file.write_text(sql_commands)
    
    # Выполняем SQL через sudo -u postgres
    cmd = f"sudo -u postgres psql -f {sql_file}"
    stdout, stderr = run_command(cmd, check=False)
    
    if "already exists" in stderr:
        print("✅ База данных и пользователь уже существуют")
    elif stderr and "error" in stderr.lower():
        print(f"❌ Ошибка создания БД: {stderr}")
        return False
    else:
        print("✅ База данных и пользователь созданы успешно")
    
    # Удаляем временный файл
    sql_file.unlink(missing_ok=True)
    return True

def test_connection():
    """Проверить подключение к базе данных"""
    print("\n🔄 Проверяю подключение к базе данных...")
    
    test_cmd = "PGPASSWORD=mythic_password psql -h localhost -U mythic_user -d mythic_db -c 'SELECT version();'"
    stdout, stderr = run_command(test_cmd, check=False)
    
    if stdout and "PostgreSQL" in stdout:
        print("✅ Подключение к базе данных успешно!")
        return True
    else:
        print(f"❌ Ошибка подключения: {stderr}")
        return False

def install_python_dependencies():
    """Установить Python зависимости"""
    print("\n🔄 Устанавливаю Python зависимости...")
    
    pip_cmd = f"{sys.executable} -m pip install asyncpg psycopg2-binary"
    stdout, stderr = run_command(pip_cmd)
    
    if stderr and "error" in stderr.lower():
        print(f"❌ Ошибка установки зависимостей: {stderr}")
        return False
    else:
        print("✅ Python зависимости установлены")
        return True

def create_env_file():
    """Создать .env файл"""
    print("\n🔄 Создаю .env файл...")
    
    env_content = """# База данных PostgreSQL
DATABASE_URL=postgresql://mythic_user:mythic_password@localhost:5432/mythic_db
ASYNC_DATABASE_URL=postgresql+asyncpg://mythic_user:mythic_password@localhost:5432/mythic_db

# Настройки Apify
APIFY_TOKEN=your_apify_token_here

# Настройки Clerk
CLERK_SECRET_KEY=your_clerk_secret_key

# Backend URL для веб-хуков
BACKEND_BASE=http://localhost:8000
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        env_file.write_text(env_content)
        print("✅ Файл .env создан")
    else:
        print("ℹ️ Файл .env уже существует")

def main():
    """Основная функция"""
    print("🚀 Настройка PostgreSQL для Mythic приложения\n")
    
    # Проверяем ОС
    if not os.path.exists("/etc/os-release"):
        print("❌ Этот скрипт предназначен для Linux")
        sys.exit(1)
    
    # Проверяем, установлен ли PostgreSQL
    if not check_postgres_installed():
        print("\n📦 PostgreSQL не найден. Устанавливаю...")
        install_postgres_ubuntu()
        
        if not check_postgres_installed():
            print("❌ Не удалось установить PostgreSQL")
            sys.exit(1)
    
    # Настраиваем базу данных
    if not setup_database():
        print("❌ Не удалось настроить базу данных")
        sys.exit(1)
    
    # Проверяем подключение
    if not test_connection():
        print("❌ Не удалось подключиться к базе данных")
        sys.exit(1)
    
    # Устанавливаем Python зависимости
    if not install_python_dependencies():
        print("❌ Не удалось установить Python зависимости")
        sys.exit(1)
    
    # Создаем .env файл
    create_env_file()
    
    print("\n🎉 Настройка завершена успешно!")
    print("\n📝 Следующие шаги:")
    print("1. Обновите токены в файле .env")
    print("2. Запустите миграции: alembic revision --autogenerate -m 'Initial migration'")
    print("3. Примените миграции: alembic upgrade head")
    print("4. Запустите приложение: uvicorn app.main:app --reload")

if __name__ == "__main__":
    main() 