#!/usr/bin/env python3
"""
Скрипт для получения трендовых тем с дашборда Macrocosm
и объединения их с Dynamic Desirability темами
"""

import asyncio
import aiohttp
import json
import re
from datetime import datetime
from typing import List, Dict, Set

# URL дашборда Macrocosm
DASHBOARD_URL = "https://sn13-dashboard.api.macrocosmos.ai/"

async def fetch_dashboard_topics() -> List[str]:
    """Получает трендовые темы с дашборда Macrocosm"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(DASHBOARD_URL, timeout=30) as response:
                if response.status == 200:
                    html_content = await response.text()
                    
                    # Ищем популярные темы/хэштеги в HTML контенте
                    topics = set()
                    
                    # Поиск хэштегов
                    hashtag_pattern = r'#([a-zA-Z0-9_]+)'
                    hashtags = re.findall(hashtag_pattern, html_content)
                    for hashtag in hashtags:
                        if len(hashtag) > 2:  # Исключаем слишком короткие
                            topics.add(f"#{hashtag.lower()}")
                    
                    # Поиск популярных терминов
                    keyword_patterns = [
                        r'\b(AI|artificial intelligence|machine learning|blockchain|crypto|bitcoin|ethereum|defi|web3|nft)\b',
                        r'\b(tesla|spacex|neuralink|openai|chatgpt|claude|gemini)\b',
                        r'\b(trump|harris|biden|politics|election|ukraine|israel|gaza)\b',
                        r'\b(stock|market|trading|investment|economy|inflation)\b',
                        r'\b(climate|environment|renewable|energy|sustainability)\b'
                    ]
                    
                    for pattern in keyword_patterns:
                        matches = re.findall(pattern, html_content, re.IGNORECASE)
                        for match in matches:
                            topics.add(match.lower())
                    
                    return list(topics)[:10]  # Топ 10 тем
                else:
                    print(f"❌ Ошибка получения дашборда: HTTP {response.status}")
                    return []
    except Exception as e:
        print(f"❌ Ошибка подключения к дашборду: {e}")
        return []

def get_gravity_topics() -> List[str]:
    """Извлекает темы из Dynamic Desirability"""
    try:
        with open('dynamic_desirability/total.json', 'r') as f:
            gravity_data = json.load(f)
        
        topics = []
        for item in gravity_data:
            if item.get('weight', 0) >= 0.8:  # Только темы с высоким весом
                label = item['params'].get('label', '')
                if label:
                    # Для Reddit убираем r/
                    if label.startswith('r/'):
                        topics.append(label[2:])
                    # Для X убираем #
                    elif label.startswith('#'):
                        topics.append(label[1:])
                    else:
                        topics.append(label)
        
        return topics
    except Exception as e:
        print(f"❌ Ошибка чтения gravity тем: {e}")
        return []

def create_combined_keywords(dashboard_topics: List[str], gravity_topics: List[str]) -> List[str]:
    """Объединяет темы с дашборда и gravity, добавляет связанные термины"""
    
    combined = set()
    
    # Добавляем темы с дашборда
    for topic in dashboard_topics:
        combined.add(topic.lower().replace('#', ''))
    
    # Добавляем gravity темы
    for topic in gravity_topics:
        combined.add(topic.lower())
    
    # Добавляем синонимы и связанные термины
    enhanced_topics = set()
    
    for topic in combined:
        enhanced_topics.add(topic)
        
        # Добавляем связанные термины
        if topic in ['bitcoin', 'btc']:
            enhanced_topics.update(['bitcoin', 'btc', 'cryptocurrency', 'crypto'])
        elif topic in ['ai', 'artificial intelligence']:
            enhanced_topics.update(['ai', 'artificialintelligence', 'machinelearning', 'deeplearning'])
        elif topic in ['tesla', 'ev', 'electric']:
            enhanced_topics.update(['tesla', 'electricvehicle', 'ev', 'electriccar'])
        elif topic in ['climate', 'environment']:
            enhanced_topics.update(['climatechange', 'environment', 'sustainability', 'greenenergy'])
        elif topic in ['defi', 'decentralizedfinance']:
            enhanced_topics.update(['defi', 'decentralizedfinance', 'blockchain'])
        elif topic in ['trump', 'politics']:
            enhanced_topics.update(['trump', 'politics', 'election', 'harris'])
        elif topic in ['ukraine', 'war']:
            enhanced_topics.update(['ukraine', 'russia', 'war', 'conflict'])
        elif topic in ['israel', 'gaza']:
            enhanced_topics.update(['israel', 'gaza', 'palestine', 'conflict'])
    
    # Фильтруем и сортируем
    final_topics = []
    for topic in sorted(enhanced_topics):
        if len(topic) >= 3:  # Исключаем слишком короткие
            final_topics.append(topic)
    
    return final_topics[:25]  # Ограничиваем до 25 тем

async def update_scraping_config():
    """Обновляет конфигурацию скрапинга с новыми темами"""
    
    print("🔍 Получение трендовых тем с дашборда Macrocosm...")
    dashboard_topics = await fetch_dashboard_topics()
    print(f"📊 Найдено тем с дашборда: {len(dashboard_topics)}")
    
    print("🎯 Получение тем из Dynamic Desirability...")
    gravity_topics = get_gravity_topics()
    print(f"⚖️ Найдено gravity тем: {len(gravity_topics)}")
    
    print("🔀 Объединение и улучшение списка тем...")
    combined_keywords = create_combined_keywords(dashboard_topics, gravity_topics)
    
    print(f"✅ Итоговый список ({len(combined_keywords)} тем):")
    for i, keyword in enumerate(combined_keywords, 1):
        print(f"  {i:2d}. {keyword}")
    
    # Обновляем config.json для twikit_scraper
    config_path = "config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        config['search_keywords'] = combined_keywords
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Обновлен {config_path}")
        
    except Exception as e:
        print(f"❌ Ошибка обновления {config_path}: {e}")
    
    # Обновляем scraping_config_gravity.json для основного майнера
    scraping_config_path = "scraping_config_gravity.json"
    try:
        with open(scraping_config_path, 'r', encoding='utf-8') as f:
            scraping_config = json.load(f)
        
        # Обновляем Twitter labels
        for scraper in scraping_config.get('scrapers', []):
            if scraper.get('provider') == 'X.microworlds':
                scraper['labels_to_scrape'] = combined_keywords
            elif scraper.get('provider') == 'Reddit.custom':
                # Для Reddit используем r/ префикс для некоторых тем
                reddit_labels = []
                for keyword in combined_keywords:
                    if keyword in ['bitcoin', 'cryptocurrency', 'politics', 'worldnews', 'technology']:
                        reddit_labels.append(f"r/{keyword}")
                    else:
                        reddit_labels.append(keyword)
                scraper['labels_to_scrape'] = reddit_labels[:15]  # Ограничиваем для Reddit
        
        with open(scraping_config_path, 'w', encoding='utf-8') as f:
            json.dump(scraping_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Обновлен {scraping_config_path}")
        
    except Exception as e:
        print(f"❌ Ошибка обновления {scraping_config_path}: {e}")
    
    print(f"\n🎯 **ИТОГ:** Создан улучшенный список из {len(combined_keywords)} тем")
    print("📈 Включает: Dashboard trends + Gravity topics + синонимы")
    print("🚀 Готово для деплоя на VPS!")

if __name__ == "__main__":
    asyncio.run(update_scraping_config())
