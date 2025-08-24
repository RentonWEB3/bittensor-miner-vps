#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функций валидации качества
без необходимости подключения к Twitter API
"""

import sys
import os

# Добавляем путь к нашему модулю
sys.path.append('.')

# Импортируем функции из улучшенного скрапера
from twikit_scraper_improved import (
    is_english, 
    is_spam_or_low_quality, 
    is_relevant_to_topic, 
    has_quality_indicators
)

class MockTweet:
    """Мок-объект для симуляции твита"""
    def __init__(self, text, likes=0, retweets=0):
        self.text = text
        self.favorite_count = likes
        self.retweet_count = retweets

def test_english_detection():
    """Тестируем определение английского языка"""
    print("=== Тест определения английского языка ===")
    
    test_cases = [
        ("This is a great electric vehicle announcement!", True),
        ("@haciykk Mıllet düşmüş geçim derdine devlet düşmüş", False),  # Турецкий
        ("भारत अब सिर्फ target सेट नहीं कर रहा", False),  # Хинди
        ("Electric cars are the future of transportation", True),
        ("123 !@# ???", False),  # Нет букв
        ("", False),  # Пустой
    ]
    
    for text, expected in test_cases:
        result = is_english(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text[:50]}...' -> {result} (ожидалось {expected})")

def test_spam_detection():
    """Тестируем определение спама"""
    print("\n=== Тест определения спама ===")
    
    test_cases = [
        ("Short", True),  # Слишком короткий
        ("@someone reply without context", True),  # Reply
        ("🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗", True),  # Много эмодзи
        ("aaaaaaaaaa repeated characters", True),  # Повторяющиеся символы
        ("#tag1 #tag2 #tag3 #tag4 #tag5 #tag6 #tag7", True),  # Много хэштегов
        ("This is a normal high-quality tweet about electric vehicles and their impact on environment", False),  # Нормальный
    ]
    
    for text, expected in test_cases:
        result = is_spam_or_low_quality(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text[:50]}...' -> {result} (ожидалось {expected})")

def test_relevance_detection():
    """Тестируем определение релевантности"""
    print("\n=== Тест определения релевантности ===")
    
    test_cases = [
        ("Tesla Model 3 is amazing electric vehicle", "ev", True),
        ("I love pizza and cats", "ev", False),
        ("Solar panels are great for renewable energy", "greenenergy", True),
        ("Climate change is affecting our planet", "climatechange", True),
        ("Just had lunch with friends", "sustainability", False),
        ("Battery technology is improving rapidly", "battery", True),
    ]
    
    for text, topic, expected in test_cases:
        result = is_relevant_to_topic(text, topic)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text[:30]}...' для '{topic}' -> {result} (ожидалось {expected})")

def test_quality_indicators():
    """Тестируем индикаторы качества"""
    print("\n=== Тест индикаторов качества ===")
    
    test_cases = [
        (MockTweet("Great tweet", likes=5, retweets=2), True),
        (MockTweet("Another great tweet", likes=0, retweets=3), True),
        (MockTweet("Low quality", likes=1, retweets=0), False),
        (MockTweet("No engagement", likes=0, retweets=0), False),
    ]
    
    for tweet, expected in test_cases:
        result = has_quality_indicators(tweet)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{tweet.text}' (❤️{tweet.favorite_count} 🔄{tweet.retweet_count}) -> {result} (ожидалось {expected})")

def main():
    """Запуск всех тестов"""
    print("🧪 Тестирование функций валидации качества\n")
    
    test_english_detection()
    test_spam_detection()
    test_relevance_detection()
    test_quality_indicators()
    
    print("\n✅ Тестирование завершено!")
    print("\nЕсли все тесты прошли успешно, можно переходить к деплою на VPS.")

if __name__ == "__main__":
    main()
