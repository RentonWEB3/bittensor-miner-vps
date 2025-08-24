# scraping/storage.py

import os, json
from common.data import DataEntity
from datetime import datetime

def deduplicate_entities(entities: list[DataEntity]) -> list[DataEntity]:
    seen_uris = set()
    deduped = []
    for e in entities:
        if e.uri not in seen_uris:
            deduped.append(e)
            seen_uris.add(e.uri)
    return deduped

def save_data_entities(entities: list[DataEntity], source_name: str):
    if not os.path.exists("normalized"):
        os.makedirs("normalized")

    now_str = datetime.utcnow().strftime("%Y%m%d_%H%M")
    out_path = f"normalized/{source_name}_{now_str}.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for e in entities:
            f.write(e.model_dump_json() + "\n")
    print(f"[INFO] Saved {len(entities)} entities to {out_path}")
