#!/usr/bin/env python3
"""
Автоматическое исправление проблем майнера Macrocosmos
Выполняет диагностику и автоматически исправляет найденные проблемы
"""

import argparse
import json
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path
import shutil

def run_command(command, check=True, capture_output=True):
    """Выполнение команды с обработкой ошибок"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=capture_output,
            text=True,
            timeout=60
        )
        if check and result.returncode != 0:
            print(f"❌ Ошибка выполнения команды: {command}")
            print(f"   {result.stderr}")
            return False, result.stderr
        return True, result.stdout
    except subprocess.TimeoutExpired:
        print(f"⏰ Таймаут выполнения команды: {command}")
        return False, "Timeout"
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False, str(e)

def check_and_fix_registration():
    """Проверка и исправление регистрации"""
    print("🔍 Проверка регистрации майнера...")
    
    success, output = run_command("btcli subnets list --subtensor.network finney")
    if not success:
        print("❌ Не удалось проверить регистрацию")
        return False
    
    if "netuid: 13" in output:
        print("✅ Майнер зарегистрирован в подсети 13")
        return True
    else:
        print("❌ Майнер не зарегистрирован в подсети 13")
        print("💡 Для регистрации выполните:")
        print("   btcli subnets register --subtensor.network finney --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY")
        return False

def check_and_fix_process():
    """Проверка и исправление процесса"""
    print("🔍 Проверка процесса майнера...")
    
    success, output = run_command("pm2 status")
    if not success:
        print("❌ PM2 не доступен")
        return False
    
    if "net13-miner" in output or "miner" in output.lower():
        print("✅ Процесс майнера запущен")
        return True
    else:
        print("❌ Процесс майнера не найден")
        print("💡 Запускаю майнер...")
        
        # Попытка запуска майнера
        success, output = run_command("pm2 start python -- ./neurons/miner.py --wallet.name your-wallet --wallet.hotkey your-hotkey")
        if success:
            print("✅ Майнер запущен")
            return True
        else:
            print("❌ Не удалось запустить майнер")
            return False

def check_and_fix_database():
    """Проверка и исправление базы данных"""
    print("🔍 Проверка базы данных...")
    
    db_path = Path("SqliteMinerStorage.sqlite")
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024 * 1024)
        print(f"✅ База данных найдена ({size_mb:.1f} MB)")
        
        # Проверяем, есть ли данные
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM data_entities")
            entity_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM data_entity_buckets")
            bucket_count = cursor.fetchone()[0]
            
            conn.close()
            
            print(f"   📊 Сущностей: {entity_count}")
            print(f"   📦 Бакетов: {bucket_count}")
            
            if entity_count > 0:
                return True
            else:
                print("⚠️ База данных пуста")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка при проверке БД: {e}")
            return False
    else:
        print("❌ База данных не найдена")
        return False

def check_and_fix_config():
    """Проверка и исправление конфигурации"""
    print("🔍 Проверка конфигурации...")
    
    config_path = Path("scraping_config.json")
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            scraper_configs = config.get('scraper_configs', [])
            print(f"✅ Конфигурация найдена ({len(scraper_configs)} скраперов)")
            
            for i, scraper in enumerate(scraper_configs):
                scraper_id = scraper.get('scraper_id', 'unknown')
                cadence = scraper.get('cadence_seconds', 0)
                print(f"   📡 Скрапер {i+1}: {scraper_id} (каждые {cadence} сек)")
            
            return True
        except Exception as e:
            print(f"❌ Ошибка при проверке конфигурации: {e}")
            return False
    else:
        print("❌ Файл конфигурации не найден")
        print("💡 Создаю базовую конфигурацию...")
        
        # Создаем базовую конфигурацию
        basic_config = {
            "scraper_configs": [
                {
                    "scraper_id": "X.microworlds",
                    "cadence_seconds": 300,
                    "labels_to_scrape": [
                        {
                            "label_choices": ["bitcoin", "ethereum", "bittensor"],
                            "max_age_hint_minutes": 1440,
                            "max_data_entities": 25
                        }
                    ],
                    "config": {
                        "cookies_path": "twitter_cookies.json"
                    }
                },
                {
                    "scraper_id": "Reddit.custom",
                    "cadence_seconds": 600,
                    "labels_to_scrape": [
                        {
                            "label_choices": ["Bitcoin", "ethereum", "CryptoCurrency"],
                            "max_age_hint_minutes": 1440,
                            "max_data_entities": 100
                        }
                    ],
                    "config": {
                        "subreddit": "all",
                        "limit_per_label": 50
                    }
                }
            ]
        }
        
        try:
            with open(config_path, 'w') as f:
                json.dump(basic_config, f, indent=2)
            print("✅ Базовая конфигурация создана")
            return True
        except Exception as e:
            print(f"❌ Ошибка при создании конфигурации: {e}")
            return False

def check_and_fix_env():
    """Проверка и исправление переменных окружения"""
    print("🔍 Проверка переменных окружения...")
    
    env_path = Path(".env")
    if env_path.exists():
        print("✅ Файл .env найден")
        
        # Проверяем основные переменные
        with open(env_path, 'r') as f:
            env_content = f.read()
        
        required_vars = [
            "APIFY_API_TOKEN",
            "REDDIT_CLIENT_ID", 
            "REDDIT_CLIENT_SECRET",
            "REDDIT_USERNAME",
            "REDDIT_PASSWORD"
        ]
        
        missing_vars = []
        for var in required_vars:
            if var not in env_content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️ Отсутствуют переменные: {', '.join(missing_vars)}")
            print("💡 Добавьте их в файл .env")
            return False
        else:
            print("✅ Все необходимые переменные окружения настроены")
            return True
    else:
        print("❌ Файл .env не найден")
        print("💡 Создаю шаблон .env...")
        
        env_template = """# Apify API Token
