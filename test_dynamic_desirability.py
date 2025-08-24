#!/usr/bin/env python3

import sys
import os
import json

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), 'dynamic_desirability'))

from dynamic_desirability.desirability_retrieval import calculate_total_weights

def test_dynamic_desirability():
    """Тестируем Dynamic Desirability с исправлениями"""
    
    print("🧪 Тестируем Dynamic Desirability...")
    
    # Создаем тестовые данные валидатора
    test_validator_data = {
        "5CzCCUzF3h5Eq3fNAr696YGRZvETYTnUHDcL16C3c9cpmbtE": {
            "percent_stake": 1.0,
            "json": [
                {
                    "id": "test_1",
                    "params": {
                        "keyword": "cognitive longevity",
                        "platform": "x",
                        "label": None,
                        "post_start_datetime": None,
                        "post_end_datetime": None
                    },
                    "weight": 1.0
                },
                {
                    "id": "test_2", 
                    "params": {
                        "keyword": "bitcoin",
                        "platform": "reddit",
                        "label": None,
                        "post_start_datetime": None,
                        "post_end_datetime": None
                    },
                    "weight": 1.0
                }
            ]
        }
    }
    
    try:
        # Вызываем функцию calculate_total_weights
        calculate_total_weights(
            validator_data=test_validator_data,
            default_json_path='dynamic_desirability/default.json',
            total_vali_weight=0.7
        )
        
        # Проверяем результат
        with open('dynamic_desirability/total.json', 'r') as f:
            data = json.load(f)
            
        print(f"✅ Dynamic Desirability работает!")
        print(f"📊 Всего записей: {len(data)}")
        
        # Проверяем валидаторские темы
        validator_topics = [item for item in data if not item['id'].startswith('default_')]
        print(f"🎯 Темы от валидаторов: {len(validator_topics)}")
        
        for i, item in enumerate(validator_topics[:5]):
            print(f"   {i+1}. {item['id']} - {item['params']['label']} (вес: {item['weight']})")
            
        if len(validator_topics) > 0:
            print("🎉 УСПЕХ! Валидаторские темы добавлены!")
        else:
            print("❌ Проблема: валидаторские темы не добавлены")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dynamic_desirability()
