# 🤖 Автоматическая оптимизация тем для майнера Macrocosm

## 📋 Обзор

Система автоматически комбинирует данные из:
- **Dynamic Desirability (Gravity)** - активные запросы пользователей
- **Dashboard** - статистика дублирования и конкуренции
- **Нишевые темы** - уникальные темы с низкой конкуренцией

## 🚀 Установка

### 1. Загрузите файлы на VPS:
```bash
# На вашем локальном компьютере
scp auto_topic_optimizer.py root@193.233.165.120:~/bittensor-miner-vps/
scp auto_optimize_cron.sh root@193.233.165.120:~/bittensor-miner-vps/
```

### 2. Установите зависимости:
```bash
# На VPS
cd ~/bittensor-miner-vps
source venv/bin/activate
pip install pandas requests
```

### 3. Сделайте скрипт исполняемым:
```bash
chmod +x auto_optimize_cron.sh
```

## ⚙️ Настройка автоматизации

### Вариант 1: Cron (рекомендуется)
```bash
# Откройте crontab
crontab -e

# Добавьте строки для запуска каждые 6 часов:
0 */6 * * * /root/bittensor-miner-vps/auto_optimize_cron.sh

# Или каждые 12 часов:
0 */12 * * * /root/bittensor-miner-vps/auto_optimize_cron.sh
```

### Вариант 2: Systemd Timer
```bash
# Создайте файл сервиса
sudo nano /etc/systemd/system/topic-optimizer.service

[Unit]
Description=Topic Optimizer for Macrocosm Miner
After=network.target

[Service]
Type=oneshot
User=root
WorkingDirectory=/root/bittensor-miner-vps
ExecStart=/root/bittensor-miner-vps/auto_optimize_cron.sh

[Install]
WantedBy=multi-user.target
```

```bash
# Создайте файл таймера
sudo nano /etc/systemd/system/topic-optimizer.timer

[Unit]
Description=Run Topic Optimizer every 6 hours
Requires=topic-optimizer.service

[Timer]
OnCalendar=*-*-* 00/6:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
# Активируйте таймер
sudo systemctl enable topic-optimizer.timer
sudo systemctl start topic-optimizer.timer
```

## 🔧 Ручной запуск

### Тестовый запуск:
```bash
cd ~/bittensor-miner-vps
source venv/bin/activate
python auto_topic_optimizer.py
```

### Запуск через bash скрипт:
```bash
./auto_optimize_cron.sh
```

## 📊 Мониторинг

### Просмотр логов:
```bash
# Логи оптимизации
tail -f /root/bittensor-miner-vps/optimization.log

# Логи майнера
tail -f /root/bittensor-miner-vps/miner.log
```

### Проверка статуса cron:
```bash
# Просмотр активных cron задач
crontab -l

# Просмотр логов cron
tail -f /var/log/cron
```

## 🎯 Как это работает

### 1. Анализ Dashboard
- Получает статистику по всем темам
- Оценивает каждую тему по формуле: `(100 - размер_ГБ) * 0.7 + рост_% * 0.3`
- Выбирает темы с низкой конкуренцией и высоким ростом

### 2. Получение Dynamic Desirability
- Подключается к Gravity API
- Получает список тем с высоким спросом
- Приоритизирует эти темы

### 3. Комбинирование
- Сначала добавляет темы из Dynamic Desirability
- Затем добавляет лучшие темы из Dashboard
- Дополняет нишевыми темами при необходимости

### 4. Обновление конфигурации
- Создает резервную копию текущей конфигурации
- Генерирует новую оптимизированную конфигурацию
- Обновляет файл конфигурации

## 🔄 Жизненный цикл

```
Каждые 6-12 часов:
1. 📊 Анализ Dashboard → низкая конкуренция
2. ⭐ Получение Dynamic Desirability → высокий спрос  
3. 🔄 Комбинирование тем → оптимальный набор
4. ⚙️ Обновление конфигурации → новая стратегия
5. 🚀 Перезапуск майнера → применение изменений
6. 📈 Мониторинг метрик → проверка эффективности
```

## 🛠️ Настройка параметров

### Изменение частоты оптимизации:
```bash
# В crontab измените интервал:
0 */4 * * *  # Каждые 4 часа
0 */8 * * *  # Каждые 8 часов
0 */12 * * * # Каждые 12 часов
```

### Изменение количества тем:
```python
# В auto_topic_optimizer.py измените:
return combined_topics[:15]  # 15 тем вместо 20
```

### Изменение весов оценки:
```python
# В analyze_dashboard_data() измените:
total_score = (size_score * 0.8) + (growth_score * 0.2)  # Больше веса размеру
```

## 🚨 Устранение неполадок

### Проблема: Не удается получить данные с Dashboard
```bash
# Проверьте доступность:
curl -I https://sn13-dashboard.api.macrocosmos.ai/

# Проверьте логи:
tail -f optimization.log | grep "dashboard"
```

### Проблема: Не удается получить Dynamic Desirability
```bash
# Проверьте доступность Gravity API:
curl -I https://gravity.api.macrocosmos.ai/api/desirability

# Проверьте логи:
tail -f optimization.log | grep "desirability"
```

### Проблема: Конфигурация не обновляется
```bash
# Проверьте права доступа:
ls -la scraping_config_*.json

# Проверьте свободное место:
df -h
```

## 📈 Ожидаемые результаты

После настройки автоматизации:

### Через 1-2 часа:
- ✅ Новые темы начнут скрапиться
- ✅ Снизится дублирование данных
- ✅ Улучшится качество контента

### Через 6-12 часов:
- 📈 Рост метрик Consensus
- 📈 Рост метрик Incentive  
- 📈 Улучшение Trust

### Через 24-48 часов:
- 🎯 Стабильные высокие метрики
- 🎯 Оптимальная стратегия скрапинга
- 🎯 Максимальная эффективность майнера

## 🔗 Полезные ссылки

- [Macrocosm Documentation](https://github.com/macrocosm-os/data-universe)
- [Dashboard](https://sn13-dashboard.api.macrocosmos.ai/)
- [Gravity](https://gravity.api.macrocosmos.ai/)
- [Taostats](https://taostats.io/)
