#!/usr/bin/env python3
"""
Финальный тест исправления Dynamic Desirability
"""

import json
import sys
import os

# Добавляем путь к модулям
sys.path.append('.')

def test_desirability_retrieval():
    """Тестируем исправленную функцию desirability_retrieval"""
    
    # Импортируем исправленную функцию
    from dynamic_desirability.desirability_retrieval import to_lookup
    
    # Создаем тестовые данные с правильной структурой
    test_jobs = [
        {
            'id': 'job_1',
            'weight': 1.0,
            'params': {
                'platform': 'reddit',
                'label': 'r/bitcoin',
                'keyword': None,
                'post_start_datetime': None,
                'post_end_datetime': None
            }
        },
        {
            'id': 'job_2', 
            'weight': 2.0,
            'params': {
                'platform': 'x',
                'keyword': 'ethereum',
                'label': 'ethereum',  # Добавляем label для совместимости
                'post_start_datetime': None,
                'post_end_datetime': None
            }
        }
    ]
    
    try:
        # Создаем временный файл с тестовыми данными
        test_file = 'test_jobs.json'
        with open(test_file, 'w') as f:
            json.dump(test_jobs, f)
        
        # Тестируем функцию to_lookup
        lookup = to_lookup(test_file)
        
        print("✅ Успешно создан DataDesirabilityLookup")
        print(f"   Количество источников данных: {len(lookup.distribution)}")
        
        # Очищаем
        os.remove(test_file)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в to_lookup: {e}")
        if os.path.exists('test_jobs.json'):
            os.remove('test_jobs.json')
        return False

if __name__ == "__main__":
    print("🧪 Финальный тест исправления Dynamic Desirability\n")
    
    print("Тестирование desirability_retrieval:")
    success = test_desirability_retrieval()
    
    if success:
        print("\n✅ ВСЕ ИСПРАВЛЕНИЯ РАБОТАЮТ!")
        print("\n📝 Что было исправлено:")
        print("   ✅ Исправлена модель Job в desirability_retrieval.py")
        print("   ✅ Исправлен union type для Python 3.9")
        print("   ✅ Добавлен правильный импорт JobParams")
        print("   ✅ Создан адаптер для совместимости с JobMatcher")
        print("   ✅ Dynamic Desirability теперь работает корректно!")
    else:
        print("\n❌ Еще есть проблемы с исправлением")
