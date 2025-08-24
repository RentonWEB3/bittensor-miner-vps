#!/usr/bin/env python3
"""
Тест обязательных полей Reddit скрапера
"""

import sys
import json
import datetime as dt
sys.path.append('.')

# Импортируем Reddit модель
from scraping.reddit.model import RedditContent, RedditDataType

def test_reddit_required_fields():
    """Тестируем обязательные поля Reddit"""
    print("🧪 Тестирование обязательных полей Reddit")
    print("=" * 60)
    
    # Тестовые данные Reddit
    test_reddit_data = [
        {
            "id": "abc123",
            "url": "https://reddit.com/r/teslamotors/comments/abc123/tesla_model_3_review/",
            "username": "tesla_fan",
            "communityName": "r/teslamotors",
            "body": "Amazing review of the Tesla Model 3! The acceleration is incredible.",
            "createdAt": dt.datetime(2025, 8, 24, 15, 30, 0, tzinfo=dt.timezone.utc),
            "dataType": RedditDataType.POST,
            "title": "Tesla Model 3 Review - Incredible Performance",
            "media": ["https://i.redd.it/tesla_model_3.jpg"],
            "is_nsfw": False
        },
        {
            "id": "def456",
            "url": "https://reddit.com/r/electricvehicles/comments/def456/solar_panels_installation/",
            "username": "solar_expert",
            "communityName": "r/electricvehicles", 
            "body": "Just installed solar panels on my roof. The energy savings are incredible!",
            "createdAt": dt.datetime(2025, 8, 24, 16, 0, 0, tzinfo=dt.timezone.utc),
            "dataType": RedditDataType.POST,
            "title": "Solar Panels Installation Complete",
            "media": [],
            "is_nsfw": False
        },
        {
            "id": "ghi789",
            "url": "https://reddit.com/r/teslamotors/comments/ghi789/comment_on_tesla_post/",
            "username": "ev_enthusiast",
            "communityName": "r/teslamotors",
            "body": "Great post! Tesla is really leading the EV revolution.",
            "createdAt": dt.datetime(2025, 8, 24, 16, 30, 0, tzinfo=dt.timezone.utc),
            "dataType": RedditDataType.COMMENT,
            "parentId": "abc123",
            "media": [],
            "is_nsfw": False
        }
    ]
    
    for i, data in enumerate(test_reddit_data, 1):
        print(f"\n📝 Тест Reddit #{i}:")
        print(f"Тип: {data['dataType']}")
        print(f"Сообщество: {data['communityName']}")
        print(f"Username: {data['username']}")
        print(f"URL: {data['url']}")
        print(f"Текст: {data['body'][:50]}...")
        
        # Создаем RedditContent объект
        try:
            reddit_content = RedditContent(**data)
            print(f"✅ RedditContent создан успешно")
            
            # Проверяем обязательные поля
            required_fields = {
                "id": bool(reddit_content.id),
                "url": bool(reddit_content.url),
                "username": bool(reddit_content.username),
                "community": bool(reddit_content.community),
                "body": bool(reddit_content.body),
                "created_at": bool(reddit_content.created_at),
                "data_type": bool(reddit_content.data_type)
            }
            
            print(f"🔍 Обязательные поля:")
            for field, filled in required_fields.items():
                status = "✅" if filled else "❌"
                print(f"   {status} {field}: {'заполнено' if filled else 'ПУСТО!'}")
            
            # Проверяем специфичные поля
            if reddit_content.data_type == RedditDataType.POST:
                print(f"   📋 title: {reddit_content.title or 'НЕТ'}")
            elif reddit_content.data_type == RedditDataType.COMMENT:
                print(f"   📋 parent_id: {reddit_content.parent_id or 'НЕТ'}")
            
            # Создаем DataEntity
            data_entity = RedditContent.to_data_entity(reddit_content)
            print(f"✅ DataEntity создан: {data_entity.uri}")
            print(f"   Размер контента: {data_entity.content_size_bytes} байт")
            print(f"   Label: {data_entity.label.value}")
            
        except Exception as e:
            print(f"❌ Ошибка создания RedditContent: {e}")
    
    print(f"\n🎯 **ВАЖНО**: Reddit использует другую модель данных!")
    print("📚 Из scraping/reddit/model.py:")
    print("   Обязательные поля RedditContent:")
    print("   - id: str")
    print("   - url: str") 
    print("   - username: str")
    print("   - community: str")
    print("   - body: str")
    print("   - created_at: datetime")
    print("   - data_type: RedditDataType")
    print("\n✅ Reddit и Twitter используют разные модели - это нормально!")

def test_reddit_validation():
    """Тестируем валидацию Reddit URL"""
    print(f"\n🔍 Тестирование валидации Reddit URL:")
    
    from scraping.reddit.utils import is_valid_reddit_url
    
    test_urls = [
        "https://reddit.com/r/teslamotors/comments/abc123/tesla_model_3_review/",
        "https://www.reddit.com/r/electricvehicles/comments/def456/solar_panels/",
        "https://old.reddit.com/r/tesla/comments/ghi789/",
        "https://example.com/not_reddit",
        "invalid_url"
    ]
    
    for url in test_urls:
        is_valid = is_valid_reddit_url(url)
        status = "✅" if is_valid else "❌"
        print(f"{status} {url}")

if __name__ == "__main__":
    test_reddit_required_fields()
    test_reddit_validation()
