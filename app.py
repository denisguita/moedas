"""
CriptoBR IA PRO - Aplicação Flask com Integração Real do Telegram
Monitora criptomoedas em tempo real e envia alertas para o Telegram
"""

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import json
import threading
import time
from datetime import datetime
import requests
from telegram_service import TelegramAlertService
import os # Adicionado para obter a porta do ambiente

app = Flask(__name__)
CORS(app)

# Configurar o serviço de Telegram
TELEGRAM_TOKEN = "7834485201:AAExDXuQJprwbv3ofUIOg5zrliXrDeA0-vU"
TELEGRAM_CHAT_ID = "695440902"
telegram_service = TelegramAlertService(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)

# Dados simulados das criptomoedas
cryptos_data = {
    'JASMY': {'price': 0.00604622, 'change24h': -0.10, 'rsi': 53.06, 'volume': 1250000, 'signal': None},
    'MOG': {'price': 0.00000085, 'change24h': 4.31, 'rsi': 30.99, 'volume': 890000, 'signal': None},
    'VISTA': {'price': 0.03106417, 'change24h': 0.02, 'rsi': 71.50, 'volume': 450000, 'signal': 'VENDA'},
    'XTZ': {'price': 0.79112302, 'change24h': -2.25, 'rsi': 74.34, 'volume': 320000, 'signal': 'VENDA'},
    'TRUMP': {'price': 0.03296450, 'change24h': 1.08, 'rsi': 52.67, 'volume': 780000, 'signal': None},
    'PEPE': {'price': 0.00000077, 'change24h': 3.85, 'rsi': 32.74, 'volume': 2100000, 'signal': None},
    'WLFI': {'price': 0.00071164, 'change24h': -1.82, 'rsi': 70.35, 'volume': 150000, 'signal': 'VENDA'},
}

# Histórico de alertas
alerts_history = []

# Flag para controlar o monitoramento
monitoring_active = True

def schedule_report():
    """Agenda o envio do relatório para o Telegram a cada 20 minutos."""
    while monitoring_active:
        print("Enviando relatório agendado...")
        cryptos_for_report = [
            {'symbol': symbol, 'change24h': data['change24h'], 'rsi': data['rsi'], 'signal': data['signal']}
            for symbol, data in cryptos_data.items()
        ]
        telegram_service.send_daily_report(cryptos_for_report)
        # Espera 20 minutos (1200 segundos)
        time.sleep(1200)

def update_crypto_prices():
    """Atualiza os preços das criptomoedas em tempo real (simulado)"""
    global cryptos_data, alerts_history
    
    while monitoring_active:
        try:
            # Simular flutuações de preço
            import random
            
            for symbol in cryptos_data:
                # Simular mudança de preço
                change = random.uniform(-0.5, 0.5)
                cryptos_data[symbol]['price'] *= (1 + change / 100)
                cryptos_data[symbol]['change24h'] += random.uniform(-0.1, 0.1)
                
                # Simular mudança de RSI
                rsi_change = random.uniform(-2, 2)
                cryptos_data[symbol]['rsi'] = max(0, min(100, cryptos_data[symbol]['rsi'] + rsi_change))
                
                # Gerar sinais baseado no RSI
                old_signal = cryptos_data[symbol]['signal']
                
                if cryptos_data[symbol]['rsi'] < 30:
                    cryptos_data[symbol]['signal'] = 'COMPRA'
                elif cryptos_data[symbol]['rsi'] > 70:
                    cryptos_data[symbol]['signal'] = 'VENDA'
                else:
                    cryptos_data[symbol]['signal'] = None
                
                # Se houve mudança de sinal, enviar alerta para o Telegram
                if cryptos_data[symbol]['signal'] and cryptos_data[symbol]['signal'] != old_signal:
                    telegram_service.send_alert(
                        crypto_symbol=symbol,
                        signal_type=cryptos_data[symbol]['signal'],
                        price=cryptos_data[symbol]['price'],
                        confidence=85.0 + random.uniform(-5, 5),
                        rsi=cryptos_data[symbol]['rsi'],
                        volume=cryptos_data[symbol]['volume']
                    )
                    
                    # Adicionar ao histórico local
                    alerts_history.append({
                        'timestamp': datetime.now().strftime("%H:%M:%S"),
                        'crypto': symbol,
                        'signal': cryptos_data[symbol]['signal'],
                        'price': cryptos_data[symbol]['price'],
                        'rsi': cryptos_data[symbol]['rsi']
                    })
            
            time.sleep(5)  # Atualizar a cada 5 segundos
            
        except Exception as e:
            print(f"Erro ao atualizar preços: {e}")
            time.sleep(5)

