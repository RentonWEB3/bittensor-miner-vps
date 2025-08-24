#!/usr/bin/env python3.11
"""
Надежный оптимизатор тем для майнера
Использует Dynamic Desirability + статичные темы без дашборда
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

class ReliableTopicOptimizer:
    def __init__(self):
        # Правильный URL для Dynamic Desirability
        self.gravity_api_url = "https://gravity.api.macrocosmos.ai/api/v1/desirable"
        
        # Статичные темы по категориям (проверенные и работающие)
        self.static_topics = {
            "reddit": {
                "crypto_ai": ["r/bitcoin", "r/ethereum", "r/artificial", "r/machinelearning", "r/cryptocurrency"],
                "tech": ["r/technology", "r/programming", "r/software", "r/hardware", "r/gaming"],
                "finance": ["r/investing", "r/stocks", "r/wallstreetbets", "r/cryptocurrency", "r/trading"],
                "news": ["r/news", "r/politics", "r/worldnews", "r/science", "r/technology"],
                "entertainment": ["r/movies", "r/music", "r/gaming", "r/sports", "r/entertainment"],
                "tesla_ev": ["r/teslamotors", "r/electricvehicles", "r/teslamodel3", "r/teslamodely", "r/teslainvestorsclub"],
                "renewable": ["r/solar", "r/renewableenergy", "r/climatechange", "r/sustainability", "r/greenenergy"]
            },
            "twitter": {
                "crypto_ai": ["bitcoin", "ethereum", "ai", "artificialintelligence", "machinelearning", "crypto", "blockchain"],
                "tech": ["technology", "programming", "software", "hardware", "gaming", "esports"],
                "finance": ["investing", "stocks", "finance", "trading", "wallstreetbets", "cryptocurrency"],
                "news": ["news", "politics", "worldnews", "technology", "science"],
                "tesla_ev": ["tesla", "electricvehicles", "teslamodel3", "teslamodely", "ev"],
                "renewable": ["solar", "renewableenergy", "climatechange", "sustainability", "greenenergy"]
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
                            topics = data[:10]  # Берем топ-10
                        elif isinstance(data, dict):
                            if 'topics' in data:
                                topics = data['topics'][:10]
                            elif 'labels' in data:
                                topics = data['labels'][:10]
                            elif 'desirable' in data:
                                topics = data['desirable'][:10]
                            else:
                                # Если структура неизвестна, берем ключи
                                topics = list(data.keys())[:10]
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
        return ["tesla", "ai", "crypto", "bitcoin", "technology", "electricvehicles", "solar", "renewableenergy"]

    def get_static_topics(self, platform: str, max_per_category: int = 2) -> List[str]:
        """Получает статичные темы по платформе"""
        logger.info(f"📂 Выбираем статичные темы для {platform}...")
        
        topics = []
        platform_topics = self.static_topics.get(platform, {})
        
        for category, category_topics in platform_topics.items():
            # Берем по 2 темы из каждой категории
            selected = category_topics[:max_per_category]
            topics.extend(selected)
            logger.info(f"  {category}: {selected}")
        
        return topics[:10]  # Ограничиваем общим количеством

    def combine_topics(self, desirability_topics: List[str], 
                      static_reddit: List[str], 
                      static_twitter: List[str]) -> Tuple[List[str], List[str]]:
        """Комбинируем темы из разных источников"""
        logger.info("🔄 Комбинируем темы...")
        
        # Финальные списки
        final_reddit = []
        final_twitter = []
        
        # Добавляем Dynamic Desirability (50%)
        for topic in desirability_topics:
            # Для Reddit добавляем r/ префикс если его нет
            if not topic.startswith('r/') and not topic.startswith('#'):
                reddit_topic = f"r/{topic}"
            else:
                reddit_topic = topic
                
            if reddit_topic not in final_reddit and len(final_reddit) < 10:
                final_reddit.append(reddit_topic)
                
            if topic not in final_twitter and len(final_twitter) < 10:
                final_twitter.append(topic)
        
        # Добавляем статичные темы (50%)
        for topic in static_reddit:
            if topic not in final_reddit and len(final_reddit) < 10:
                final_reddit.append(topic)
                
        for topic in static_twitter:
            if topic not in final_twitter and len(final_twitter) < 10:
                final_twitter.append(topic)
        
        # Убираем дубликаты
        final_reddit = list(dict.fromkeys(final_reddit))
        final_twitter = list(dict.fromkeys(final_twitter))
        
        logger.info(f"🎯 Финальные Reddit темы: {final_reddit}")
        logger.info(f"🎯 Финальные Twitter темы: {final_twitter}")
        
        return final_reddit[:10], final_twitter[:10]

    def create_optimized_config(self, reddit_topics: List[str], twitter_topics: List[str]) -> Dict:
        """Создает оптимизированную конфигурацию"""
        logger.info("⚙️ Создаем оптимизированную конфигурацию...")
        
        config = {
            "scraper_configs": [
                {
                    "scraper_id": "X.microworlds",
                    "cadence_seconds": 300,  # 5 минут
                    "labels_to_scrape": [
                        {
                            "label_choices": twitter_topics,
                            "max_age_hint_minutes": 1440,  # 24 часа
                            "max_data_entities": 10
                        }
                    ],
                    "config": {
                        "cookies_path": "twitter_cookies.json"
                    }
                },
                {
                    "scraper_id": "Reddit.custom",
                    "cadence_seconds": 900,  # 15 минут
                    "labels_to_scrape": [
                        {
                            "label_choices": reddit_topics,
                            "max_age_hint_minutes": 1440,  # 24 часа
                            "max_data_entities": 200
                        }
                    ],
                    "config": {
                        "subreddit": "all",
                        "limit_per_label": 100
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
        logger.info("🚀 Начинаем надежную оптимизацию тем...")
        
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
            logger.info("🎉 Оптимизация завершена успешно!")
            logger.info(f"📋 Reddit темы: {final_reddit}")
            logger.info(f"📋 Twitter темы: {final_twitter}")
            return True
        else:
            logger.error("❌ Ошибка при обновлении конфигурации")
            return False

def main():
    """Основная функция"""
    optimizer = ReliableTopicOptimizer()
    success = optimizer.optimize_topics()
    
    if success:
        print("\n🎯 Рекомендации:")
        print("1. Перезапустите майнер с новой конфигурацией")
        print("2. Мониторьте метрики в течение 2-4 часов")
        print("3. Запускайте оптимизацию каждые 6-12 часов")
        print("4. Анализируйте логи для корректировки тем")
        print("5. Используйте только проверенные темы без дашборда")
    else:
        print("\n⚠️ Оптимизация не завершена. Проверьте логи.")

if __name__ == "__main__":
    main()
