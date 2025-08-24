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

def extract_hashtags(text: str) -> list:
    """Извлекает хэштеги из текста твита"""
    hashtags = re.findall(r'#(\w+)', text)
    return [f"#{tag}" for tag in hashtags]

def extract_urls(text: str) -> list:
    """Извлекает URL из текста твита"""
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)
    return urls

def is_english_basic(text: str) -> bool:
    """Базовая проверка английского языка (менее строгая)"""
    if not text.strip():
        return False
    
    # Подсчет английских символов
    english_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
    total_chars = sum(1 for c in text if c.isalpha())
    
    if total_chars == 0:
        return True  # Если нет букв, считаем валидным (числа, символы)
    
    # Снижен порог до 60% для менее строгой фильтрации
    return (english_chars / total_chars) >= 0.6

def is_basic_spam(text: str) -> bool:
    """Базовая анти-спам проверка (только критичные случаи)"""
    text = text.strip()
    
    # Только критичные фильтры:
    # 1. Слишком короткий (меньше 10 символов)
    if len(text) < 10:
        return True
    
    # 2. Повторяющиеся символы (явный спам)
    if re.search(r'(.)\1{10,}', text):  # 10+ одинаковых символов подряд
        return True
    
    # 3. Слишком много одинаковых хэштегов
    hashtag_count = len(re.findall(r'#\w+', text))
    if hashtag_count > 10:  # Увеличен лимит
        return True
    
    return False

def is_relevant_basic(text: str, topic: str) -> bool:
    """Базовая проверка релевантности (менее строгая)"""
    text_lower = text.lower()
    topic_lower = topic.lower()
    
    # Прямое упоминание темы
    if topic_lower in text_lower:
        return True
    
    # Расширенные синонимы
    topic_synonyms = {
        'ev': ['electric', 'vehicle', 'car', 'tesla', 'battery', 'charging', 'bev', 'auto', 'motor'],
        'tesla': ['model', 'cybertruck', 'elon', 'musk', 'supercharger', 'autopilot'],
        'greenenergy': ['solar', 'wind', 'renewable', 'clean', 'sustainable', 'energy', 'power'],
        'electricvehicles': ['electric', 'vehicle', 'car', 'auto', 'ev', 'battery', 'charging'],
        'sustainability': ['renewable', 'green', 'eco', 'climate', 'carbon', 'environment'],
        'renewableenergy': ['solar', 'wind', 'hydro', 'renewable', 'clean', 'energy'],
        'climatechange': ['climate', 'warming', 'carbon', 'emission', 'greenhouse', 'environment'],
        'battery': ['lithium', 'charging', 'energy', 'storage', 'battery', 'power'],
        'charging': ['charge', 'station', 'fast', 'supercharger', 'plug', 'electric']
    }
    
    # Если есть синонимы для темы
    synonyms = topic_synonyms.get(topic_lower, [])
    for synonym in synonyms:
        if synonym in text_lower:
            return True
    
    # Если синонимов нет, считаем релевантным (не отбрасываем)
    return len(synonyms) == 0

def is_valid_quality_tweet(tweet, topic: str) -> bool:
    """Упрощенная валидация качества твита"""
    try:
        text = getattr(tweet, "text", "").strip()
        
        # Базовая проверка - есть ли текст
        if not text:
            print(f"[FILTER] Пустой текст")
            return False
        
        # Только критичные фильтры:
        
        # 1. Базовая проверка языка (менее строгая)
        if not is_english_basic(text):
            print(f"[FILTER] Не английский: {text[:50]}...")
            return False
        
        # 2. Только критичный спам
        if is_basic_spam(text):
            print(f"[FILTER] Критичный спам: {text[:50]}...")
            return False
        
        # 3. Базовая релевантность (менее строгая)
        if not is_relevant_basic(text, topic):
            print(f"[FILTER] Не релевантно к '{topic}': {text[:50]}...")
            return False
        
        # НЕ проверяем лайки/ретвиты - пусть валидатор решает
        
        print(f"[VALID] Принят: {text[:50]}...")
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка валидации: {e}")
        return True  # При ошибке пропускаем (не отбрасываем)

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
    print(f"[QUALITY] Базовая валидация качества (менее строгая)")

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
            
            # Используем упрощенную валидацию
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

            # Извлекаем хэштеги и URL из твита
            tweet_hashtags = extract_hashtags(text)
            tweet_urls = extract_urls(text)
            tweet_url = tweet_urls[0] if tweet_urls else f"https://twitter.com/i/web/status/{tweet.id}"
            
            # Получаем username
            username = getattr(tweet, 'username', '') or getattr(tweet.user, 'username', '') if hasattr(tweet, 'user') else ''

            # Создаём JSON объект для контента с ЗАПОЛНЕННЫМИ ОБЯЗАТЕЛЬНЫМИ ПОЛЯМИ
            content_json = {
                "text": text,
                "tweet_hashtags": tweet_hashtags,  # ОБЯЗАТЕЛЬНО: реальные хэштеги
                "username": username,              # ОБЯЗАТЕЛЬНО: реальный username 
                "url": tweet_url,                  # ОБЯЗАТЕЛЬНО: реальный URL
                "timestamp": iso_datetime,
                "user_id": getattr(tweet, 'user_id', '') or str(getattr(tweet, 'id', '')),
                "user_display_name": getattr(tweet, 'user_display_name', '') or getattr(tweet.user, 'name', '') if hasattr(tweet, 'user') else '',
                "user_verified": getattr(tweet, 'user_verified', False),
                "tweet_id": str(tweet.id),
                "is_reply": getattr(tweet, 'is_reply', False),
                "is_quote": getattr(tweet, 'is_quote', False),
                "conversation_id": getattr(tweet, 'conversation_id', ''),
                "in_reply_to_user_id": getattr(tweet, 'in_reply_to_user_id', ''),
                "media": getattr(tweet, 'media', []) or []
            }
            
            entities.append({
                "uri": tweet_url,
                "datetime": iso_datetime,
                "source": "X",
                "label": {"name": term},
                "content": json.dumps(content_json, ensure_ascii=False),
                "content_size_bytes": len(json.dumps(content_json, ensure_ascii=False).encode("utf-8"))
            })

        print(f"[QUALITY] '{term}': {keyword_quality}/{keyword_processed} принятых твитов")
        
        # троттлинг
        await asyncio.sleep(20)

    print(f"[QUALITY] Общая статистика: {total_quality}/{total_processed} принятых твитов ({total_quality/total_processed*100:.1f}%)")

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
