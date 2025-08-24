#!/usr/bin/env python3
"""
Быстрая диагностика майнера Macrocosmos
Проверяет основные параметры и выводит отчет в консоль
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
import subprocess
import requests

def check_registration():
    """Проверка регистрации майнера"""
    print("🔍 Проверка регистрации...")
    
    try:
        # Проверяем через btcli
        result = subprocess.run(
            ['btcli', 'subnets', 'list', '--subtensor.network', 'finney'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            output = result.stdout
            if 'netuid: 13' in output:
                print("✅ Майнер зарегистрирован в подсети 13")
                return True
            else:
                print("❌ Майнер не найден в подсети 13")
                return False
        else:
            print(f"❌ Ошибка при проверке регистрации: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ btcli не найден. Убедитесь, что Bittensor установлен")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def check_process_status():
    """Проверка статуса процесса"""
    print("🔍 Проверка статуса процесса...")
    
    try:
        result = subprocess.run(
            ['pm2', 'status'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            output = result.stdout
            if 'net13-miner' in output or 'miner' in output.lower():
                print("✅ Процесс майнера запущен")
                return True
            else:
                print("❌ Процесс майнера не найден")
                return False
        else:
            print("❌ PM2 не доступен")
            return False
            
    except FileNotFoundError:
        print("❌ PM2 не установлен")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def check_database():
    """Проверка базы данных"""
    print("🔍 Проверка базы данных...")
    
    try:
        db_path = Path("SqliteMinerStorage.sqlite")
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            print(f"✅ База данных найдена ({size_mb:.1f} MB)")
            
            # Проверяем, есть ли данные
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Проверяем количество записей
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
        else:
            print("❌ База данных не найдена")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при проверке БД: {e}")
        return False

def check_logs():
    """Проверка логов"""
    print("🔍 Проверка логов...")
    
    try:
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
        
        if not found_logs:
            print("❌ Логи не найдены")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке логов: {e}")
        return False

def check_network():
    """Проверка сетевого подключения"""
    print("🔍 Проверка сетевого подключения...")
    
    try:
        # Проверяем подключение к Bittensor
        result = subprocess.run(
            ['btcli', 'subnets', 'list', '--subtensor.network', 'finney'],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Подключение к Bittensor работает")
            return True
        else:
            print("❌ Проблемы с подключением к Bittensor")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Таймаут при подключении к Bittensor")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def check_config():
    """Проверка конфигурации"""
    print("🔍 Проверка конфигурации...")
    
    try:
        config_path = Path("scraping_config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            scraper_configs = config.get('scraper_configs', [])
            print(f"✅ Конфигурация найдена ({len(scraper_configs)} скраперов)")
            
            for i, scraper in enumerate(scraper_configs):
                scraper_id = scraper.get('scraper_id', 'unknown')
                cadence = scraper.get('cadence_seconds', 0)
                print(f"   📡 Скрапер {i+1}: {scraper_id} (каждые {cadence} сек)")
            
            return True
        else:
            print("❌ Файл конфигурации не найден")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при проверке конфигурации: {e}")
        return False

def check_dashboard():
    """Проверка доступности дашборда"""
    print("🔍 Проверка дашборда...")
    
    try:
        response = requests.get("https://sn13-dashboard.api.macrocosmos.ai/", timeout=10)
        if response.status_code == 200:
            print("✅ Дашборд Macrocosmos доступен")
            return True
        else:
            print(f"❌ Дашборд недоступен (статус: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при проверке дашборда: {e}")
        return False

def check_diagnostic_files():
    """Проверка файлов диагностики"""
    print("🔍 Проверка файлов диагностики...")
    
    try:
        diagnostic_dir = Path("diagnostics")
        if diagnostic_dir.exists():
            diagnostic_files = list(diagnostic_dir.glob("diagnostic_*.json"))
            
            if diagnostic_files:
                latest_file = max(diagnostic_files, key=lambda x: x.stat().st_mtime)
                print(f"✅ Файлы диагностики найдены ({len(diagnostic_files)} файлов)")
                
                # Читаем последний файл
                with open(latest_file, 'r', encoding='utf-8') as f:
                    diagnostic_data = json.load(f)
                
                issues = diagnostic_data.get('issues', [])
                warnings = diagnostic_data.get('warnings', [])
                
                if issues:
                    print(f"   ❌ Проблемы ({len(issues)}):")
                    for issue in issues[:3]:  # Показываем первые 3
                        print(f"      {issue}")
                
                if warnings:
                    print(f"   ⚠️ Предупреждения ({len(warnings)}):")
                    for warning in warnings[:3]:  # Показываем первые 3
                        print(f"      {warning}")
                
                return True
            else:
                print("❌ Файлы диагностики не найдены")
                return False
        else:
            print("❌ Папка диагностики не найдена")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при проверке файлов диагностики: {e}")
        return False

def generate_report(results):
    """Генерация отчета"""
    print("\n" + "="*50)
    print("📊 ОТЧЕТ ДИАГНОСТИКИ")
    print("="*50)
    
    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)
    
    print(f"Проверок выполнено: {total_checks}")
    print(f"Успешных: {passed_checks}")
    print(f"Проваленных: {total_checks - passed_checks}")
    print(f"Процент успеха: {(passed_checks/total_checks)*100:.1f}%")
    
    print("\n📋 Детали:")
    for check_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
    
    print("\n💡 Рекомендации:")
    
    if not results['registration']:
        print("  • Зарегистрируйте майнер: btcli subnets register --subtensor.network finney")
    
    if not results['process']:
        print("  • Запустите майнер: pm2 start python -- ./neurons/miner.py")
    
    if not results['database']:
        print("  • Проверьте настройки скрапинга в scraping_config.json")
    
    if not results['network']:
        print("  • Проверьте интернет-соединение")
    
    if results['logs'] and 'ERROR' in str(results['logs']):
        print("  • Проверьте логи на наличие ошибок")
    
    print("\n🌐 Полезные ссылки:")
    print("  • Дашборд: https://sn13-dashboard.api.macrocosmos.ai/")
    print("  • Документация: https://docs.macrocosmos.ai/")
    print("  • Discord: https://discord.gg/bittensor")

def main():
    parser = argparse.ArgumentParser(description="Быстрая диагностика майнера Macrocosmos")
    parser.add_argument("--save-report", action="store_true", help="Сохранить отчет в файл")
    
    args = parser.parse_args()
    
    print("🚀 Запуск быстрой диагностики майнера Macrocosmos...")
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Выполняем все проверки
    results = {
        'registration': check_registration(),
        'process': check_process_status(),
        'database': check_database(),
        'logs': check_logs(),
        'network': check_network(),
        'config': check_config(),
        'dashboard': check_dashboard(),
        'diagnostic_files': check_diagnostic_files()
    }
    
    # Генерируем отчет
    generate_report(results)
    
    # Сохраняем отчет если нужно
    if args.save_report:
        report_path = f"diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': results,
                'summary': {
                    'total_checks': len(results),
                    'passed_checks': sum(1 for result in results.values() if result),
                    'success_rate': (sum(1 for result in results.values() if result) / len(results)) * 100
                }
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Отчет сохранен в: {report_path}")
    
    # Возвращаем код выхода
    if all(results.values()):
        print("\n🎉 Все проверки пройдены успешно!")
        sys.exit(0)
    else:
        print("\n⚠️ Обнаружены проблемы. Проверьте рекомендации выше.")
        sys.exit(1)

if __name__ == "__main__":
    main()
