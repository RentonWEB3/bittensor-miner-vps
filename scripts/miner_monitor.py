#!/usr/bin/env python3
"""
Скрипт мониторинга и управления майнером Macrocosmos
Предоставляет веб-интерфейс для мониторинга состояния майнера
"""

import argparse
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import bittensor as bt
from flask import Flask, render_template, jsonify, request
import requests

# Настройки Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

class MinerMonitor:
    """Класс для мониторинга майнера"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path
        self.last_check = datetime.now()
        self.check_interval = 60  # секунды
        self.monitoring_data = {}
        self.is_monitoring = False
        
    def start_monitoring(self):
        """Запуск мониторинга"""
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("🔍 Мониторинг майнера запущен")
    
    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.is_monitoring = False
        print("⏹️ Мониторинг майнера остановлен")
    
    def _monitor_loop(self):
        """Основной цикл мониторинга"""
        while self.is_monitoring:
            try:
                self._collect_metrics()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Ошибка в цикле мониторинга: {e}")
                time.sleep(10)
    
    def _collect_metrics(self):
        """Сбор метрик майнера"""
        try:
            # Проверка файлов диагностики
            diagnostic_files = list(Path("diagnostics").glob("diagnostic_*.json"))
            if diagnostic_files:
                latest_diagnostic = max(diagnostic_files, key=lambda x: x.stat().st_mtime)
                with open(latest_diagnostic, 'r', encoding='utf-8') as f:
                    diagnostic_data = json.load(f)
                
                self.monitoring_data['diagnostic'] = diagnostic_data
                self.monitoring_data['last_update'] = datetime.now().isoformat()
            
            # Проверка логов
            self._check_logs()
            
            # Проверка состояния процесса
            self._check_process_status()
            
        except Exception as e:
            print(f"Ошибка при сборе метрик: {e}")
    
    def _check_logs(self):
        """Проверка логов майнера"""
        try:
            # Проверяем последние логи (можно настроить путь к логам)
            log_path = Path("logs/miner.log")
            if log_path.exists():
                with open(log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    last_lines = lines[-50:]  # Последние 50 строк
                    
                # Анализ логов на наличие ошибок
                errors = [line for line in last_lines if 'ERROR' in line or 'CRITICAL' in line]
                warnings = [line for line in last_lines if 'WARNING' in line]
                
                self.monitoring_data['logs'] = {
                    'last_lines': last_lines[-10:],  # Последние 10 строк
                    'error_count': len(errors),
                    'warning_count': len(warnings),
                    'recent_errors': errors[-5:] if errors else [],
                    'recent_warnings': warnings[-5:] if warnings else []
                }
        except Exception as e:
            print(f"Ошибка при проверке логов: {e}")
    
    def _check_process_status(self):
        """Проверка статуса процесса майнера"""
        try:
            # Проверяем, запущен ли процесс через pm2
            result = requests.get("http://localhost:3000/api/processes", timeout=5)
            if result.status_code == 200:
                processes = result.json()
                miner_process = next((p for p in processes if 'miner' in p['name'].lower()), None)
                
                if miner_process:
                    self.monitoring_data['process'] = {
                        'status': miner_process['pm2_env']['status'],
                        'uptime': miner_process['pm2_env']['pm_uptime'],
                        'memory': miner_process['monit']['memory'],
                        'cpu': miner_process['monit']['cpu']
                    }
                else:
                    self.monitoring_data['process'] = {'status': 'not_found'}
            else:
                self.monitoring_data['process'] = {'status': 'pm2_unavailable'}
                
        except Exception as e:
            self.monitoring_data['process'] = {'status': 'error', 'error': str(e)}
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Получение сводки статуса"""
        if not self.monitoring_data:
            return {'status': 'no_data'}
        
        diagnostic = self.monitoring_data.get('diagnostic', {})
        process = self.monitoring_data.get('process', {})
        logs = self.monitoring_data.get('logs', {})
        
        # Определение общего статуса
        status = 'healthy'
        issues = []
        
        if diagnostic.get('issues'):
            status = 'critical'
            issues.extend(diagnostic['issues'])
        
        if process.get('status') != 'online':
            status = 'warning'
            issues.append(f"Процесс: {process.get('status', 'unknown')}")
        
        if logs.get('error_count', 0) > 0:
            status = 'warning'
            issues.append(f"Ошибки в логах: {logs['error_count']}")
        
        return {
            'status': status,
            'issues': issues,
            'last_update': self.monitoring_data.get('last_update'),
            'uptime': diagnostic.get('uptime_seconds', 0),
            'data_entities': diagnostic.get('metrics', {}).get('data', {}).get('total_entities', 0),
            'incentives': diagnostic.get('metrics', {}).get('incentives', {}).get('relative_incentive', 0)
        }

