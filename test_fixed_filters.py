#!/usr/bin/env python3
"""
Тест исправленных фильтров (менее строгих)
"""

import sys
sys.path.append('.')

from twikit_scraper import (
    is_english_basic, 
    is_basic_spam, 
    is_relevant_basic, 
    is_valid_quality_tweet,
    extract_hashtags,
    extract_urls
)

class MockTweet:
    def __init__(self, text, username="test_user", tweet_id="12345"):
        self.text = text
        self.username = username
        self.id = tweet_id

def test_fixed_filters():
    print("🧪 Тестирование исправленных фильтров (менее строгих)")
    print("=" * 60)
    
    # Тесты языка (менее строгие)
    print("\n📝 Тест языка (снижен порог до 60%):")
    test_cases = [
        ("Electric cars are the future", True),  # 100% английский
        ("Tesla Model 3 is amazing! 🚗", True),  # ~90% английский
        ("EV charging @TeslaMotors rocks!", True),  # ~85% английский
        ("Solar energy is clean power", True),  # 100% английский
        ("мы любим Tesla cars", False),  # ~50% английский - НЕ ПРОЙДЕТ
        ("できた〜。1個目より足長くなった。", False),  # Японский - НЕ ПРОЙДЕТ
    ]
    
    for text, expected in test_cases:
        result = is_english_basic(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}' -> {result}")
    
    # Тесты спама (только критичные случаи)
    print("\n🗑️ Тест спама (только критичные):")
    spam_cases = [
        ("Short", True),  # Меньше 10 символов - СПАМ
        ("Normal tweet about electric vehicles and future", False),  # Нормальный
        ("aaaaaaaaaaaaa spam", True),  # 10+ повторов - СПАМ 
        ("Tesla model 3 rocks", False),  # Нормальный
        ("#" * 11 + " too many hashtags", True),  # 11 хэштегов - СПАМ
        ("Great EV news #tesla #ev #green", False),  # 3 хэштега - ОК
    ]
    
    for text, expected in spam_cases:
        result = is_basic_spam(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text[:40]}...' -> {result}")
    
    # Тесты релевантности (расширенные синонимы)
    print("\n🎯 Тест релевантности (расширенные синонимы):")
    relevance_cases = [
        ("Tesla Model 3 is amazing", "tesla", True),  # Прямое упоминание
        ("Electric vehicle charging is fast", "ev", True),  # Синоним
        ("Solar power plants are efficient", "greenenergy", True),  # Синоним  
        ("Battery technology improves daily", "ev", True),  # Связанный термин
        ("I love pizza and cats", "ev", False),  # Не релевантно
        ("Unknown topic example", "unknowntopic", True),  # Нет синонимов = ОК
    ]
    
    for text, topic, expected in relevance_cases:
        result = is_relevant_basic(text, topic)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}' для '{topic}' -> {result}")
    
    # Тест извлечения данных
    print("\n🔍 Тест извлечения хэштегов и URL:")
    data_cases = [
        ("Great #Tesla #EV news!", ["#Tesla", "#EV"]),
        ("Check this https://twitter.com/tesla/status/123", ["https://twitter.com/tesla/status/123"]),
        ("Solar power #clean #energy https://example.com", ["#clean", "#energy"]),
    ]
    
    for text, expected_tags in data_cases:
        hashtags = extract_hashtags(text)
        urls = extract_urls(text)
        print(f"📝 '{text}'")
        print(f"   Хэштеги: {hashtags}")
        print(f"   URL: {urls}")
    
    # Общий тест валидации
    print("\n🎯 Общий тест валидации:")
    tweets = [
        MockTweet("Tesla Model 3 performance is incredible #EV"),
        MockTweet("Solar panels are getting more efficient"),
        MockTweet("Short"),  # Слишком короткий
        MockTweet("мы любим Tesla"),  # Не английский
        MockTweet("Electric vehicle charging infrastructure growing #EV #Tesla"),
    ]
    
    topics = ["tesla", "greenenergy", "ev", "ev", "ev"]
    
    for i, (tweet, topic) in enumerate(zip(tweets, topics)):
        result = is_valid_quality_tweet(tweet, topic)
        print(f"📋 Твит {i+1}: {result} - '{tweet.text}'")
    
    print(f"\n✅ Тестирование завершено!")
    print("🎯 Ожидается: увеличение проходимости с 14% до 60-80%")

if __name__ == "__main__":
    test_fixed_filters()
