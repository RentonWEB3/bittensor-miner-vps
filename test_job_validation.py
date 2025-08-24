#!/usr/bin/env python3

import json
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), 'rewards'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'dynamic_desirability'))

from rewards.data import Job, JobMatcher

def test_job_validation():
    """Тестируем валидацию Job с реальными данными"""
    
    # Загружаем данные из total.json
    try:
        with open('dynamic_desirability/total.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Файл total.json не найден")
        return
    
    print(f"📊 Загружено {len(data)} записей из total.json")
    
    # Тестируем первые 5 записей
    for i, item in enumerate(data[:5]):
        print(f"\n🔍 Тестируем запись {i+1}:")
        print(f"   ID: {item.get('id')}")
        print(f"   Weight: {item.get('weight')}")
        print(f"   Params: {item.get('params')}")
        
        try:
            # Создаем Job объект
            job = Job(
                id=item.get('id'),
                keyword=item.get('params', {}).get('keyword') or "",
                label=item.get('params', {}).get('label') or "default",
                job_weight=item.get('weight'),
                start_timebucket=None,
                end_timebucket=None
            )
            print(f"   ✅ Job создан успешно: {job}")
            
        except Exception as e:
            print(f"   ❌ Ошибка создания Job: {e}")
            print(f"   🔍 Типы данных:")
            print(f"      id: {type(item.get('id'))} = {item.get('id')}")
            print(f"      keyword: {type(item.get('params', {}).get('keyword'))} = {item.get('params', {}).get('keyword')}")
            print(f"      label: {type(item.get('params', {}).get('label'))} = {item.get('params', {}).get('label')}")
            print(f"      weight: {type(item.get('weight'))} = {item.get('weight')}")

if __name__ == "__main__":
    test_job_validation()