# Создаем экземпляр монитора
monitor = MinerMonitor()

@app.route('/')
def dashboard():
    """Главная страница дашборда"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """API для получения статуса майнера"""
    return jsonify(monitor.get_status_summary())

@app.route('/api/metrics')
def get_metrics():
    """API для получения полных метрик"""
    return jsonify(monitor.monitoring_data)

@app.route('/api/diagnostic')
def run_diagnostic():
    """API для запуска диагностики"""
    try:
        # Здесь можно добавить вызов диагностики майнера
        return jsonify({'status': 'success', 'message': 'Диагностика запущена'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/restart')
def restart_miner():
    """API для перезапуска майнера"""
    try:
        # Перезапуск через pm2
        import subprocess
        result = subprocess.run(['pm2', 'restart', 'net13-miner'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            return jsonify({'status': 'success', 'message': 'Майнер перезапущен'})
        else:
            return jsonify({'status': 'error', 'message': result.stderr})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/logs')
def get_logs():
    """API для получения логов"""
    try:
        log_path = Path("logs/miner.log")
        if log_path.exists():
            with open(log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                return jsonify({
                    'status': 'success',
                    'logs': lines[-100:]  # Последние 100 строк
                })
        else:
            return jsonify({'status': 'error', 'message': 'Файл логов не найден'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def create_templates():
    """Создание HTML шаблонов"""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Создаем основной шаблон
    dashboard_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Мониторинг майнера Macrocosmos</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .status-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .status-healthy { border-left: 5px solid #28a745; }
        .status-warning { border-left: 5px solid #ffc107; }
        .status-critical { border-left: 5px solid #dc3545; }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .metric-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }
        .metric-label {
            color: #666;
            font-size: 14px;
        }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        .btn:hover { background: #5a6fd8; }
        .btn-danger { background: #dc3545; }
        .btn-danger:hover { background: #c82333; }
        .logs {
            background: #1e1e1e;
            color: #fff;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            max-height: 300px;
            overflow-y: auto;
        }
        .refresh-btn {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 18px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Мониторинг майнера Macrocosmos</h1>
            <p>Subnet 13 - Data Universe</p>
        </div>
        
        <button class="refresh-btn" onclick="refreshData()">🔄</button>
        
        <div id="status-card" class="status-card">
            <h2>Статус системы</h2>
            <div id="status-content">Загрузка...</div>
        </div>
        
        <div class="metric-grid" id="metrics-grid">
            <!-- Метрики будут загружены динамически -->
        </div>
        
        <div class="status-card">
            <h2>Действия</h2>
            <button class="btn" onclick="runDiagnostic()">🔍 Запустить диагностику</button>
            <button class="btn btn-danger" onclick="restartMiner()">🔄 Перезапустить майнер</button>
            <button class="btn" onclick="showLogs()">📋 Показать логи</button>
        </div>
        
        <div class="status-card" id="logs-section" style="display: none;">
            <h2>Логи майнера</h2>
            <div class="logs" id="logs-content"></div>
        </div>
    </div>

    <script>
        function refreshData() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => updateStatus(data));
                
            fetch('/api/metrics')
                .then(response => response.json())
                .then(data => updateMetrics(data));
        }
        
        function updateStatus(data) {
            const statusCard = document.getElementById('status-card');
            const statusContent = document.getElementById('status-content');
            
            // Обновляем класс статуса
            statusCard.className = `status-card status-${data.status}`;
            
            let statusHtml = `
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="metric-value">${data.status.toUpperCase()}</div>
                        <div class="metric-label">Статус</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${Math.round(data.uptime / 3600)}ч</div>
                        <div class="metric-label">Время работы</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${data.data_entities || 0}</div>
                        <div class="metric-label">Сущностей данных</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${(data.incentives * 100).toFixed(2)}%</div>
                        <div class="metric-label">Относительные стимулы</div>
                    </div>
                </div>
            `;
            
            if (data.issues && data.issues.length > 0) {
                statusHtml += '<h3>Проблемы:</h3><ul>';
                data.issues.forEach(issue => {
                    statusHtml += `<li>${issue}</li>`;
                });
                statusHtml += '</ul>';
            }
            
            statusContent.innerHTML = statusHtml;
        }
        
        function updateMetrics(data) {
            const metricsGrid = document.getElementById('metrics-grid');
            
            if (data.diagnostic && data.diagnostic.metrics) {
                const metrics = data.diagnostic.metrics;
                let metricsHtml = '';
                
                if (metrics.data) {
                    metricsHtml += `
                        <div class="metric-card">
                            <div class="metric-value">${metrics.data.total_entities || 0}</div>
                            <div class="metric-label">Всего сущностей</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${metrics.data.total_buckets || 0}</div>
                            <div class="metric-label">Всего бакетов</div>
                        </div>
                    `;
                }
                
                if (metrics.incentives) {
                    metricsHtml += `
                        <div class="metric-card">
                            <div class="metric-value">${metrics.incentives.position || 'N/A'}</div>
                            <div class="metric-label">Позиция в рейтинге</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${metrics.incentives.total_miners || 0}</div>
                            <div class="metric-label">Всего майнеров</div>
                        </div>
                    `;
                }
                
                metricsGrid.innerHTML = metricsHtml;
            }
        }
        
        function runDiagnostic() {
            fetch('/api/diagnostic')
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    setTimeout(refreshData, 2000);
                });
        }
        
        function restartMiner() {
            if (confirm('Вы уверены, что хотите перезапустить майнер?')) {
                fetch('/api/restart')
                    .then(response => response.json())
                    .then(data => {
                        alert(data.message);
                        setTimeout(refreshData, 5000);
                    });
            }
        }
        
        function showLogs() {
            fetch('/api/logs')
                .then(response => response.json())
                .then(data => {
                    const logsSection = document.getElementById('logs-section');
                    const logsContent = document.getElementById('logs-content');
                    
                    if (data.status === 'success') {
                        logsContent.innerHTML = data.logs.join('<br>');
                        logsSection.style.display = 'block';
                    } else {
                        alert(data.message);
                    }
                });
        }
        
        // Автообновление каждые 30 секунд
        setInterval(refreshData, 30000);
        
        // Загрузка данных при загрузке страницы
        document.addEventListener('DOMContentLoaded', refreshData);
    </script>
</body>
</html>
    """
    
    with open(templates_dir / "dashboard.html", "w", encoding="utf-8") as f:
        f.write(dashboard_html)

def main():
    parser = argparse.ArgumentParser(description="Мониторинг майнера Macrocosmos")
    parser.add_argument("--port", type=int, default=8080, help="Порт для веб-интерфейса")
    parser.add_argument("--host", default="0.0.0.0", help="Хост для веб-интерфейса")
    parser.add_argument("--no-monitor", action="store_true", help="Не запускать мониторинг")
    
    args = parser.parse_args()
    
    # Создаем шаблоны
    create_templates()
    
    # Запускаем мониторинг
    if not args.no_monitor:
        monitor.start_monitoring()
    
    print(f"🌐 Веб-интерфейс доступен по адресу: http://{args.host}:{args.port}")
    print("📊 Откройте браузер для просмотра дашборда")
    
    # Запускаем Flask приложение
    app.run(host=args.host, port=args.port, debug=False)

if __name__ == "__main__":
    main()
