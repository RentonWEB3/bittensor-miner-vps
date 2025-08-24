# 🚀 Команды для развертывания на сервере

## 1. Подключиться к серверу
```bash
ssh root@193.233.165.120
```

## 2. Перейти в директорию проекта
```bash
cd ~/bittensor-miner-vps
```

## 3. Остановить майнер
```bash
pkill -f "neurons.miner"
```

## 4. Создать резервные копии
```bash
cp dynamic_desirability/data.py dynamic_desirability/data_backup.py
cp dynamic_desirability/desirability_retrieval.py dynamic_desirability/desirability_retrieval_backup.py
```

## 5. Получить исправления с GitHub
```bash
git pull origin main
```

## 6. Проверить изменения
```bash
git log --oneline -5
git diff HEAD~1 dynamic_desirability/
```

## 7. Перезапустить майнер
```bash
source venv/bin/activate && source .env && nohup python3.11 -m neurons.miner --neuron.scraping_config_file ./scraping_config_gravity.json --vpermit_rao_limit 1000 --gravity --neuron.axon_host 0.0.0.0 --logging.trace > miner.log 2>&1 &
```

## 8. Проверить логи
```bash
tail -f miner.log | grep -i "desirability\|gravity\|error"
```

## 9. Проверить Dynamic Desirability
```bash
# Проверить размер total.json (должен увеличиться)
ls -la dynamic_desirability/total.json

# Проверить содержимое (должны быть реальные темы, а не default)
head -20 dynamic_desirability/total.json

# Проверить количество записей
python3.11 -c "
import json
with open('dynamic_desirability/total.json', 'r') as f:
    data = json.load(f)
    print(f'Всего записей: {len(data)}')
    print('Первые 5 записей:')
    for i, item in enumerate(data[:5]):
        print(f'{i+1}. {item.get(\"id\", \"N/A\")} - {item.get(\"params\", {}).get(\"label\", \"N/A\")}')
"
```

## 10. Ожидаемые результаты
- ✅ Ошибка "1 validation error for Job" должна исчезнуть
- ✅ `total.json` должен содержать реальные темы от валидаторов
- ✅ Размер `total.json` должен увеличиться
- ✅ В логах должно появиться "Total weights have been calculated and written to total.json"
- ✅ Метрики должны улучшиться
