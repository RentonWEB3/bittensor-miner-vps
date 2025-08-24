#!/bin/bash

# Автоматический оптимизатор тем для майнера Macrocosm
# Запускается по расписанию для обновления конфигурации

# Настройки
SCRIPT_DIR="/root/bittensor-miner-vps"
LOG_FILE="/root/bittensor-miner-vps/optimization.log"
PYTHON_PATH="/root/bittensor-miner-vps/venv/bin/python"

# Функция логирования
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Переходим в директорию скрипта
cd "$SCRIPT_DIR" || {
    log "❌ Ошибка: не удалось перейти в директорию $SCRIPT_DIR"
    exit 1
}

# Активируем виртуальное окружение
source venv/bin/activate || {
    log "❌ Ошибка: не удалось активировать виртуальное окружение"
    exit 1
}

log "🚀 Запуск автоматической оптимизации тем..."

# Запускаем оптимизатор
$PYTHON_PATH auto_topic_optimizer.py

if [ $? -eq 0 ]; then
    log "✅ Оптимизация завершена успешно"
    
    # Проверяем, изменилась ли конфигурация
    if [ -f "scraping_config_optimized.json" ]; then
        log "📋 Новая конфигурация создана"
        
        # Копируем новую конфигурацию
        cp scraping_config_optimized.json scraping_config_gravity.json
        
        log "🔄 Конфигурация обновлена"
        
        # Перезапускаем майнер (опционально)
        # pkill -f "python3.11 -m neurons.miner"
        # sleep 5
        # nohup python3.11 -m neurons.miner --neuron.scraping_config_file ./scraping_config_gravity.json --vpermit_rao_limit 1000 --gravity --neuron.axon_host 0.0.0.0 --logging.trace > miner.log 2>&1 &
        
        log "💡 Рекомендация: перезапустите майнер вручную для применения новой конфигурации"
    else
        log "⚠️ Новая конфигурация не создана"
    fi
else
    log "❌ Ошибка при оптимизации"
fi

log "🏁 Автоматическая оптимизация завершена"