# Iniciar thread de monitoramento
monitoring_thread = threading.Thread(target=update_crypto_prices, daemon=True)
monitoring_thread.start()

# Iniciar thread de relatório
report_thread = threading.Thread(target=schedule_report, daemon=True)
report_thread.start()

# HTML da aplicação
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-PT">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CriptoBR IA PRO - Telegram Integrado</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100% ); color: #e2e8f0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        .logo { font-size: 28px; font-weight: bold; background: linear-gradient(135deg, #10b981 0%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .latency { font-size: 12px; color: #10b981; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 1px solid #334155; }
        .tab { padding: 12px 20px; cursor: pointer; border-bottom: 3px solid transparent; transition: all 0.3s; }
        .tab.active { border-bottom-color: #10b981; color: #10b981; }
        .tab:hover { color: #10b981; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .crypto-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .crypto-card { background: rgba(30, 41, 59, 0.8); border: 1px solid #334155; border-radius: 12px; padding: 20px; transition: all 0.3s; }
        .crypto-card:hover { border-color: #10b981; box-shadow: 0 0 20px rgba(16, 185, 129, 0.2); }
        .crypto-name { font-size: 18px; font-weight: bold; margin-bottom: 10px; }
        .crypto-price { font-size: 24px; font-weight: bold; color: #10b981; margin-bottom: 10px; }
        .crypto-change { font-size: 14px; margin-bottom: 10px; }
        .positive { color: #10b981; }
        .negative { color: #ef4444; }
        .signal-badge { display: inline-block; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: bold; margin-top: 10px; }
        .signal-buy { background: rgba(16, 185, 129, 0.2); color: #10b981; }
        .signal-sell { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
        .button { padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; transition: all 0.3s; }
        .button-primary { background: #10b981; color: white; }
        .button-primary:hover { background: #059669; }
        .button-secondary { background: #3b82f6; color: white; }
        .button-secondary:hover { background: #2563eb; }
        .alert-item { background: rgba(30, 41, 59, 0.8); border-left: 4px solid #10b981; padding: 15px; margin-bottom: 10px; border-radius: 6px; }
        .alert-time { font-size: 12px; color: #94a3b8; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .stat-card { background: rgba(30, 41, 59, 0.8); border: 1px solid #334155; border-radius: 12px; padding: 15px; text-align: center; }
        .stat-value { font-size: 24px; font-weight: bold; color: #10b981; }
        .stat-label { font-size: 12px; color: #94a3b8; margin-top: 5px; }
        .chart-container { background: rgba(30, 41, 59, 0.8); border: 1px solid #334155; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
        .input-field { background: rgba(15, 23, 42, 0.8); border: 1px solid #334155; color: #e2e8f0; padding: 10px 15px; border-radius: 6px; margin-bottom: 10px; width: 100%; }
        .success-message { background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #10b981; padding: 15px; border-radius: 6px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <div class="logo">CriptoBR IA PRO</div>
                <div style="font-size: 12px; color: #94a3b8; margin-top: 5px;">Inteligência Financeira em Tempo Real com Telegram</div>
            </div>
            <div style="text-align: right;">
                <div class="latency" id="latency">● 0ms</div>
                <div style="font-size: 12px; color: #94a3b8; margin-top: 5px;">Utilizador: demo@criptobr.com</div>
            </div>
        </div>

        <div class="tabs">
            <div class="tab active" onclick="switchTab('dashboard')">📊 Dashboard</div>
            <div class="tab" onclick="switchTab('alerts')">🔔 Alertas</div>
            <div class="tab" onclick="switchTab('settings')">⚙️ Configurações</div>
        </div>

        <!-- Dashboard Tab -->
        <div id="dashboard" class="tab-content active">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value" id="active-signals">0</div>
                    <div class="stat-label">Sinais Ativos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="precision">0%</div>
                    <div class="stat-label">Precisão</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="return">+0%</div>
                    <div class="stat-label">Retorno</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="cryptos-count">7</div>
                    <div class="stat-label">Moedas</div>
                </div>
            </div>

            <div class="crypto-grid" id="cryptos-container">
                <!-- Preenchido por JavaScript -->
            </div>
        </div>

        <!-- Alerts Tab -->
        <div id="alerts" class="tab-content">
            <div style="margin-bottom: 20px;">
                <button class="button button-primary" onclick="sendTestAlert()">🧪 Testar Alerta</button>
                <button class="button button-secondary" onclick="sendDailyReport()">📋 Enviar Relatório Diário</button>
            </div>

            <div id="alerts-container" style="max-height: 500px; overflow-y: auto;">
                <!-- Preenchido por JavaScript -->
            </div>
        </div>

        <!-- Settings Tab -->
        <div id="settings" class="tab-content">
            <div style="background: rgba(30, 41, 59, 0.8); border: 1px solid #334155; border-radius: 12px; padding: 20px; max-width: 500px;">
                <h3 style="margin-bottom: 20px; font-size: 18px; font-weight: bold;">Configurações do Telegram</h3>
                
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-size: 14px;">Token do Bot:</label>
                    <input type="password" class="input-field" id="telegram-token" value="7834485201:AAExDXuQJprwbv3ofUIOg5zrliXrDeA0-vU" readonly>
                </div>

                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-size: 14px;">Chat ID:</label>
                    <input type="text" class="input-field" id="telegram-chat-id" value="695440902" readonly>
                </div>

                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-size: 14px;">
                        <input type="checkbox" checked onchange="toggleMonitoring()"> Monitoramento Ativo
                    </label>
                </div>

                <button class="button button-primary" onclick="testTelegramConnection()">🧪 Testar Conexão</button>
            </div>
        </div>
    </div>

    <script>
        let lastUpdate = Date.now();

        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }

        function updateLatency() {
            const now = Date.now();
            const latency = now - lastUpdate;
            document.getElementById('latency').textContent = `● ${latency}ms`;
            lastUpdate = now;
        }

        function updateDashboard() {
            fetch('/api/cryptos')
                .then(r => r.json())
                .then(data => {
                    // Atualizar container de criptomoedas
                    const container = document.getElementById('cryptos-container');
                    container.innerHTML = '';

                    let activeSignals = 0;
                    let totalReturn = 0;

                    data.cryptos.forEach(crypto => {
                        if (crypto.signal) activeSignals++;
                        totalReturn += crypto.change24h;

                        const changeClass = crypto.change24h > 0 ? 'positive' : 'negative';
                        const changeSymbol = crypto.change24h > 0 ? '📈' : '📉';
                        const signalHtml = crypto.signal ? `<div class="signal-badge signal-${crypto.signal === 'COMPRA' ? 'buy' : 'sell'}">${crypto.signal}</div>` : '';

                        const html = `
                            <div class="crypto-card">
                                <div class="crypto-name">${crypto.symbol}</div>
                                <div class="crypto-price">R$ ${crypto.price.toFixed(8)}</div>
                                <div class="crypto-change">
                                    <span class="${changeClass}">${changeSymbol} ${crypto.change24h > 0 ? '+' : ''}${crypto.change24h.toFixed(2)}%</span>
                                </div>
                                <div style="font-size: 12px; color: #94a3b8;">RSI: ${crypto.rsi.toFixed(2)}</div>
                                <div style="font-size: 12px; color: #94a3b8;">Volume: ${(crypto.volume / 1000).toFixed(0)}K</div>
                                ${signalHtml}
                            </div>
                        `;
                        container.innerHTML += html;
                    });

                    // Atualizar estatísticas
                    document.getElementById('active-signals').textContent = activeSignals;
                    document.getElementById('precision').textContent = '92.7%';
                    document.getElementById('return').textContent = `${totalReturn > 0 ? '+' : ''}${(totalReturn / 7).toFixed(2)}%`;

                    updateLatency();
                });
        }

        function updateAlerts() {
            fetch('/api/alerts')
                .then(r => r.json())
                .then(data => {
                    const container = document.getElementById('alerts-container');
                    container.innerHTML = '';

                    if (data.alerts.length === 0) {
                        container.innerHTML = '<div style="color: #94a3b8; text-align: center; padding: 40px;">Nenhum alerta enviado ainda</div>';
                        return;
                    }

                    data.alerts.forEach(alert => {
                        const emoji = alert.signal === 'COMPRA' ? '🟢' : '🔴';
                        const html = `
                            <div class="alert-item">
                                <div style="font-weight: bold; margin-bottom: 5px;">${emoji} ${alert.crypto} - ${alert.signal}</div>
                                <div style="font-size: 12px; color: #94a3b8;">Preço: R$ ${alert.price.toFixed(8)} | RSI: ${alert.rsi.toFixed(2)}</div>
                                <div class="alert-time">${alert.timestamp}</div>
                            </div>
                        `;
                        container.innerHTML += html;
                    });
                });
        }

        function sendTestAlert() {
            fetch('/api/test-alert', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    alert('✓ Alerta de teste enviado para o Telegram!');
                    updateAlerts();
                });
        }

        function sendDailyReport() {
            fetch('/api/daily-report', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    alert('✓ Relatório diário enviado para o Telegram!');
                });
        }

        function testTelegramConnection() {
            fetch('/api/test-telegram', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        alert('✓ Conexão com Telegram funcionando corretamente!');
                    } else {
                        alert('✗ Erro ao conectar com Telegram');
                    }
                });
        }

        function toggleMonitoring() {
            fetch('/api/toggle-monitoring', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    console.log('Monitoramento:', data.monitoring ? 'Ativo' : 'Inativo');
                });
        }

        // Atualizar dados a cada 2 segundos
        setInterval(() => {
            updateDashboard();
            updateAlerts();
        }, 2000);

        // Atualização inicial
        updateDashboard();
        updateAlerts();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/cryptos')
def get_cryptos():
    """Retorna os dados das criptomoedas"""
    cryptos = []
    for symbol, data in cryptos_data.items():
        cryptos.append({
            'symbol': symbol,
            'price': data['price'],
            'change24h': data['change24h'],
            'rsi': data['rsi'],
            'volume': data['volume'],
            'signal': data['signal']
        })
    return jsonify({'cryptos': cryptos})

@app.route('/api/alerts')
def get_alerts():
    """Retorna o histórico de alertas"""
    return jsonify({'alerts': alerts_history[-20:]})  # Últimos 20 alertas

@app.route('/api/test-alert', methods=['POST'])
def test_alert():
    """Envia um alerta de teste"""
    telegram_service.send_alert(
        crypto_symbol="TESTE",
        signal_type="COMPRA",
        price=0.00001234,
        confidence=85.0,
        rsi=25.5,
        volume=1000000
    )
    
    alerts_history.append({
        'timestamp': datetime.now().strftime("%H:%M:%S"),
        'crypto': 'TESTE',
        'signal': 'COMPRA',
        'price': 0.00001234,
        'rsi': 25.5
    })
    
    return jsonify({'success': True})

@app.route('/api/daily-report', methods=['POST'])
def daily_report():
    """Envia um relatório diário"""
    cryptos_for_report = [
        {'symbol': symbol, 'change24h': data['change24h'], 'rsi': data['rsi'], 'signal': data['signal']}
        for symbol, data in cryptos_data.items()
    ]
    telegram_service.send_daily_report(cryptos_for_report)
    return jsonify({'success': True})

@app.route('/api/test-telegram', methods=['POST'])
def test_telegram():
    """Testa a conexão com o Telegram"""
    success = telegram_service.send_test_message()
    return jsonify({'success': success})

@app.route('/api/toggle-monitoring', methods=['POST'])
def toggle_monitoring():
    """Ativa/desativa o monitoramento"""
    global monitoring_active
    monitoring_active = not monitoring_active
    return jsonify({'monitoring': monitoring_active})

if __name__ == '__main__':
    print("=" * 60)
    print("CriptoBR IA PRO - Aplicação com Integração do Telegram")
    print("=" * 60)
    print(f"✓ Telegram Token: {TELEGRAM_TOKEN[:20]}...")
    print(f"✓ Chat ID: {TELEGRAM_CHAT_ID}")
    print(f"✓ Servidor iniciado em: http://localhost:5000" )
    print("=" * 60)
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
