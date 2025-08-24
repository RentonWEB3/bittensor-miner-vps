import os
import json
import asyncio
import traceback
import re
from datetime import datetime
from typing import Dict, Any

try:
    from twikit import Client, errors as twikit_errors
except ImportError:  # pragma: no cover - twikit may not be installed during tests
    Client = None

    class _DummyTwikitErrors:
        NotFound = Exception

    twikit_errors = _DummyTwikitErrors()

CONFIG_PATH = "config.json"

def load_config():
    return json.load(open(CONFIG_PATH, "r", encoding="utf-8"))

def is_english(text: str) -> bool:
    """Проверяет, является ли текст преимущественно английским"""
    # Подсчет английских символов
    english_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
    total_chars = sum(1 for c in text if c.isalpha())
    
    if total_chars == 0:
        return False
    
    # Минимум 80% английских символов
    return (english_chars / total_chars) >= 0.8

def has_quality_indicators(tweet) -> bool:
    """Проверяет индикаторы качества твита"""
    try:
        # Минимальное количество лайков или ретвитов для качественного контента
        likes = getattr(tweet, 'favorite_count', 0) or getattr(tweet, 'likes', 0) or 0
        retweets = getattr(tweet, 'retweet_count', 0) or getattr(tweet, 'retweets', 0) or 0
        
        # Качественный твит должен иметь минимальную активность
        return likes >= 2 or retweets >= 1
    except:
        # Если не можем получить метрики, пропускаем этот фильтр
        return True

def is_spam_or_low_quality(text: str) -> bool:
    """Определяет спам или низкокачественный контент"""
    # Слишком короткий текст
    if len(text.strip()) < 30:
        return True
    
    # Начинается с @ (reply без контекста)
    if text.strip().startswith('@'):
        return True
    
    # Слишком много эмодзи или спецсимволов
    emoji_pattern = re.compile(r'[^\w\s.,!?;:\'"()-]', re.UNICODE)
    special_chars = len(emoji_pattern.findall(text))
    if special_chars > len(text) * 0.3:  # Более 30% спецсимволов
        return True
    
    # Повторяющиеся символы (спам)
    if re.search(r'(.)\1{4,}', text):  # 5+ одинаковых символов подряд
        return True
    
    # Слишком много хэштегов
    hashtag_count = len(re.findall(r'#\w+', text))
    if hashtag_count > 5:
        return True
    
    return False

def is_relevant_to_topic(text: str, topic: str) -> bool:
    """Проверяет релевантность твита к теме"""
    text_lower = text.lower()
    topic_lower = topic.lower()
    
    # Прямое упоминание темы
    if topic_lower in text_lower:
        return True
    
    # Синонимы и связанные термы для основных тем
    topic_synonyms = {
        'ev': ['electric vehicle', 'electric car', 'tesla', 'battery', 'charging', 'bev'],
        'tesla': ['model s', 'model 3', 'model x', 'model y', 'cybertruck', 'elon musk'],
        'sustainability': ['renewable', 'green energy', 'climate', 'carbon', 'eco'],
        'greenenergy': ['solar', 'wind', 'renewable', 'clean energy', 'sustainable'],
        'renewableenergy': ['solar power', 'wind power', 'clean energy', 'green'],
        'climatechange': ['global warming', 'carbon emission', 'greenhouse', 'climate'],
        'battery': ['lithium', 'charging', 'energy storage', 'battery tech'],
        'charging': ['supercharger', 'fast charging', 'ev charging', 'charge station']
    }
    
    synonyms = topic_synonyms.get(topic_lower, [])
    for synonym in synonyms:
        if synonym in text_lower:
            return True
    
    return False

def is_valid_quality_tweet(tweet, topic: str) -> bool:
    """Комплексная валидация качества твита"""
    try:
        text = getattr(tweet, "text", "").strip()
        
        # Базовая проверка - есть ли текст
        if not text:
            return False
        
        # Проверка языка (только английский)
        if not is_english(text):
            print(f"[FILTER] Не английский язык: {text[:50]}...")
            return False
        
        # Проверка на спам и низкое качество
        if is_spam_or_low_quality(text):
            print(f"[FILTER] Спам/низкое качество: {text[:50]}...")
            return False
        
        # Проверка релевантности к теме
        if not is_relevant_to_topic(text, topic):
            print(f"[FILTER] Не релевантно к '{topic}': {text[:50]}...")
            return False
        
        # Проверка индикаторов качества (лайки/ретвиты)
        if not has_quality_indicators(tweet):
            print(f"[FILTER] Низкая активность: {text[:50]}...")
            return False
        
        print(f"[VALID] Качественный твит: {text[:50]}...")
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка валидации твита: {e}")
        return False

