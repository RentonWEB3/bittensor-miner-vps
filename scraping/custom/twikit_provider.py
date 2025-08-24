import json
import asyncio
from scraping.scraper import Scraper, ValidationResult, HFValidationResult
from common.data import DataEntity, DataLabel, DataSource
import twikit_scraper  # ваш модуль
from datetime import datetime

class TwikitProvider(Scraper):
    def __init__(self, config=None, session=None):
        self.session = session
        scraper_key = "X.apidojo"   # теперь используем X.apidojo

        # Если передали CoordinatorConfig (есть поле scraper_configs)
        if hasattr(config, "scraper_configs"):
            scraper_cfg = config.scraper_configs.get(scraper_key)
        else:
            scraper_cfg = config  # возможно уже ScraperConfig

        if scraper_cfg is None:
            print("WARN: scraper_cfg for X.apidojo not found")
            self.search_keywords = []
            self.tweets_per_keyword = 100
            self.cookies_file = "twitter_cookies.json"
        else:
            labels_cfg = getattr(scraper_cfg, "labels_to_scrape", [])
            if labels_cfg:
                first = labels_cfg[0]
                self.search_keywords = [lbl.value for lbl in getattr(first, "label_choices", [])]
                self.tweets_per_keyword = getattr(first, "max_data_entities", 100)
            else:
                self.search_keywords = []
                self.tweets_per_keyword = 100
            self.cookies_file = "twitter_cookies.json"

        print("DEBUG Twikit search_keywords:", self.search_keywords, "tweets_per_keyword:", self.tweets_per_keyword, "cookies_file:", self.cookies_file)

    def _write_temp_config(self):
        # Записываем файл config.json для twikit_scraper
        cfg = {
            "cookies_file": self.cookies_file,
            "search_keywords": self.search_keywords,
            "tweets_per_keyword": self.tweets_per_keyword
        }
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False)

    async def scrape(self, scrape_config=None):
        """Scrapes twitter using the ``twikit`` helper module."""
        import bittensor as bt
        
        try:
            bt.logging.debug("DEBUG: Starting TwikitProvider scrape")
            
            # Получаем ключевые слова из scrape_config
            if scrape_config and hasattr(scrape_config, 'labels'):
                search_keywords = [label.value for label in scrape_config.labels]
                entity_limit = getattr(scrape_config, 'entity_limit', 100)
                print(f"DEBUG: Using keywords from scrape_config: {search_keywords}, limit: {entity_limit}")
            else:
                search_keywords = self.search_keywords
                entity_limit = self.tweets_per_keyword
                print(f"DEBUG: Using default keywords: {search_keywords}, limit: {entity_limit}")
            
            # Обновляем конфигурацию
            self.search_keywords = search_keywords
            self.tweets_per_keyword = entity_limit
            
            # Подготовим config.json
            self._write_temp_config()

            # Запустим асинхронную функцию twikit_scraper.scrape_twitter()
            items = await twikit_scraper.scrape_twitter()
            entities = []
            for i in items:
                raw_dt = i["datetime"]
                try:
                    # Поддерживаем как старый, так и новый ISO формат
                    if "T" in raw_dt and ("+" in raw_dt or "Z" in raw_dt):
                        # ISO формат: "2025-08-23T16:16:30+00:00"
                        from datetime import datetime as dt
                        dt_obj = dt.fromisoformat(raw_dt.replace("Z", "+00:00"))
                    else:
                        # Старый формат: "Sat Aug 23 16:16:30 +0000 2025"
                        dt_obj = datetime.strptime(raw_dt, "%a %b %d %H:%M:%S %z %Y")
                except Exception as e:
                    print(f"DEBUG cannot parse datetime: {raw_dt}, error: {e}")
                    # Попробуем текущее время как fallback
                    from datetime import datetime as dt
                    dt_obj = dt.utcnow().replace(tzinfo=dt.timezone.utc)
                    print(f"DEBUG using current time as fallback: {dt_obj}")

                # Создаём JSON объект для контента (как ожидает HuggingFace uploader)
                content_json = {
                    "text": i["content"],
                    "tweet_hashtags": [],  # Можно извлекать из текста при необходимости
                    "username": "",  # Будет кодироваться позже
                    "url": "",  # URL из твита если есть
                    "timestamp": dt_obj.isoformat(),  # Дополнительная метка времени
                    "user_id": "",
                    "user_display_name": "",
                    "user_verified": False,
                    "tweet_id": i["uri"].split("/")[-1] if "/" in i["uri"] else "",
                    "is_reply": False,
                    "is_quote": False,
                    "conversation_id": "",
                    "in_reply_to_user_id": "",
                    "media": []
                }
                content_bytes = json.dumps(content_json, ensure_ascii=False).encode("utf-8")
                # Создаем правильную структуру для HF-валидации
                entities.append(
                    DataEntity(
                        uri=i["uri"],
                        datetime=dt_obj,
                        source=DataSource.X,
                        label=DataLabel(value=i["label"]),  # Уже правильный формат
                        content=i["content"].encode("utf-8"),  # Сырой текст
                        content_size_bytes=i["content_size_bytes"],
                    )
                )
            return entities
        
        except RecursionError as e:
            bt.logging.error(f"RecursionError in TwikitProvider: {e}")
            return []
        except Exception as e:
            bt.logging.error(f"Error in TwikitProvider: {type(e).__name__}: {e}")
            return []

    async def validate(self, entities):
        """Perform a very basic validation of scraped entities."""

        if not entities:
            return []

        results = []
        for entity in entities:
            is_valid = bool(getattr(entity, "content", "").strip())
            results.append(
                ValidationResult(
                    is_valid=is_valid,
                    content_size_bytes_validated=len(entity.content.encode("utf-8")) if entity.content else 0,
                    reason="" if is_valid else "Empty content",
                )
            )

        return results

    async def validate_hf(self, entities) -> HFValidationResult:
        """Validate HF dataset entries.

        This basic implementation simply marks all provided entities as valid
        without performing any external checks. It returns an
        ``HFValidationResult`` mirroring the structure used by other scrapers so
        that the class satisfies :class:`Scraper`'s abstract interface.

        Args:
            entities: An iterable of HF dataset rows represented as dictionaries.

        Returns:
            HFValidationResult indicating success for all rows.
        """

        if not entities:
            return HFValidationResult(
                is_valid=True,
                validation_percentage=100.0,
                reason="No entities to validate",
            )

        results = [
            ValidationResult(
                is_valid=True,
                content_size_bytes_validated=0,
                reason="",
            )
            for _ in entities
        ]

        valid_count = len([r for r in results if r.is_valid])
        validation_percentage = (valid_count / len(results)) * 100

        return HFValidationResult(
            is_valid=True,
            validation_percentage=validation_percentage,
            reason=f"Validation Percentage = {validation_percentage}",
        )