import os
import json
import asyncio
import traceback
from datetime import datetime
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

def is_valid(tweet):
    text = getattr(tweet, "text", "").strip()
    return bool(text)

async def scrape_twitter():
    if Client is None:
        raise ImportError("twikit package is required for scrape_twitter")

    cfg = load_config()
    
        # Настройка прокси по примеру рабочего проекта
    proxy_url = "http://RX4TVSAM:XDGZS8Y8@104.234.127.240:48028"
    timeout_val = 60

    # Создаем клиент с прокси (как в рабочем проекте)
    client = Client(proxy=proxy_url, timeout=timeout_val)
    client.load_cookies(cfg["cookies_file"])
    
    print(f"[scraper] proxy set={bool(proxy_url)} timeout={timeout_val}s")
    
    print(f"Куки загружены из файла: {cfg['cookies_file']}")
    print(f"Прокси настроен: {proxy_url}")

    entities = []
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
        for tweet in tweets:
            if not is_valid(tweet):
                continue
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

        # троттлинг
        await asyncio.sleep(20)

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