# Старая функция для совместимости
def is_valid(tweet):
    text = getattr(tweet, "text", "").strip()
    return bool(text)

async def scrape_twitter():
    if Client is None:
        raise ImportError("twikit package is required for scrape_twitter")

    cfg = load_config()
    
    # Создаем клиент без прокси (на VPS прокси не нужен)
    timeout_val = 60
    client = Client(timeout=timeout_val)
    client.load_cookies(cfg["cookies_file"])
    
    print(f"[scraper] proxy set=False timeout={timeout_val}s")
    print(f"Куки загружены из файла: {cfg['cookies_file']}")
    print(f"Прокси отключен для VPS")
    print(f"[QUALITY] Включена валидация качества контента")

    entities = []
    total_processed = 0
    total_quality = 0
    
    for term in cfg["search_keywords"]:
        print(f"--- Поиск по ключевому слову: '{term}'")
        try:
            result = await client.search_tweet(term, "latest", cfg["tweets_per_keyword"])
        except twikit_errors.NotFound:
            print(f"WARNING: '{term}' вернул 404, пропускаем")
            continue
        except Exception as e:
            print(f"ERROR: при поиске '{term}': {type(e).__name__}: {str(e)}")
            print(f"TRACEBACK: {traceback.format_exc()}")
            continue

        tweets = getattr(result, "data", result)
        keyword_processed = 0
        keyword_quality = 0
        
        for tweet in tweets:
            total_processed += 1
            keyword_processed += 1
            
            # Используем новую качественную валидацию
            if not is_valid_quality_tweet(tweet, term):
                continue
                
            total_quality += 1
            keyword_quality += 1
            text = tweet.text
            
            # Конвертируем datetime в ISO формат
            try:
                if hasattr(tweet, 'created_at') and tweet.created_at:
                    from datetime import datetime as dt
                    # Парсим Twitter datetime формат в ISO
                    if isinstance(tweet.created_at, str):
                        # Twitter формат: "Sat Aug 23 16:16:30 +0000 2025"
                        parsed_dt = dt.strptime(tweet.created_at, "%a %b %d %H:%M:%S %z %Y")
                        iso_datetime = parsed_dt.isoformat()
                    else:
                        iso_datetime = tweet.created_at.isoformat() if hasattr(tweet.created_at, 'isoformat') else str(tweet.created_at)
                else:
                    from datetime import datetime as dt
                    iso_datetime = dt.utcnow().isoformat()
            except Exception as e:
                print(f"WARNING: Не удалось обработать datetime {tweet.created_at}: {e}")
                from datetime import datetime as dt
                iso_datetime = dt.utcnow().isoformat()

            # Создаём JSON объект для контента (как ожидает HuggingFace uploader)
            content_json = {
                "text": text,
                "tweet_hashtags": [],  # Можно извлекать из текста при необходимости
                "username": "",  # Будет кодироваться позже
                "url": "",  # URL из твита если есть
                "timestamp": iso_datetime,  # Дополнительная метка времени
                "user_id": "",
                "user_display_name": "",
                "user_verified": False,
                "tweet_id": str(tweet.id),
                "is_reply": False,
                "is_quote": False,
                "conversation_id": "",
                "in_reply_to_user_id": "",
                "media": []
            }
            
            entities.append({
                "uri": f"https://twitter.com/i/web/status/{tweet.id}",
                "datetime": iso_datetime,
                "source": "X",
                "label": {"name": term},
                "content": json.dumps(content_json, ensure_ascii=False),
                "content_size_bytes": len(json.dumps(content_json, ensure_ascii=False).encode("utf-8"))
            })

        print(f"[QUALITY] '{term}': {keyword_quality}/{keyword_processed} качественных твитов")
        
        # троттлинг
        await asyncio.sleep(20)

    print(f"[QUALITY] Общая статистика: {total_quality}/{total_processed} качественных твитов ({total_quality/total_processed*100:.1f}%)")

    # дедупликация по uri
    seen = set()
    unique = []
    for e in entities:
        if e["uri"] in seen:
            continue
        seen.add(e["uri"])
        unique.append(e)
    print(f"После дедупликации: {len(unique)} твитов")

    os.makedirs("normalized", exist_ok=True)
    out_file = f"normalized/twitter_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.jsonl"
    with open(out_file, "w", encoding="utf-8") as f:
        for e in unique:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    print(f"Сохранено: {out_file}")

    return unique

if __name__ == "__main__":
    asyncio.run(scrape_twitter())
