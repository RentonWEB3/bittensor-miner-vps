#!/usr/bin/env python3
import asyncio, json
from dynamic_desirability.desirability_retrieval import run_retrieval
from common.data import DataLabel
from common.utils import get_validator_data
import bittensor as bt

# Загружаем конфиг Bittensor (для доступа к metagraph и hotkeys)
from bittensor import config as btconfig
cfg = btconfig.config()

# Получаем lookup по весам тем
desirability_lookup = asyncio.run(run_retrieval(cfg))
# Берём все ярлыки с положительным весом
labels = [job.params.label for job in desirability_lookup.distribution.values() if job.weight > 0.1]

# Строим новую конфигурацию
scrapers = [
  {
    "scraper_id": "X.microworlds",
    "cadence_seconds": 300,
    "labels_to_scrape": [
      {
        "label_choices": labels,
        "max_age_hint_minutes": 1440,
        "max_data_entities": 100
      }
    ],
    "config": { "cookies_path": "twitter_cookies.json" }
  },
  {
    "scraper_id": "Reddit.custom",
    "cadence_seconds": 300,
    "labels_to_scrape": [
      {
        "label_choices": labels,
        "max_age_hint_minutes": 1440,
        "max_data_entities": 100
      }
    ],
    "config": {
      "subreddit": "all",
      "limit_per_label": 100
    }
  }
]

with open("scraping_config.json", "w", encoding="utf-8") as f:
    json.dump({"scraper_configs": scrapers}, f, ensure_ascii=False, indent=2)

print(f"Updated scraping_config.json with {len(labels)} labels.")
