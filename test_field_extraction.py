#!/usr/bin/env python3
"""
Тест извлечения обязательных полей без подключения к Twitter API
"""

import sys
import re
import json

sys.path.append('.')

from twikit_scraper import extract_hashtags, extract_urls

class MockTweet:
    """Мок твита для тестирования"""
    def __init__(self, text, username="test_user", tweet_id="1234567890"):
        self.text = text
        self.id = tweet_id
        self.username = username
        # Мок user объекта
        self.user = MockUser(username, f"Display {username}", verified=False)

class MockUser:
    def __init__(self, username, name, verified=False):
        self.username = username
        self.name = name
        self.verified = verified

def test_field_extraction():
    """Тестируем извлечение обязательных полей"""
    print("🧪 Тестирование извлечения обязательных полей")
    print("=" * 60)
    
    # Тестовые твиты
    test_tweets = [
        MockTweet(
            "Great news about #Tesla Model 3! Electric vehicles are the future. #EV #CleanEnergy https://tesla.com/model3",
            "elonmusk",
            "1234567890123456789"
        ),
        MockTweet(
            "Solar panels becoming more efficient every year! Check this: https://example.com/solar #Solar #GreenEnergy",
            "solar_expert",
            "9876543210987654321"
        ),
        MockTweet(
            "Battery technology breakthrough announced today",
            "tech_news",
            "5555555555555555555"
        )
    ]
    
    for i, tweet in enumerate(test_tweets, 1):
        print(f"\n📝 Тест твита #{i}:")
        print(f"Текст: {tweet.text}")
        
        # Извлекаем хэштеги
        hashtags = extract_hashtags(tweet.text)
        print(f"✅ Хэштеги: {hashtags}")
        
        # Извлекаем URL
        urls = extract_urls(tweet.text)
        tweet_url = urls[0] if urls else f"https://twitter.com/i/web/status/{tweet.id}"
        print(f"✅ URL: {tweet_url}")
        
        # Получаем username
        username = getattr(tweet, 'username', '') or getattr(tweet.user, 'username', '') if hasattr(tweet, 'user') else ''
        print(f"✅ Username: {username}")
        
        # Проверяем обязательные поля
        required_fields_filled = {
            "text": bool(tweet.text.strip()),
            "tweet_hashtags": len(hashtags) > 0 or True,  # Может быть пустым
            "username": bool(username),
            "url": bool(tweet_url)
        }
        
        print(f"🔍 Обязательные поля:")
        for field, filled in required_fields_filled.items():
            status = "✅" if filled else "❌"
            print(f"   {status} {field}: {'заполнено' if filled else 'ПУСТО!'}")
        
        # Симулируем JSON контент
        content_json = {
            "text": tweet.text,
            "tweet_hashtags": hashtags,
            "username": username,
            "url": tweet_url,
            "timestamp": "2025-08-24T15:30:00Z",
            "user_id": str(tweet.id),
            "user_display_name": getattr(tweet.user, 'name', '') if hasattr(tweet, 'user') else '',
            "user_verified": getattr(tweet.user, 'verified', False) if hasattr(tweet, 'user') else False,
            "tweet_id": str(tweet.id),
            "is_reply": False,
            "is_quote": False,
            "conversation_id": "",
            "in_reply_to_user_id": "",
            "media": []
        }
        
        print(f"📋 JSON контент (обрезано):")
        for key in ["text", "tweet_hashtags", "username", "url"]:
            value = content_json[key]
            print(f"   {key}: {value}")
    
    print(f"\n🎯 **ВАЖНО**: Все обязательные поля должны быть заполнены!")
    print("📚 Из документации scraping/x/utils.py:")
    print("   REQUIRED_FIELDS = [")
    print("       ('username', 'usernames'),")
    print("       ('text', 'texts'),")
    print("       ('url', 'urls'),")
    print("       ('tweet_hashtags', 'hashtags'),")
    print("   ]")
    print("\n✅ Если все поля заполняются правильно - можно деплоить на VPS!")

def test_regex_extraction():
    """Тестируем регулярные выражения"""
    print(f"\n🔍 Тестирование регулярных выражений:")
    
    test_cases = [
        "Check out #Tesla and #EV news at https://tesla.com/news",
        "Solar power #renewable #energy https://example.com/solar and https://another.com",
        "No hashtags or links here",
        "#SingleHashtag only",
        "Just a link: https://test.com",
    ]
    
    for text in test_cases:
        hashtags = extract_hashtags(text)
        urls = extract_urls(text)
        print(f"📝 '{text}'")
        print(f"   🏷️ Хэштеги: {hashtags}")
        print(f"   🔗 URLs: {urls}")

if __name__ == "__main__":
    test_field_extraction()
    test_regex_extraction()
