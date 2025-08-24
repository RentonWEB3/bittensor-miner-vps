#!/usr/bin/env python3.11
"""
Полный аудит кода майнера
Проверяет соответствие требованиям валидаторов и выявляет ошибки
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
import importlib.util

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent))

class CodeAuditor:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0
        
        # Требования валидаторов
        self.twitter_required_fields = ["username", "text", "url", "tweet_hashtags"]
        self.reddit_required_fields = ["id", "url", "username", "communityName", "body", "createdAt", "dataType"]
        
    def log_issue(self, component: str, issue: str, severity: str = "ERROR"):
        """Логирует проблему"""
        self.issues.append({
            "component": component,
            "issue": issue,
            "severity": severity
        })
        print(f"❌ [{severity}] {component}: {issue}")
        
    def log_warning(self, component: str, warning: str):
        """Логирует предупреждение"""
        self.warnings.append({
            "component": component,
            "warning": warning
        })
        print(f"⚠️  {component}: {warning}")
        
    def log_success(self, component: str, message: str):
        """Логирует успех"""
        self.success_count += 1
        print(f"✅ {component}: {message}")
        
    def check_twitter_field_population(self) -> bool:
        """Проверяет правильность заполнения полей Twitter"""
        print("\n🔍 Проверяем заполнение полей Twitter...")
        
        try:
            # Проверяем twikit_scraper.py
            if Path("twikit_scraper.py").exists():
                with open("twikit_scraper.py", "r") as f:
                    content = f.read()
                
                # Проверяем наличие всех обязательных полей
                for field in self.twitter_required_fields:
                    if field not in content:
                        self.log_issue("Twitter Scraper", f"Отсутствует обязательное поле: {field}")
                        return False
                
                # Проверяем правильность заполнения content_json
                if "content_json" in content and "username" in content and "url" in content:
                    self.log_success("Twitter Scraper", "Все обязательные поля присутствуют")
                else:
                    self.log_issue("Twitter Scraper", "Неправильная структура content_json")
                    return False
                    
            else:
                self.log_issue("Twitter Scraper", "Файл twikit_scraper.py не найден")
                return False
                
        except Exception as e:
            self.log_issue("Twitter Scraper", f"Ошибка проверки: {e}")
            return False
            
        return True
        
    def check_reddit_field_population(self) -> bool:
        """Проверяет правильность заполнения полей Reddit"""
        print("\n🔍 Проверяем заполнение полей Reddit...")
        
        try:
            # Проверяем reddit_custom_scraper.py
            if Path("scraping/reddit/reddit_custom_scraper.py").exists():
                with open("scraping/reddit/reddit_custom_scraper.py", "r") as f:
                    content = f.read()
                
                # Проверяем использование правильных алиасов
                if "communityName" in content and "createdAt" in content and "dataType" in content:
                    self.log_success("Reddit Scraper", "Правильные алиасы полей используются")
                else:
                    self.log_issue("Reddit Scraper", "Неправильные алиасы полей")
                    return False
                    
            else:
                self.log_issue("Reddit Scraper", "Файл reddit_custom_scraper.py не найден")
                return False
                
        except Exception as e:
            self.log_issue("Reddit Scraper", f"Ошибка проверки: {e}")
            return False
            
        return True
        
    def check_config_validation(self) -> bool:
        """Проверяет валидацию конфигурации"""
        print("\n🔍 Проверяем валидацию конфигурации...")
        
        try:
            # Проверяем загрузку конфигурации
            if Path("scraping_config_test.json").exists():
                with open("scraping_config_test.json", "r") as f:
                    config = json.load(f)
                
                # Проверяем структуру
                if "scraper_configs" in config:
                    self.log_success("Config Validation", "Правильная структура конфигурации")
                    
                    # Проверяем каждый скрапер
                    for scraper in config["scraper_configs"]:
                        if "scraper_id" in scraper and "labels_to_scrape" in scraper:
                            self.log_success("Config Validation", f"Скрапер {scraper['scraper_id']} корректный")
                        else:
                            self.log_issue("Config Validation", f"Неправильная структура скрапера: {scraper}")
                            return False
                else:
                    self.log_issue("Config Validation", "Отсутствует scraper_configs в конфигурации")
                    return False
                    
            else:
                self.log_issue("Config Validation", "Файл конфигурации не найден")
                return False
                
        except Exception as e:
            self.log_issue("Config Validation", f"Ошибка валидации: {e}")
            return False
            
        return True
        
    def check_pydantic_models(self) -> bool:
        """Проверяет Pydantic модели"""
        print("\n🔍 Проверяем Pydantic модели...")
        
        try:
            # Проверяем модель RedditContent
            from scraping.reddit.model import RedditContent, RedditDataType
            
            # Тестируем создание объекта
            test_data = {
                "id": "test123",
                "url": "https://reddit.com/r/test/comments/test123/test_post/",
                "username": "testuser",
                "communityName": "r/test",
                "body": "Test post body",
                "createdAt": "2025-08-24T12:00:00Z",
                "dataType": "post"
            }
            
            reddit_content = RedditContent(**test_data)
            self.log_success("Pydantic Models", "RedditContent модель работает корректно")
            
            # Проверяем модель XContent
            try:
                from scraping.x.model import XContent
                self.log_success("Pydantic Models", "XContent модель доступна")
            except ImportError:
                self.log_warning("Pydantic Models", "XContent модель недоступна")
                
        except Exception as e:
            self.log_issue("Pydantic Models", f"Ошибка проверки моделей: {e}")
            return False
            
        return True
        
    def check_data_upload_format(self) -> bool:
        """Проверяет формат данных для загрузки"""
        print("\n🔍 Проверяем формат данных для загрузки...")
        
        try:
            # Проверяем HuggingFace uploader
            if Path("upload_utils/huggingface_uploader.py").exists():
                with open("upload_utils/huggingface_uploader.py", "r") as f:
                    content = f.read()
                
                # Проверяем правильность обработки данных
                # HuggingFace uploader использует SQL запросы к DataEntity
                if "DataEntity" in content and ("FROM DataEntity" in content or "SELECT" in content):
                    self.log_success("Data Upload", "Правильная обработка DataEntity через SQL")
                else:
                    self.log_issue("Data Upload", "Неправильная обработка DataEntity")
                    return False
                    
            else:
                self.log_issue("Data Upload", "HuggingFace uploader не найден")
                return False
                
        except Exception as e:
            self.log_issue("Data Upload", f"Ошибка проверки: {e}")
            return False
            
        return True
        
    def check_quality_filters(self) -> bool:
        """Проверяет качественные фильтры"""
        print("\n🔍 Проверяем качественные фильтры...")
        
        try:
            # Проверяем twikit_scraper.py на наличие фильтров
            if Path("twikit_scraper.py").exists():
                with open("twikit_scraper.py", "r") as f:
                    content = f.read()
                
                # Проверяем наличие базовых фильтров
                if "is_english_basic" in content or "is_basic_spam" in content:
                    self.log_success("Quality Filters", "Базовые фильтры качества присутствуют")
                else:
                    self.log_warning("Quality Filters", "Фильтры качества отсутствуют")
                    
            else:
                self.log_issue("Quality Filters", "Файл twikit_scraper.py не найден")
                return False
                
        except Exception as e:
            self.log_issue("Quality Filters", f"Ошибка проверки: {e}")
            return False
            
        return True
        
    def check_error_handling(self) -> bool:
        """Проверяет обработку ошибок"""
        print("\n🔍 Проверяем обработку ошибок...")
        
        try:
            # Проверяем основные файлы на наличие try-catch блоков
            files_to_check = [
                "twikit_scraper.py",
                "scraping/reddit/reddit_custom_scraper.py",
                "upload_utils/huggingface_uploader.py"
            ]
            
            for file_path in files_to_check:
                if Path(file_path).exists():
                    with open(file_path, "r") as f:
                        content = f.read()
                    
                    if "try:" in content and "except" in content:
                        self.log_success("Error Handling", f"Обработка ошибок в {file_path}")
                    else:
                        self.log_warning("Error Handling", f"Недостаточная обработка ошибок в {file_path}")
                else:
                    self.log_warning("Error Handling", f"Файл {file_path} не найден")
                    
        except Exception as e:
            self.log_issue("Error Handling", f"Ошибка проверки: {e}")
            return False
            
        return True
        
    def check_performance_optimization(self) -> bool:
        """Проверяет оптимизацию производительности"""
        print("\n🔍 Проверяем оптимизацию производительности...")
        
        try:
            # Проверяем настройки cadence
            if Path("scraping_config_test.json").exists():
                with open("scraping_config_test.json", "r") as f:
                    config = json.load(f)
                
                for scraper in config.get("scraper_configs", []):
                    cadence = scraper.get("cadence_seconds", 0)
                    if 300 <= cadence <= 3600:  # 5 минут - 1 час
                        self.log_success("Performance", f"Оптимальный cadence: {cadence}s")
                    else:
                        self.log_warning("Performance", f"Неоптимальный cadence: {cadence}s")
                        
        except Exception as e:
            self.log_issue("Performance", f"Ошибка проверки: {e}")
            return False
            
        return True
        
    def run_full_audit(self) -> Dict[str, Any]:
        """Запускает полный аудит"""
        print("🚀 Начинаем полный аудит кода майнера...\n")
        
        checks = [
            ("Twitter Field Population", self.check_twitter_field_population),
            ("Reddit Field Population", self.check_reddit_field_population),
            ("Config Validation", self.check_config_validation),
            ("Pydantic Models", self.check_pydantic_models),
            ("Data Upload Format", self.check_data_upload_format),
            ("Quality Filters", self.check_quality_filters),
            ("Error Handling", self.check_error_handling),
            ("Performance Optimization", self.check_performance_optimization)
        ]
        
        results = {}
        
        for check_name, check_func in checks:
            self.total_checks += 1
            try:
                result = check_func()
                results[check_name] = result
            except Exception as e:
                self.log_issue(check_name, f"Критическая ошибка: {e}")
                results[check_name] = False
        
        # Формируем отчет
        report = {
            "summary": {
                "total_checks": self.total_checks,
                "successful_checks": self.success_count,
                "issues_found": len(self.issues),
                "warnings_found": len(self.warnings)
            },
            "issues": self.issues,
            "warnings": self.warnings,
            "results": results
        }
        
        return report
        
    def print_report(self, report: Dict[str, Any]):
        """Выводит отчет об аудите"""
        print("\n" + "="*60)
        print("📊 ОТЧЕТ ОБ АУДИТЕ КОДА")
        print("="*60)
        
        summary = report["summary"]
        print(f"📈 Всего проверок: {summary['total_checks']}")
        print(f"✅ Успешных: {summary['successful_checks']}")
        print(f"❌ Проблем: {summary['issues_found']}")
        print(f"⚠️  Предупреждений: {summary['warnings_found']}")
        
        if report["issues"]:
            print("\n🚨 КРИТИЧЕСКИЕ ПРОБЛЕМЫ:")
            for issue in report["issues"]:
                print(f"  • {issue['component']}: {issue['issue']}")
                
        if report["warnings"]:
            print("\n⚠️  ПРЕДУПРЕЖДЕНИЯ:")
            for warning in report["warnings"]:
                print(f"  • {warning['component']}: {warning['warning']}")
                
        # Рекомендации
        print("\n🎯 РЕКОМЕНДАЦИИ:")
        if summary['issues_found'] > 0:
            print("  1. Исправьте критические проблемы перед запуском")
            print("  2. Проверьте заполнение всех обязательных полей")
            print("  3. Убедитесь в правильности структуры данных")
        else:
            print("  1. Код готов к тестированию")
            print("  2. Запустите локальные тесты")
            print("  3. Проверьте работу на сервере")
            
        print("="*60)

def main():
    """Основная функция"""
    auditor = CodeAuditor()
    report = auditor.run_full_audit()
    auditor.print_report(report)
    
    # Возвращаем код выхода
    if report["summary"]["issues_found"] > 0:
        return 1
    else:
        return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
