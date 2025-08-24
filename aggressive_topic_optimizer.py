#!/usr/bin/env python3.11
"""
Агрессивный оптимизатор тем для майнера
Больше тем, больше данных, более частый скрапинг
"""

import json
import requests
import logging
from typing import List, Dict, Tuple
from pathlib import Path
import time
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AggressiveTopicOptimizer:
    def __init__(self):
        # Правильный URL для Dynamic Desirability
        self.gravity_api_url = "https://gravity.api.macrocosmos.ai/api/v1/desirable"
        
        # Расширенные статичные темы (больше покрытие)
        self.static_topics = {
            "reddit": {
                "crypto_ai": ["r/bitcoin", "r/ethereum", "r/artificial", "r/machinelearning", "r/cryptocurrency", "r/blockchain", "r/defi", "r/nft"],
                "tech": ["r/technology", "r/programming", "r/software", "r/hardware", "r/gaming", "r/esports", "r/cybersecurity", "r/linux"],
                "finance": ["r/investing", "r/stocks", "r/wallstreetbets", "r/cryptocurrency", "r/trading", "r/personalfinance", "r/economics", "r/financialindependence"],
                "news": ["r/news", "r/politics", "r/worldnews", "r/science", "r/technology", "r/environment", "r/space", "r/medicine"],
                "entertainment": ["r/movies", "r/music", "r/gaming", "r/sports", "r/entertainment", "r/television", "r/books", "r/art"],
                "tesla_ev": ["r/teslamotors", "r/electricvehicles", "r/teslamodel3", "r/teslamodely", "r/teslainvestorsclub", "r/teslamodelx", "r/teslamodels", "r/cybertruck"],
                "renewable": ["r/solar", "r/renewableenergy", "r/climatechange", "r/sustainability", "r/greenenergy", "r/windenergy", "r/energy", "r/environment"],
                "lifestyle": ["r/fitness", "r/health", "r/food", "r/travel", "r/lifestyle", "r/cooking", "r/outdoors", "r/wellness"],
                "business": ["r/entrepreneur", "r/business", "r/startups", "r/marketing", "r/sales", "r/consulting", "r/freelance", "r/smallbusiness"]
            },
            "twitter": {
                "crypto_ai": ["bitcoin", "ethereum", "ai", "artificialintelligence", "machinelearning", "crypto", "blockchain", "defi", "nft", "web3"],
                "tech": ["technology", "programming", "software", "hardware", "gaming", "esports", "cybersecurity", "linux", "opensource", "cloud"],
                "finance": ["investing", "stocks", "finance", "trading", "wallstreetbets", "cryptocurrency", "personalfinance", "economics", "fintech", "wealth"],
                "news": ["news", "politics", "worldnews", "technology", "science", "environment", "space", "medicine", "health", "climate"],
                "tesla_ev": ["tesla", "electricvehicles", "teslamodel3", "teslamodely", "ev", "teslamodelx", "teslamodels", "cybertruck", "elonmusk", "spacex"],
                "renewable": ["solar", "renewableenergy", "climatechange", "sustainability", "greenenergy", "windenergy", "energy", "environment", "cleanenergy", "carbon"],
                "business": ["entrepreneur", "business", "startups", "marketing", "sales", "consulting", "freelance", "smallbusiness", "leadership", "innovation"]
            }
        }

    def fetch_dynamic_desirability(self) -> List[str]:
        """Получаем Dynamic Desirability темы с правильным API"""
        logger.info("⭐ Получаем Dynamic Desirability...")
        
        try:
            # Пробуем разные варианты API
            api_variants = [
                "https://gravity.api.macrocosmos.ai/api/v1/desirable",
                "https://gravity.api.macrocosmos.ai/api/desirable",
                "https://gravity.api.macrocosmos.ai/desirable",
                "https://api.gravity.macrocosmos.ai/v1/desirable"
            ]
            
            for api_url in api_variants:
                try:
                    logger.info(f"Пробуем API: {api_url}")
                    response = requests.get(api_url, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        logger.info(f"✅ Успешно получены данные с {api_url}")
                        
                        # Обрабатываем разные форматы ответа
                        if isinstance(data, list):
                            topics = data[:15]  # Берем больше тем
                        elif isinstance(data, dict):
                            if 'topics' in data:
                                topics = data['topics'][:15]
                            elif 'labels' in data:
                                topics = data['labels'][:15]
                            elif 'desirable' in data:
                                topics = data['desirable'][:15]
                            else:
                                topics = list(data.keys())[:15]
                        else:
                            topics = []
                        
                        if topics:
                            logger.info(f"📊 Получено {len(topics)} тем: {topics}")
                            return topics
                            
                except Exception as e:
                    logger.warning(f"Не удалось получить данные с {api_url}: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Ошибка при получении Dynamic Desirability: {e}")
        
        # Fallback темы если API недоступен
        logger.info("🔄 Используем fallback темы")
        return ["tesla", "ai", "crypto", "bitcoin", "technology", "electricvehicles", "solar", "renewableenergy", "ethereum", "machinelearning", "blockchain", "climatechange", "sustainability", "investing", "news"]

    def get_static_topics(self, platform: str, max_per_category: int = 3) -> List[str]:
        """Получает статичные темы по платформе (больше тем)"""
        logger.info(f"📂 Выбираем статичные темы для {platform}...")
        
        topics = []
        platform_topics = self.static_topics.get(platform, {})
        
        for category, category_topics in platform_topics.items():
            # Берем по 3 темы из каждой категории
            selected = category_topics[:max_per_category]
            topics.extend(selected)
            logger.info(f"  {category}: {selected}")
        
        return topics[:20]  # Увеличиваем лимит до 20

    def combine_topics(self, desirability_topics: List[str], 
                      static_reddit: List[str], 
                      static_twitter: List[str]) -> Tuple[List[str], List[str]]:
        """Комбинируем темы из разных источников"""
        logger.info("🔄 Комбинируем темы...")
        
        # Финальные списки
        final_reddit = []
        final_twitter = []
        
        # Добавляем Dynamic Desirability (60% - приоритет)
        for topic in desirability_topics:
            # Для Reddit добавляем r/ префикс если его нет
            if not topic.startswith('r/') and not topic.startswith('#'):
                reddit_topic = f"r/{topic}"
            else:
                reddit_topic = topic
                
            if reddit_topic not in final_reddit and len(final_reddit) < 25:
                final_reddit.append(reddit_topic)
                
            if topic not in final_twitter and len(final_twitter) < 25:
                final_twitter.append(topic)
        
        # Добавляем статичные темы (40%)
        for topic in static_reddit:
            if topic not in final_reddit and len(final_reddit) < 25:
                final_reddit.append(topic)
                
        for topic in static_twitter:
            if topic not in final_twitter and len(final_twitter) < 25:
                final_twitter.append(topic)
        
        # Убираем дубликаты
        final_reddit = list(dict.fromkeys(final_reddit))
        final_twitter = list(dict.fromkeys(final_twitter))
        
        logger.info(f"🎯 Финальные Reddit темы: {final_reddit}")
        logger.info(f"🎯 Финальные Twitter темы: {final_twitter}")
        
        return final_reddit[:25], final_twitter[:25]

    def create_optimized_config(self, reddit_topics: List[str], twitter_topics: List[str]) -> Dict:
        """Создает агрессивную конфигурацию"""
        logger.info("⚙️ Создаем агрессивную конфигурацию...")
        
        config = {
            "scraper_configs": [
                {
                    "scraper_id": "X.microworlds",
                    "cadence_seconds": 180,  # 3 минуты (быстрее)
                    "labels_to_scrape": [
                        {
                            "label_choices": twitter_topics,
                            "max_age_hint_minutes": 1440,  # 24 часа
                            "max_data_entities": 25  # Больше данных
                        }
                    ],
                    "config": {
                        "cookies_path": "twitter_cookies.json"
                    }
                },
                {
                    "scraper_id": "Reddit.custom",
                    "cadence_seconds": 600,  # 10 минут (быстрее)
                    "labels_to_scrape": [
                        {
                            "label_choices": reddit_topics,
                            "max_age_hint_minutes": 1440,  # 24 часа
                            "max_data_entities": 1000  # Максимально больше данных
                        }
                    ],
                    "config": {
                        "subreddit": "all",
                        "limit_per_label": 1000  # Максимально больше постов на тему
                    }
                }
            ]
        }
        
        return config

    def backup_current_config(self) -> bool:
        """Создает резервную копию текущей конфигурации"""
        try:
            if Path("scraping_config_gravity.json").exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"scraping_config_backup_{timestamp}.json"
                import shutil
                shutil.copy("scraping_config_gravity.json", backup_name)
                logger.info(f"✅ Резервная копия создана: {backup_name}")
                return True
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии: {e}")
        return False

    def update_config(self, config: Dict) -> bool:
        """Обновляет конфигурацию"""
        try:
            # Сохраняем оптимизированную конфигурацию
            with open("scraping_config_optimized.json", "w") as f:
                json.dump(config, f, indent=2)
            
            # Копируем в основную конфигурацию
            import shutil
            shutil.copy("scraping_config_optimized.json", "scraping_config_gravity.json")
            
            logger.info("✅ Конфигурация обновлена: scraping_config_gravity.json")
            return True
        except Exception as e:
            logger.error(f"Ошибка обновления конфигурации: {e}")
            return False

    def optimize_topics(self) -> bool:
        """Основная функция оптимизации"""
        logger.info("🚀 Начинаем агрессивную оптимизацию тем...")
        
        # Получаем данные из всех источников
        desirability_topics = self.fetch_dynamic_desirability()
        static_reddit = self.get_static_topics("reddit")
        static_twitter = self.get_static_topics("twitter")
        
        # Комбинируем темы
        final_reddit, final_twitter = self.combine_topics(
            desirability_topics, static_reddit, static_twitter
        )
        
        # Создаем конфигурацию
        config = self.create_optimized_config(final_reddit, final_twitter)
        
        # Создаем резервную копию
        self.backup_current_config()
        
        # Обновляем конфигурацию
        if self.update_config(config):
            logger.info("🎉 Агрессивная оптимизация завершена успешно!")
            logger.info(f"📋 Reddit темы: {len(final_reddit)} тем")
            logger.info(f"📋 Twitter темы: {len(final_twitter)} тем")
            logger.info(f"⚡ Cadence: Twitter 3мин, Reddit 10мин")
            logger.info(f"📊 Лимиты: Twitter 25, Reddit 1000 (МАКСИМАЛЬНО!)")
            return True
        else:
            logger.error("❌ Ошибка при обновлении конфигурации")
            return False

def main():
    """Основная функция"""
    optimizer = AggressiveTopicOptimizer()
    success = optimizer.optimize_topics()
    
    if success:
        print("\n🎯 Рекомендации:")
        print("1. Перезапустите майнер с новой конфигурацией")
        print("2. Мониторьте метрики в течение 2-4 часов")
        print("3. Запускайте оптимизацию каждые 6-12 часов")
        print("4. Анализируйте логи для корректировки тем")
        print("5. Используйте только проверенные темы без дашборда")
        print("6. Агрессивный режим: больше тем, больше данных, быстрее скрапинг")
    else:
        print("\n⚠️ Оптимизация не завершена. Проверьте логи.")

if __name__ == "__main__":
    main()
