#!/usr/bin/env python3.11
"""
Продвинутый оптимизатор тем для майнера
Анализирует дашборд, Dynamic Desirability и создает оптимальную конфигурацию
"""

import json
import requests
import pandas as pd
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

class AdvancedTopicOptimizer:
    def __init__(self):
        self.dashboard_url = "https://sn13-dashboard.api.macrocosmos.ai"
        self.gravity_api_url = "https://gravity.api.macrocosmos.ai/api/v1/desirable"
        self.csv_file = "2025-08-24T13-15_export.csv"
        
        # Категории тем для лучшего покрытия
        self.topic_categories = {
            "crypto_ai": ["bitcoin", "ethereum", "ai", "artificialintelligence", "machinelearning", "crypto", "blockchain"],
            "tech": ["technology", "programming", "software", "hardware", "gaming", "esports"],
            "finance": ["investing", "stocks", "finance", "trading", "wallstreetbets", "cryptocurrency"],
            "news": ["news", "politics", "worldnews", "technology", "science"],
            "entertainment": ["movies", "music", "gaming", "sports", "entertainment"],
            "lifestyle": ["fitness", "health", "food", "travel", "lifestyle"]
        }
        
        # Темы с высоким ростом (из CSV)
        self.high_growth_reddit = [
            "r/askreddit", "r/amioverreacting", "r/aitah", "r/nostupidquestions", 
            "r/politics", "r/teenagers", "r/wallstreetbets", "r/relationship_advice",
            "r/teenagersbutbetter", "r/market76", "r/helldivers", "r/genshin_impact_leaks",
            "r/growagarden", "r/productivitycafe", "r/nightreign", "r/originalcharacter"
        ]
        
        self.high_growth_twitter = [
            "tesla", "electricvehicles", "solar", "technology", "ai", "crypto",
            "bitcoin", "ethereum", "artificialintelligence", "machinelearning"
        ]

    def fetch_dashboard_data(self) -> pd.DataFrame:
        """Получаем данные с дашборда"""
        logger.info("📊 Получаем данные с дашборда...")
        
        try:
            # Пробуем получить данные через API
            response = requests.get(f"{self.dashboard_url}/api/top-labels", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return pd.DataFrame(data)
        except Exception as e:
            logger.warning(f"Не удалось получить данные через API: {e}")
        
        # Если API не работает, используем CSV файл
        try:
            if Path(self.csv_file).exists():
                df = pd.read_csv(self.csv_file)
                logger.info(f"✅ Загружено {len(df)} записей из CSV")
                return df
            else:
                logger.warning(f"CSV файл {self.csv_file} не найден")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Ошибка чтения CSV: {e}")
            return pd.DataFrame()

    def fetch_dynamic_desirability(self) -> List[str]:
        """Получаем Dynamic Desirability темы"""
        logger.info("⭐ Получаем Dynamic Desirability...")
        
        try:
            response = requests.get(self.gravity_api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    return data[:10]  # Берем топ-10
                elif isinstance(data, dict) and 'topics' in data:
                    return data['topics'][:10]
        except Exception as e:
            logger.warning(f"Не удалось получить Dynamic Desirability: {e}")
        
        # Fallback темы
        return ["tesla", "ai", "crypto", "bitcoin", "technology"]

    def analyze_dashboard_data(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """Анализируем данные дашборда и выбираем лучшие темы"""
        logger.info("🔍 Анализируем данные дашборда...")
        
        if df.empty:
            logger.warning("Нет данных для анализа")
            return self.high_growth_reddit[:5], self.high_growth_twitter[:5]
        
        # Фильтруем по источнику
        reddit_data = df[df['source'] == 'reddit'].copy()
        twitter_data = df[df['source'] == 'x'].copy()
        
        # Сортируем по объему данных
        reddit_top = reddit_data.nlargest(10, 'size collected')
        twitter_top = twitter_data.nlargest(10, 'size collected')
        
        # Извлекаем темы
        reddit_topics = []
        for _, row in reddit_top.iterrows():
            label = row['label']
            if pd.notna(label) and label != 'NULL':
                # Убираем r/ префикс для анализа
                clean_label = label.replace('r/', '') if label.startswith('r/') else label
                reddit_topics.append(clean_label)
        
        twitter_topics = []
        for _, row in twitter_top.iterrows():
            label = row['label']
            if pd.notna(label) and label != 'NULL':
                # Убираем # префикс для анализа
                clean_label = label.replace('#', '') if label.startswith('#') else label
                twitter_topics.append(clean_label)
        
        logger.info(f"📊 Найдено {len(reddit_topics)} топ Reddit тем")
        logger.info(f"📊 Найдено {len(twitter_topics)} топ Twitter тем")
        
        return reddit_topics[:5], twitter_topics[:5]

    def get_category_topics(self) -> Tuple[List[str], List[str]]:
        """Получаем темы по категориям"""
        logger.info("📂 Выбираем темы по категориям...")
        
        # Выбираем по одной теме из каждой категории
        reddit_categories = []
        twitter_categories = []
        
        for category, topics in self.topic_categories.items():
            if topics:
                # Для Reddit добавляем r/ префикс
                reddit_topic = f"r/{topics[0]}" if topics[0] not in ['ai', 'crypto'] else topics[0]
                reddit_categories.append(reddit_topic)
                
                # Для Twitter используем без префикса
                twitter_categories.append(topics[0])
        
        return reddit_categories[:5], twitter_categories[:5]

    def combine_topics(self, dashboard_reddit: List[str], dashboard_twitter: List[str], 
                      desirability: List[str], category_reddit: List[str], 
                      category_twitter: List[str]) -> Tuple[List[str], List[str]]:
        """Комбинируем темы из разных источников"""
        logger.info("🔄 Комбинируем темы...")
        
        # Создаем финальные списки
        final_reddit = []
        final_twitter = []
        
        # Добавляем темы из дашборда (40%)
        final_reddit.extend(dashboard_reddit)
        final_twitter.extend(dashboard_twitter)
        
        # Добавляем Dynamic Desirability (30%)
        for topic in desirability:
            if topic not in final_reddit and len(final_reddit) < 10:
                final_reddit.append(topic)
            if topic not in final_twitter and len(final_twitter) < 10:
                final_twitter.append(topic)
        
        # Добавляем категорийные темы (30%)
        for topic in category_reddit:
            if topic not in final_reddit and len(final_reddit) < 10:
                final_reddit.append(topic)
        
        for topic in category_twitter:
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
        
        # Добавляем r/ префикс для Reddit тем, если его нет
        reddit_with_prefix = []
        for topic in reddit_topics:
            if not topic.startswith('r/') and not topic.startswith('#'):
                reddit_with_prefix.append(f"r/{topic}")
            else:
                reddit_with_prefix.append(topic)
        
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
                            "label_choices": reddit_with_prefix,
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
        logger.info("🚀 Начинаем продвинутую оптимизацию тем...")
        
        # Получаем данные из всех источников
        dashboard_df = self.fetch_dashboard_data()
        desirability_topics = self.fetch_dynamic_desirability()
        dashboard_reddit, dashboard_twitter = self.analyze_dashboard_data(dashboard_df)
        category_reddit, category_twitter = self.get_category_topics()
        
        # Комбинируем темы
        final_reddit, final_twitter = self.combine_topics(
            dashboard_reddit, dashboard_twitter, desirability_topics,
            category_reddit, category_twitter
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
    optimizer = AdvancedTopicOptimizer()
    success = optimizer.optimize_topics()
    
    if success:
        print("\n🎯 Рекомендации:")
        print("1. Перезапустите майнер с новой конфигурацией")
        print("2. Мониторьте метрики в течение 2-4 часов")
        print("3. Запускайте оптимизацию каждые 6-12 часов")
        print("4. Анализируйте логи для корректировки тем")
    else:
        print("\n⚠️ Оптимизация не завершена. Проверьте логи.")

if __name__ == "__main__":
    main()
