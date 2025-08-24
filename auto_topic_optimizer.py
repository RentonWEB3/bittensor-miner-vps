#!/usr/bin/env python3
"""
Автоматический оптимизатор тем для майнера Macrocosm
Комбинирует Dynamic Desirability и Dashboard данные для максимальной эффективности
"""

import json
import requests
import pandas as pd
import time
import logging
from typing import List, Dict, Tuple
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TopicOptimizer:
    def __init__(self):
        self.dashboard_url = "https://sn13-dashboard.api.macrocosmos.ai/"
        self.gravity_url = "https://gravity.api.macrocosmos.ai/api/desirability"  # Предполагаемый URL
        self.config_file = "scraping_config_optimized.json"
        self.backup_file = "scraping_config_backup.json"
        
    def fetch_dashboard_data(self) -> pd.DataFrame:
        """Получает данные с дашборда"""
        try:
            # Пытаемся получить данные с дашборда
            response = requests.get(f"{self.dashboard_url}/api/stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return pd.DataFrame(data)
            else:
                logger.warning(f"Не удалось получить данные с дашборда: {response.status_code}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Ошибка при получении данных с дашборда: {e}")
            return pd.DataFrame()
    
    def fetch_dynamic_desirability(self) -> List[str]:
        """Получает список желаемых тем из Dynamic Desirability"""
        try:
            # Пытаемся получить данные из Gravity API
            response = requests.get(self.gravity_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('desirable_topics', [])
            else:
                logger.warning(f"Не удалось получить Dynamic Desirability: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Ошибка при получении Dynamic Desirability: {e}")
            return []
    
    def analyze_dashboard_data(self, df: pd.DataFrame) -> Dict[str, float]:
        """Анализирует данные дашборда и возвращает оценку тем"""
        if df.empty:
            return {}
        
        # Создаем оценку на основе размера данных и роста
        topic_scores = {}
        
        for _, row in df.iterrows():
            label = row.get('label', '')
            size_gb = row.get('size collected', 0)
            growth = row.get('vs. previous day', 0)
            
            if label and label != 'NULL':
                # Оценка: меньше данных = лучше, больше роста = лучше
                # Нормализуем размер (меньше = лучше)
                size_score = max(0, 100 - size_gb) / 100
                
                # Нормализуем рост (больше = лучше)
                growth_score = min(1.0, max(0, growth) / 100)
                
                # Общая оценка
                total_score = (size_score * 0.7) + (growth_score * 0.3)
                topic_scores[label] = total_score
        
        return topic_scores
    
    def combine_topics(self, dashboard_scores: Dict[str, float], 
                      desirability_topics: List[str]) -> List[str]:
        """Комбинирует темы из обоих источников"""
        combined_topics = []
        
        # 1. Добавляем темы из Dynamic Desirability (высший приоритет)
        for topic in desirability_topics:
            if topic not in combined_topics:
                combined_topics.append(topic)
                logger.info(f"✅ Добавлена тема из Dynamic Desirability: {topic}")
        
        # 2. Добавляем лучшие темы из дашборда (низкая конкуренция)
        sorted_dashboard = sorted(dashboard_scores.items(), 
                                key=lambda x: x[1], reverse=True)
        
        for topic, score in sorted_dashboard[:10]:  # Топ-10 из дашборда
            if topic not in combined_topics and score > 0.5:
                combined_topics.append(topic)
                logger.info(f"📊 Добавлена тема из дашборда: {topic} (оценка: {score:.2f})")
        
        # 3. Добавляем нишевые темы (если нужно больше разнообразия)
        niche_topics = [
            "growagarden", "productivitycafe", "nightreign", 
            "teenagersbutbetter", "market76", "helldivers",
            "genshin_impact_leaks", "gunaccessoriesforsale",
            "originalcharacter", "technology", "teslamotors",
            "electricvehicles", "solar", "windenergy", "climatechange"
        ]
        
        for topic in niche_topics:
            if topic not in combined_topics and len(combined_topics) < 20:
                combined_topics.append(topic)
                logger.info(f"🎯 Добавлена нишевая тема: {topic}")
        
        return combined_topics[:20]  # Ограничиваем до 20 тем
    
    def create_optimized_config(self, topics: List[str]) -> Dict:
        """Создает оптимизированную конфигурацию скрапинга"""
        config = {
            "scraper_configs": [
                {
                    "scraper_id": "X.microworlds",
                    "cadence_seconds": 300,
                    "labels_to_scrape": [
                        {
                            "label_choices": topics[:10],  # Первые 10 тем для Twitter
                            "max_age_hint_minutes": 1440,
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
                            "label_choices": topics,  # Все темы для Reddit
                            "max_age_hint_minutes": 1440,
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
    
    def backup_current_config(self):
        """Создает резервную копию текущей конфигурации"""
        try:
            with open(self.config_file, 'r') as f:
                current_config = json.load(f)
            
            with open(self.backup_file, 'w') as f:
                json.dump(current_config, f, indent=2)
            
            logger.info(f"✅ Резервная копия создана: {self.backup_file}")
        except Exception as e:
            logger.warning(f"Не удалось создать резервную копию: {e}")
    
    def update_config(self, new_config: Dict):
        """Обновляет конфигурацию"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(new_config, f, indent=2)
            
            logger.info(f"✅ Конфигурация обновлена: {self.config_file}")
            logger.info(f"📋 Темы: {new_config['platforms']['reddit']['labels']}")
        except Exception as e:
            logger.error(f"Ошибка при обновлении конфигурации: {e}")
    
    def optimize_topics(self) -> bool:
        """Основная функция оптимизации"""
        logger.info("🚀 Начинаем оптимизацию тем...")
        
        # 1. Получаем данные с дашборда
        logger.info("📊 Получаем данные с дашборда...")
        dashboard_df = self.fetch_dashboard_data()
        dashboard_scores = self.analyze_dashboard_data(dashboard_df)
        
        # 2. Получаем Dynamic Desirability
        logger.info("⭐ Получаем Dynamic Desirability...")
        desirability_topics = self.fetch_dynamic_desirability()
        
        # 3. Комбинируем темы
        logger.info("🔄 Комбинируем темы...")
        optimized_topics = self.combine_topics(dashboard_scores, desirability_topics)
        
        if not optimized_topics:
            logger.error("❌ Не удалось получить темы для оптимизации")
            return False
        
        # 4. Создаем новую конфигурацию
        logger.info("⚙️ Создаем оптимизированную конфигурацию...")
        new_config = self.create_optimized_config(optimized_topics)
        
        # 5. Создаем резервную копию
        self.backup_current_config()
        
        # 6. Обновляем конфигурацию
        self.update_config(new_config)
        
        logger.info(f"🎉 Оптимизация завершена! Выбрано {len(optimized_topics)} тем")
        return True

def main():
    """Главная функция"""
    optimizer = TopicOptimizer()
    
    # Запускаем оптимизацию
    success = optimizer.optimize_topics()
    
    if success:
        print("\n🎯 Рекомендации:")
        print("1. Перезапустите майнер с новой конфигурацией")
        print("2. Мониторьте метрики в течение 1-2 часов")
        print("3. Запускайте оптимизацию каждые 6-12 часов")
    else:
        print("\n❌ Оптимизация не удалась. Проверьте логи.")

if __name__ == "__main__":
    main()
