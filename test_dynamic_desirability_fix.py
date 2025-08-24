#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправления Dynamic Desirability
"""

import json
import sys
import os

# Добавляем путь к модулям
sys.path.append('.')

def test_job_creation():
    """Тестируем создание объекта Job с правильными параметрами"""
    
    # Импортируем необходимые классы
    from dynamic_desirability.data import Job, JobParams
    
    # Тестовые данные
    test_job_data = {
        'id': 'test_job_1',
        'weight': 1.5,
        'params': {
            'keyword': 'bitcoin',
            'platform': 'reddit',
            'label': 'r/bitcoin',
            'post_start_datetime': '2025-08-24T00:00:00',
            'post_end_datetime': '2025-08-24T23:59:59'
        }
    }
    
    try:
        # Создаем JobParams
        job_params = JobParams(
            keyword=test_job_data['params'].get('keyword'),
            platform=test_job_data['params'].get('platform'),
            label=test_job_data['params'].get('label'),
            post_start_datetime=test_job_data['params'].get('post_start_datetime'),
            post_end_datetime=test_job_data['params'].get('post_end_datetime')
        )
        
        # Создаем Job
        job = Job(
            id=test_job_data['id'],
            weight=test_job_data['weight'],
            params=job_params
        )
        
        print("✅ Успешно создан объект Job:")
        print(f"   ID: {job.id}")
        print(f"   Weight: {job.weight}")
        print(f"   Platform: {job.params.platform}")
        print(f"   Label: {job.params.label}")
        print(f"   Keyword: {job.params.keyword}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании Job: {e}")
        return False

def test_job_validation():
    """Тестируем валидацию Job с различными данными"""
    
    from dynamic_desirability.data import Job, JobParams
    
    test_cases = [
        {
            'name': 'Валидные данные',
            'data': {
                'id': 'valid_job',
                'weight': 1.0,
                'params': {
                    'platform': 'reddit',
                    'label': 'r/bitcoin'
                }
            },
            'should_pass': True
        },
        {
            'name': 'Невалидный ID с слешем',
            'data': {
                'id': 'invalid/id',
                'weight': 1.0,
                'params': {
                    'platform': 'reddit',
                    'label': 'r/bitcoin'
                }
            },
            'should_pass': False
        },
        {
            'name': 'Невалидная платформа',
            'data': {
                'id': 'valid_job',
                'weight': 1.0,
                'params': {
                    'platform': 'invalid_platform',
                    'label': 'r/bitcoin'
                }
            },
            'should_pass': False
        }
    ]
    
    for test_case in test_cases:
        try:
            job_params = JobParams(**test_case['data']['params'])
            job = Job(**test_case['data'])
            
            if test_case['should_pass']:
                print(f"✅ {test_case['name']}: Успешно")
            else:
                print(f"❌ {test_case['name']}: Должен был упасть, но прошел")
                
        except Exception as e:
            if test_case['should_pass']:
                print(f"❌ {test_case['name']}: Упал, но должен был пройти - {e}")
            else:
                print(f"✅ {test_case['name']}: Ожидаемо упал - {e}")

if __name__ == "__main__":
    print("🧪 Тестирование исправления Dynamic Desirability\n")
    
    print("1. Тестирование создания Job:")
    test_job_creation()
    
    print("\n2. Тестирование валидации Job:")
    test_job_validation()
    
    print("\n✅ Тестирование завершено!")
    print("\n📝 Исправления:")
    print("   ✅ Исправлена модель Job в desirability_retrieval.py")
    print("   ✅ Исправлен union type для Python 3.9")
    print("   ✅ Добавлен правильный импорт JobParams")
    print("   ⚠️  JobMatcher требует совместимости со старой моделью Job")
