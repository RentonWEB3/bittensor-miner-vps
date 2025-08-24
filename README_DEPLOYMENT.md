# 🚀 Bittensor Miner Deployment Guide

## Описание
Рабочий майнер для Bittensor Subnet 13 с поддержкой:
- ✅ Dynamic Desirability (Gravity)
- ✅ Reddit и Twitter скрапинг
- ✅ HuggingFace загрузки
- ✅ Оптимизированные настройки

## Быстрое развертывание на VPS

### 1. Подготовка сервера
```bash
# Обновить систему
sudo apt update && sudo apt upgrade -y

# Установить Python 3.11
sudo apt install python3.11 python3.11-pip python3.11-venv -y

# Установить Git
sudo apt install git -y
```

### 2. Клонирование репозитория
```bash
git clone https://github.com/YOUR_USERNAME/bittensor-miner-vps.git
cd bittensor-miner-vps
```

### 3. Настройка окружения
```bash
# Создать виртуальное окружение
python3.11 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
```

### 4. Настройка конфигурации

#### A. Создать файл с переменными окружения
```bash
cat > .env << EOF
REDDIT_CLIENT_ID="YOUR_REDDIT_CLIENT_ID"
REDDIT_CLIENT_SECRET="YOUR_REDDIT_CLIENT_SECRET"
HUGGINGFACE_TOKEN="YOUR_HUGGINGFACE_TOKEN"
EOF
```

#### B. Настроить Twitter cookies
```bash
# Создать twitter_cookies.json с вашими куками
```

#### C. Настроить Bittensor кошелек
```bash
# Создать кошелек
btcli wallet new_coldkey --wallet.name default
btcli wallet new_hotkey --wallet.name default --wallet.hotkey default

# Зарегистрировать hotkey в subnet 13
btcli subnet register --wallet.name default --wallet.hotkey default --subtensor.network finney --netuid 13
```

### 5. Запуск майнера
```bash
# Загрузить переменные окружения
source .env

# Запустить майнер
nohup python3.11 -m neurons.miner \
  --neuron.scraping_config_file ./scraping_config_gravity.json \
  --vpermit_rao_limit 1000 \
  --gravity \
  --neuron.axon_host 0.0.0.0 \
  --logging.trace > miner.log 2>&1 &
```

### 6. Мониторинг
```bash
# Просмотр логов
tail -f miner.log

# Проверка статуса
ps aux | grep miner

# Проверка метрик
python3.11 -c "
import bittensor as bt
subtensor = bt.subtensor(network='finney')
metagraph = subtensor.metagraph(netuid=13)
hotkey = 'YOUR_HOTKEY'
uid = metagraph.hotkeys.index(hotkey)
print(f'Trust: {float(metagraph.T[uid]):.6f}')
print(f'Consensus: {float(metagraph.C[uid]):.6f}')
print(f'Incentive: {float(metagraph.I[uid]):.6f}')
"
```

## Настройка Firewall

### UFW (Ubuntu)
```bash
# Установить UFW
sudo apt install ufw

# Разрешить SSH
sudo ufw allow ssh

# Разрешить порт майнера
sudo ufw allow 8091

# Включить firewall
sudo ufw enable
```

### iptables
```bash
# Разрешить порт 8091
sudo iptables -A INPUT -p tcp --dport 8091 -j ACCEPT
sudo iptables-save
```

## Автозапуск (systemd)

### Создать сервис
```bash
sudo nano /etc/systemd/system/bittensor-miner.service
```

### Содержимое файла
```ini
[Unit]
Description=Bittensor Miner
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/bittensor-miner-vps
Environment=PATH=/home/YOUR_USERNAME/bittensor-miner-vps/venv/bin
ExecStart=/home/YOUR_USERNAME/bittensor-miner-vps/venv/bin/python -m neurons.miner --neuron.scraping_config_file ./scraping_config_gravity.json --vpermit_rao_limit 1000 --gravity --neuron.axon_host 0.0.0.0 --logging.trace
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Активировать сервис
```bash
sudo systemctl daemon-reload
sudo systemctl enable bittensor-miner
sudo systemctl start bittensor-miner
```

## Мониторинг и логи

### Просмотр логов
```bash
# systemd сервис
sudo journalctl -u bittensor-miner -f

# Ручной запуск
tail -f miner.log
```

### Проверка статуса
```bash
# Статус сервиса
sudo systemctl status bittensor-miner

# Процессы
ps aux | grep miner

# Порт
netstat -tlnp | grep 8091
```

## Troubleshooting

### Проблема: Нет метрик
- Проверить доступность порта 8091 извне
- Проверить firewall на VPS
- Проверить логи на ошибки

### Проблема: Нет данных
- Проверить Reddit API ключи
- Проверить Twitter cookies
- Проверить HuggingFace токен

### Проблема: Майнер не запускается
- Проверить Python версию (должна быть 3.11+)
- Проверить зависимости
- Проверить права доступа к файлам

## Полезные команды

```bash
# Остановить майнер
sudo systemctl stop bittensor-miner

# Перезапустить майнер
sudo systemctl restart bittensor-miner

# Проверить метрики
python3.11 -c "import bittensor as bt; subtensor = bt.subtensor(network='finney'); metagraph = subtensor.metagraph(netuid=13); hotkey = 'YOUR_HOTKEY'; uid = metagraph.hotkeys.index(hotkey); print(f'Trust: {float(metagraph.T[uid]):.6f}'); print(f'Consensus: {float(metagraph.C[uid]):.6f}'); print(f'Incentive: {float(metagraph.I[uid]):.6f}')"

# Проверить доступность
curl -s http://localhost:8091/health
```

## Поддержка

При возникновении проблем:
1. Проверьте логи: `tail -f miner.log`
2. Проверьте статус сервиса: `sudo systemctl status bittensor-miner`
3. Проверьте доступность порта: `netstat -tlnp | grep 8091`
4. Проверьте метрики в метаграфе
