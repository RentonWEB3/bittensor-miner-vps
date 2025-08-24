#!/usr/bin/env python3.11
"""
Локальный тест конфигурации и скраперов
"""

import json
import sys
import os
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent))

def test_config_loading():
    """Тестируем загрузку конфигурации"""
    print("🔧 Тестируем загрузку конфигурации...")
    
    try:
        with open('scraping_config_test.json', 'r') as f:
            config = json.load(f)
        
        print("✅ Конфигурация загружена успешно")
        print(f"📊 Количество скраперов: {len(config['scraper_configs'])}")
        
        for i, scraper in enumerate(config['scraper_configs']):
            print(f"  {i+1}. {scraper['scraper_id']}")
            print(f"     Темы: {scraper['labels_to_scrape'][0]['label_choices'][:3]}...")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return False

def test_pydantic_models():
    """Тестируем Pydantic модели"""
    print("\n🔧 Тестируем Pydantic модели...")
    
    try:
        from scraping.config.model import ScrapingConfig
        
        with open('scraping_config_test.json', 'r') as f:
            config_data = json.load(f)
        
        config = ScrapingConfig(**config_data)
        print("✅ Pydantic валидация прошла успешно")
        print(f"📊 Валидных скраперов: {len(config.scraper_configs)}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка Pydantic валидации: {e}")
        return False

def test_reddit_topics():
    """Тестируем темы Reddit"""
    print("\n🔧 Тестируем темы Reddit...")
    
    try:
        with open('scraping_config_test.json', 'r') as f:
            config = json.load(f)
        
        reddit_scraper = None
        for scraper in config['scraper_configs']:
            if scraper['scraper_id'] == 'Reddit.custom':
                reddit_scraper = scraper
                break
        
        if reddit_scraper:
            topics = reddit_scraper['labels_to_scrape'][0]['label_choices']
            print(f"✅ Найдено {len(topics)} тем для Reddit")
            
            # Проверяем наличие r/ префикса
            r_prefixed = [t for t in topics if t.startswith('r/')]
            print(f"📊 Тем с префиксом r/: {len(r_prefixed)}")
            
            if r_prefixed:
                print(f"   Примеры: {r_prefixed[:3]}")
            
            return True
        else:
            print("❌ Reddit скрапер не найден в конфигурации")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки тем Reddit: {e}")
        return False

def test_twitter_topics():
    """Тестируем темы Twitter"""
    print("\n🔧 Тестируем темы Twitter...")
    
    try:
        with open('scraping_config_test.json', 'r') as f:
            config = json.load(f)
        
        twitter_scraper = None
        for scraper in config['scraper_configs']:
            if scraper['scraper_id'] == 'X.microworlds':
                twitter_scraper = scraper
                break
        
        if twitter_scraper:
            topics = twitter_scraper['labels_to_scrape'][0]['label_choices']
            print(f"✅ Найдено {len(topics)} тем для Twitter")
            print(f"   Темы: {topics}")
            
            return True
        else:
            print("❌ Twitter скрапер не найден в конфигурации")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки тем Twitter: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Начинаем локальное тестирование конфигурации...\n")
    
    tests = [
        test_config_loading,
        test_pydantic_models,
        test_reddit_topics,
        test_twitter_topics
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Результаты тестирования: {passed}/{total} тестов прошли успешно")
    
    if passed == total:
        print("🎉 Все тесты прошли успешно! Конфигурация готова к использованию.")
        return True
    else:
        print("⚠️ Некоторые тесты не прошли. Требуется исправление.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