APIFY_API_TOKEN=your_apify_token_here

# Reddit API Credentials
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

# YouTube API Key (optional)
YOUTUBE_API_KEY=your_youtube_api_key

# HuggingFace Token (optional)
HUGGINGFACE_TOKEN=your_huggingface_token
"""
        
        try:
            with open(env_path, 'w') as f:
                f.write(env_template)
            print("✅ Шаблон .env создан")
            print("💡 Заполните переменные своими значениями")
            return False
        except Exception as e:
            print(f"❌ Ошибка при создании .env: {e}")
            return False

def check_and_fix_logs():
    """Проверка и исправление логов"""
    print("🔍 Проверка логов...")
    
    log_paths = [
        Path("logs/miner.log"),
        Path("logs/neurons.log"),
        Path("miner.log")
    ]
    
    found_logs = False
    for log_path in log_paths:
        if log_path.exists():
            found_logs = True
            print(f"✅ Логи найдены: {log_path}")
            
            # Проверяем последние ошибки
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    last_lines = lines[-20:]  # Последние 20 строк
                    
                    errors = [line for line in last_lines if 'ERROR' in line]
                    warnings = [line for line in last_lines if 'WARNING' in line]
                    
                    if errors:
                        print(f"   ⚠️ Последние ошибки ({len(errors)}):")
                        for error in errors[-3:]:
                            print(f"      {error.strip()}")
                    
                    if warnings:
                        print(f"   ⚠️ Последние предупреждения ({len(warnings)}):")
                        for warning in warnings[-3:]:
                            print(f"      {warning.strip()}")
                
                break
            except Exception as e:
                print(f"❌ Ошибка при чтении логов: {e}")
    
    if not found_logs:
        print("❌ Логи не найдены")
        print("💡 Создаю папку для логов...")
        
        try:
            Path("logs").mkdir(exist_ok=True)
            print("✅ Папка logs создана")
        except Exception as e:
            print(f"❌ Ошибка при создании папки logs: {e}")
    
    return True

def check_and_fix_dependencies():
    """Проверка и исправление зависимостей"""
    print("🔍 Проверка зависимостей...")
    
    # Проверяем основные пакеты
    required_packages = [
        "bittensor",
        "torch", 
        "numpy",
        "pandas",
        "requests",
        "flask"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Отсутствуют пакеты: {', '.join(missing_packages)}")
        print("💡 Устанавливаю зависимости...")
        
        success, output = run_command("pip install -e .")
        if success:
            print("✅ Зависимости установлены")
            return True
        else:
            print("❌ Ошибка при установке зависимостей")
            return False
    else:
        print("✅ Все зависимости установлены")
        return True

def restart_miner():
    """Перезапуск майнера"""
    print("🔄 Перезапуск майнера...")
    
    # Останавливаем майнер
    success, output = run_command("pm2 stop net13-miner", check=False)
    
    # Ждем немного
    time.sleep(5)
    
    # Запускаем майнер
    success, output = run_command("pm2 start python -- ./neurons/miner.py --wallet.name your-wallet --wallet.hotkey your-hotkey")
    if success:
        print("✅ Майнер перезапущен")
        return True
    else:
        print("❌ Ошибка при перезапуске майнера")
        return False

def main():
    parser = argparse.ArgumentParser(description="Автоматическое исправление проблем майнера Macrocosmos")
    parser.add_argument("--fix-all", action="store_true", help="Исправить все найденные проблемы")
    parser.add_argument("--restart", action="store_true", help="Перезапустить майнер")
    parser.add_argument("--check-only", action="store_true", help="Только проверить, не исправлять")
    
    args = parser.parse_args()
    
    print("🚀 Автоматическое исправление проблем майнера Macrocosmos...")
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Выполняем все проверки
    checks = {
        'registration': check_and_fix_registration(),
        'process': check_and_fix_process(),
        'database': check_and_fix_database(),
        'config': check_and_fix_config(),
        'env': check_and_fix_env(),
        'logs': check_and_fix_logs(),
        'dependencies': check_and_fix_dependencies()
    }
    
    # Подсчитываем результаты
    total_checks = len(checks)
    passed_checks = sum(1 for result in checks.values() if result)
    
    print("\n" + "="*50)
    print("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ")
    print("="*50)
    
    print(f"Проверок выполнено: {total_checks}")
    print(f"Успешных: {passed_checks}")
    print(f"Проваленных: {total_checks - passed_checks}")
    print(f"Процент успеха: {(passed_checks/total_checks)*100:.1f}%")
    
    print("\n📋 Детали:")
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
    
    # Если нужно исправить все проблемы
    if args.fix_all and not args.check_only:
        print("\n🔧 Исправление проблем...")
        
        if not checks['dependencies']:
            print("💡 Устанавливаю зависимости...")
            check_and_fix_dependencies()
        
        if not checks['config']:
            print("💡 Создаю конфигурацию...")
            check_and_fix_config()
        
        if not checks['env']:
            print("💡 Создаю .env файл...")
            check_and_fix_env()
        
        if not checks['process']:
            print("💡 Запускаю майнер...")
            check_and_fix_process()
    
    # Если нужно перезапустить майнер
    if args.restart and not args.check_only:
        restart_miner()
    
    # Рекомендации
    print("\n💡 Рекомендации:")
    
    if not checks['registration']:
        print("  • Зарегистрируйте майнер: btcli subnets register --subtensor.network finney")
    
    if not checks['env']:
        print("  • Заполните переменные в файле .env")
    
    if not checks['database']:
        print("  • Запустите майнер в offline режиме для накопления данных")
    
    if not checks['process']:
        print("  • Запустите майнер: pm2 start python -- ./neurons/miner.py")
    
    print("\n🌐 Полезные ссылки:")
    print("  • Дашборд: https://sn13-dashboard.api.macrocosmos.ai/")
    print("  • Документация: https://docs.macrocosmos.ai/")
    print("  • Discord: https://discord.gg/bittensor")
    
    # Возвращаем код выхода
    if all(checks.values()):
        print("\n🎉 Все проверки пройдены успешно!")
        sys.exit(0)
    else:
        print("\n⚠️ Обнаружены проблемы. Проверьте рекомендации выше.")
        sys.exit(1)

if __name__ == "__main__":
    main()
