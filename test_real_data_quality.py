#!/usr/bin/env python3
"""
Тест качества валидации на реальных данных из normalized файлов
"""

import json
import sys
sys.path.append('.')

from twikit_scraper_improved import (
    is_english, 
    is_spam_or_low_quality, 
    is_relevant_to_topic, 
    is_valid_quality_tweet
)

class MockTweet:
    """Мок-объект твита на основе реальных данных"""
    def __init__(self, content_data):
        self.text = content_data.get('text', '')
        self.id = content_data.get('tweet_id', '12345')
        self.favorite_count = 0  # Примерные значения
        self.retweet_count = 0
        
def test_real_twitter_data():
    """Тестируем качество валидации на реальных твитах"""
    print("🧪 Анализ качества реальных Twitter данных")
    print("=" * 60)
    
    # Читаем последний файл с Twitter данными
    import os
    normalized_dir = "normalized"
    twitter_files = [f for f in os.listdir(normalized_dir) if f.startswith("twitter_") and f.endswith(".jsonl")]
    
    if not twitter_files:
        print("❌ Нет файлов Twitter для анализа")
        return
    
    # Берем последний файл
    latest_file = sorted(twitter_files)[-1]
    file_path = os.path.join(normalized_dir, latest_file)
    
    print(f"📁 Анализируем файл: {latest_file}")
    print("-" * 60)
    
    total_tweets = 0
    quality_tweets = 0
    issues_breakdown = {
        'not_english': 0,
        'spam_low_quality': 0,
        'not_relevant': 0,
        'low_engagement': 0,
        'passed_all_checks': 0
    }
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
                
            try:
                data = json.loads(line)
                content_json = json.loads(data['content'])
                tweet = MockTweet(content_json)
                topic = data['label']['name']
                
                total_tweets += 1
                text = tweet.text
                
                print(f"\n📝 Твит #{line_num}: {text[:100]}...")
                print(f"🏷️ Тема: {topic}")
                
                # Пошаговая проверка
                if not is_english(text):
                    print("❌ Не английский язык")
                    issues_breakdown['not_english'] += 1
                    continue
                    
                if is_spam_or_low_quality(text):
                    print("❌ Спам/низкое качество")
                    issues_breakdown['spam_low_quality'] += 1
                    continue
                    
                if not is_relevant_to_topic(text, topic):
                    print("❌ Не релевантно к теме")
                    issues_breakdown['not_relevant'] += 1
                    continue
                    
                print("✅ Прошел все проверки качества!")
                quality_tweets += 1
                issues_breakdown['passed_all_checks'] += 1
                
            except Exception as e:
                print(f"❌ Ошибка обработки строки {line_num}: {e}")
                continue
    
    # Статистика
    print("\n" + "=" * 60)
    print("📊 СТАТИСТИКА КАЧЕСТВА")
    print("=" * 60)
    print(f"📈 Всего твитов: {total_tweets}")
    print(f"✅ Качественных: {quality_tweets}")
    print(f"📉 Процент качества: {(quality_tweets/total_tweets*100):.1f}%" if total_tweets > 0 else "0%")
    
    print(f"\n🔍 Причины отклонения:")
    print(f"🌐 Не английский язык: {issues_breakdown['not_english']}")
    print(f"🗑️ Спам/низкое качество: {issues_breakdown['spam_low_quality']}")
    print(f"❌ Не релевантно: {issues_breakdown['not_relevant']}")
    print(f"✅ Прошли проверки: {issues_breakdown['passed_all_checks']}")
    
    if quality_tweets < total_tweets * 0.3:
        print(f"\n⚠️ ВНИМАНИЕ: Только {(quality_tweets/total_tweets*100):.1f}% твитов прошли проверку качества!")
        print("💡 Это объясняет низкие метрики майнера - валидаторы получают в основном некачественные данные")
    else:
        print(f"\n✅ Хорошо: {(quality_tweets/total_tweets*100):.1f}% твитов имеют высокое качество")

if __name__ == "__main__":
    test_real_twitter_data()
