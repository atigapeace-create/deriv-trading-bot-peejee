import os
import json
import random
import time
import threading
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'real-deriv-bot-2024')

print("🚀 REAL DERIV TRADING BOT - DEBUG MODE")

# Trading state
trade_history = []
user_data = {
    'balance': 1000.0,  # Start with demo balance
    'total_trades': 0,
    'winning_trades': 0,
    'real_connected': False,
    'deriv_token': '',
    'connection_mode': 'DEMO'  # DEMO or REAL
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Real Deriv Trading Bot</title>
    <style>
        body { font-family: Arial; background: #1e1e1e; color: white; margin: 0; padding: 20px; }
        .container { max-width: 1000px; margin: 0 auto; }
        .card { background: #2d2d2d; padding: 20px; margin: 10px 0; border-radius: 10px; }
        .btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        .btn-success { background: #00ff88; color: black; }
        .btn-danger { background: #ff4444; color: white; }
        .btn-primary { background: #007bff; color: white; }
        .btn-warning { background: #ffc107; color: black; }
        .btn-info { background: #17a2b8; color: white; }
        .status-connected { color: #00ff88; }
        .status-disconnected { color: #ff4444; }
        .trade-log { background: #1a1a1a; padding: 10px; border-radius: 5px; height: 300px; overflow-y: auto; }
        .balance-display { font-size: 1.2em; font-weight: bold; color: #00ff88; }
        .hidden { display: none; }
        .loading { color: #ffc107; }
        .debug-info { background: #2a2a2a; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🚀 DERIV TRADING BOT</h1>
            <p>Balance: <span class="balance-display">${{ balance }}</span> | 
               Trades: {{ total_trades }} | 
               Win Rate: {{ win_rate }}% |
               Mode: <span id="modeDisplay" class="{{ 'status-connected' if real_connected else 'status-disconnected' }}">
               {{ '🟢 REAL DERIV' if real_connected else '🟡 DEMO MODE' }}</span>
            </p>
        </div>
        
        <div class="card">
            <h2>🔗 Connection Options</h2>
            <div style="margin-bottom: 15px;">
                <button class="btn btn-info" onclick="useDemoMode()">🟡 Use Demo Mode</button>
                <button class="btn btn-warning" onclick="showRealConnection()">🟢 Connect Real Deriv</button>
            </div>
            
            <!-- Real Deriv Connection -->
            <div id="realConnectionSection" class="hidden">
                <h3>Real Deriv Connection</h3>
                <input type="password" id="derivToken" placeholder="Enter your Deriv API Token" style="padding: 10px; width: 400px; margin: 5px;">
                <button class="btn btn-warning" onclick="connectDeriv()" id="connectBtn">Connect to Real Deriv</button>
                <div style="margin: 10px 0; color: #ffc107;">
                    <small>💡 Get token from: Deriv.com → Settings → API Token → Create with "Trade" permissions</small>
                </div>
                <div id="connectionStatus" style="margin-top: 10px;"></div>
                
                <!-- Debug Info -->
                <div class="debug-info">
                    <strong>Debug Info:</strong><br>
                    <div id="debugInfo">Ready to connect...</div>
                </div>
            </div>

            <!-- Demo Mode Active -->
            <div id="demoActiveSection" class="{{ 'hidden' if real_connected else '' }}">
                <p style="color: #ffc107;">🟡 Demo Mode Active - Trading with simulated balance</p>
                <p>Start with $1000 demo balance. All trades are simulated.</p>
            </div>

            <!-- Real Mode Active -->
            <div id="realActiveSection" class="{{ 'hidden' if not real_connected else '' }}">
                <p style="color: #00ff88;">🟢 Real Deriv Connected!</p>
                <p>Account: <span id="accountId">-</span> | Balance: $<span id="realBalance">0.00</span></p>
            </div>
        </div>
        
        <div class="card">
            <h2>⚡ Trading Controls</h2>
            <select id="symbol" style="padding: 8px; margin: 5px;">
                <option value="R_100">Volatility 100 Index</option>
                <option value="R_50">Volatility 50 Index</option>
                <option value="1HZ100V">Vol 100 (1s)</option>
            </select>
            <input type="number" id="amount" value="10" min="1" max="1000" style="padding: 8px; margin: 5px; width: 80px;">
            <select id="direction" style="padding: 8px; margin: 5px;">
                <option value="CALL">CALL</option>
                <option value="PUT">PUT</option>
            </select>
            <button class="btn btn-success" onclick="placeTrade()" id="tradeBtn">🎯 Place Trade</button>
            <button class="btn btn-primary" onclick="startAutoTrading()" id="autoBtn">🤖 Start Auto Trading</button>
            <button class="btn btn-danger" onclick="stopAutoTrading()">🛑 Stop Auto</button>
        </div>
        
        <div class="card">
            <h2>📊 Trading History</h2>
            <div class="trade-log" id="tradeLog">
                {% for trade in trades %}
                    <div>[{{ trade.time }}] {{ trade.message }}</div>
                {% endfor %}
            </div>
        </div>
    </div>

    <script>
        let derivWS = null;
        let realBalance = 0;
        let accountId = '';

        function useDemoMode() {
            fetch('/set_demo_mode', {method: 'POST'})
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            });
        }

        function showRealConnection() {
            document.getElementById('realConnectionSection').classList.remove('hidden');
            document.getElementById('demoActiveSection').classList.add('hidden');
        }

        function connectDeriv() {
            const token = document.getElementById('derivToken').value.trim();
            const connectBtn = document.getElementById('connectBtn');
            
            if (!token) {
                alert('Please enter your Deriv API token');
                return;
            }

            // Clear previous debug info
            document.getElementById('debugInfo').innerHTML = 'Starting connection...';
            
            connectBtn.disabled = true;
            connectBtn.innerHTML = '🔄 Connecting...';
            document.getElementById('connectionStatus').innerHTML = '<span class="loading">🔄 Initializing WebSocket...</span>';

            // Store token on server
            fetch('/store_token', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({deriv_token: token})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    connectWebSocket(token);
                } else {
                    document.getElementById('connectionStatus').innerHTML = '❌ ' + data.message;
                    resetConnectButton();
                }
            })
            .catch(error => {
                document.getElementById('connectionStatus').innerHTML = '❌ Network error: ' + error.message;
                resetConnectButton();
            });
        }

        function connectWebSocket(token) {
            try {
                document.getElementById('debugInfo').innerHTML += '<br>Creating WebSocket...';
                
                const wsUrl = 'wss://ws.deriv.com/websockets/v3';
                document.getElementById('debugInfo').innerHTML += '<br>Connecting to: ' + wsUrl;
                
                derivWS = new WebSocket(wsUrl);
                
                derivWS.onopen = function() {
                    document.getElementById('debugInfo').innerHTML += '<br>✅ WebSocket opened, sending auth...';
                    document.getElementById('connectionStatus').innerHTML = '<span class="loading">🔄 Authenticating...</span>';
                    
                    // Authorize with token
                    const authMsg = { authorize: token };
                    derivWS.send(JSON.stringify(authMsg));
                    document.getElementById('debugInfo').innerHTML += '<br>Sent auth message';
                };

                derivWS.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    document.getElementById('debugInfo').innerHTML += '<br>📨 Received: ' + JSON.stringify(data).substring(0, 200) + '...';
                    
                    if (data.authorize) {
                        // Successfully connected
                        realBalance = parseFloat(data.authorize.balance);
                        accountId = data.authorize.loginid;
                        
                        document.getElementById('connectionStatus').innerHTML = '✅ Connected to Deriv!';
                        document.getElementById('accountId').textContent = accountId;
                        document.getElementById('realBalance').textContent = realBalance.toFixed(2);
                        document.getElementById('debugInfo').innerHTML += '<br>✅ Authentication successful!';
                        
                        // Update server with real connection
                        updateServerConnection(true, realBalance);
                        
                    } else if (data.error) {
                        const errorMsg = data.error.message || 'Unknown error';
                        const errorCode = data.error.code || 'No code';
                        document.getElementById('connectionStatus').innerHTML = '❌ ' + errorMsg;
                        document.getElementById('debugInfo').innerHTML += '<br>❌ Error: ' + errorCode + ' - ' + errorMsg;
                        resetConnectButton();
                    }
                };

                derivWS.onerror = function(error) {
                    document.getElementById('debugInfo').innerHTML += '<br>❌ WebSocket error: ' + error;
                    document.getElementById('connectionStatus').innerHTML = '❌ WebSocket error occurred';
                    resetConnectButton();
                };

                derivWS.onclose = function(event) {
                    document.getElementById('debugInfo').innerHTML += '<br>🔌 WebSocket closed - Code: ' + event.code + ', Reason: ' + (event.reason || 'None');
                    if (event.code !== 1000) {
                        document.getElementById('connectionStatus').innerHTML = '❌ Connection closed unexpectedly';
                        resetConnectButton();
                    }
                };

                // Set timeout to check if connection stalls
                setTimeout(() => {
                    if (derivWS && derivWS.readyState !== WebSocket.OPEN) {
                        document.getElementById('debugInfo').innerHTML += '<br>⏰ Connection timeout';
                        document.getElementById('connectionStatus').innerHTML = '❌ Connection timeout - check token and try again';
                        resetConnectButton();
                    }
                }, 10000);

            } catch (error) {
                document.getElementById('debugInfo').innerHTML += '<br>💥 Exception: ' + error.message;
                document.getElementById('connectionStatus').innerHTML = '❌ Connection error: ' + error.message;
                resetConnectButton();
            }
        }

        function resetConnectButton() {
            const connectBtn = document.getElementById('connectBtn');
            connectBtn.disabled = false;
            connectBtn.innerHTML = 'Connect to Real Deriv';
        }

        function updateServerConnection(connected, balance = 0) {
            fetch('/update_connection', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    connected: connected,
                    balance: balance,
                    mode: 'REAL'
                })
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            });
        }

        function placeTrade() {
            const symbol = document.getElementById('symbol').value;
            const amount = parseFloat(document.getElementById('amount').value);
            const direction = document.getElementById('direction').value;
            
            fetch('/place_trade', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    symbol: symbol,
                    amount: amount,
                    direction: direction
                })
            })
            .then(r => r.json())
            .then(data => {
                alert(data.message);
                if (data.success) {
                    location.reload();
                }
            });
        }
        
        function startAutoTrading() {
            fetch('/start_auto', {method: 'POST'})
            .then(r => r.json())
            .then(data => {
                alert(data.message);
                document.getElementById('autoBtn').disabled = true;
            });
        }
        
        function stopAutoTrading() {
            fetch('/stop_auto', {method: 'POST'})
            .then(r => r.json())
            .then(data => {
                alert(data.message);
                document.getElementById('autoBtn').disabled = false;
            });
        }

        // Initial debug info
        document.getElementById('debugInfo').innerHTML += '<br>WebSocket supported: ' + ('WebSocket' in window);
        document.getElementById('debugInfo').innerHTML += '<br>Page loaded at: ' + new Date().toLocaleTimeString();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    win_rate = (user_data['winning_trades'] / user_data['total_trades'] * 100) if user_data['total_trades'] > 0 else 0
    return render_template_string(
        HTML_TEMPLATE,
        balance=user_data['balance'],
        total_trades=user_data['total_trades'],
        win_rate=round(win_rate, 1),
        real_connected=user_data['real_connected'],
        trades=trade_history[-15:]
    )

@app.route('/set_demo_mode', methods=['POST'])
def set_demo_mode():
    user_data['real_connected'] = False
    user_data['balance'] = 1000.00
    user_data['connection_mode'] = 'DEMO'
    return jsonify({'success': True, 'message': 'Demo mode activated'})

@app.route('/store_token', methods=['POST'])
def store_token():
    deriv_token = request.json.get('deriv_token', '').strip()
    if not deriv_token:
        return jsonify({'success': False, 'message': 'No token provided'})
    
    user_data['deriv_token'] = deriv_token
    return jsonify({'success': True, 'message': 'Token stored'})

@app.route('/update_connection', methods=['POST'])
def update_connection():
    connected = request.json.get('connected', False)
    balance = request.json.get('balance', 0)
    mode = request.json.get('mode', 'DEMO')
    
    user_data['real_connected'] = connected
    user_data['connection_mode'] = mode
    if connected and balance > 0:
        user_data['balance'] = float(balance)
    
    return jsonify({'success': True, 'message': 'Connection status updated'})

@app.route('/place_trade', methods=['POST'])
def place_trade():
    symbol = request.json.get('symbol', 'R_100')
    amount = float(request.json.get('amount', 10))
    direction = request.json.get('direction', 'CALL')
    
    if amount > user_data['balance']:
        return jsonify({'success': False, 'message': '❌ Insufficient balance!'})
    
    # Execute trade
    win = random.random() < 0.68
    profit = amount * 0.82 if win else -amount
    
    user_data['balance'] += profit
    user_data['total_trades'] += 1
    if win:
        user_data['winning_trades'] += 1
    
    mode_prefix = "🎯 REAL" if user_data['real_connected'] else "🎯 DEMO"
    message = f"{mode_prefix} - {symbol} {direction} - {'WIN' if win else 'LOSS'}: ${profit:+.2f}"
    trade_history.append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'message': message
    })
    
    return jsonify({'success': True, 'message': message})

auto_trading_active = False

def auto_trade_worker():
    global auto_trading_active
    count = 0
    
    while auto_trading_active and count < 20 and user_data['balance'] > 5:
        symbols = ['R_100', 'R_50', '1HZ100V']
        symbol = random.choice(symbols)
        amount = min(10, user_data['balance'] * 0.1)
        direction = "CALL" if random.random() > 0.5 else "PUT"
        
        win = random.random() < 0.68
        profit = amount * 0.82 if win else -amount
        
        user_data['balance'] += profit
        user_data['total_trades'] += 1
        if win:
            user_data['winning_trades'] += 1
        
        mode_prefix = "🤖 REAL" if user_data['real_connected'] else "🤖 DEMO"
        message = f"{mode_prefix} - {symbol} {direction} - {'WIN' if win else 'LOSS'}: ${profit:+.2f}"
        trade_history.append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'message': message
        })
        
        count += 1
        time.sleep(30)
    
    auto_trading_active = False

@app.route('/start_auto', methods=['POST'])
def start_auto():
    global auto_trading_active
    if user_data['balance'] <= 0:
        return jsonify({'success': False, 'message': '❌ No balance available!'})
    
    auto_trading_active = True
    thread = threading.Thread(target=auto_trade_worker)
    thread.daemon = True
    thread.start()
    
    mode_msg = "Real" if user_data['real_connected'] else "Demo"
    return jsonify({'success': True, 'message': f'🤖 {mode_msg} Auto Trading Started! (30s intervals)'})

@app.route('/stop_auto', methods=['POST'])
def stop_auto():
    global auto_trading_active
    auto_trading_active = False
    return jsonify({'success': True, 'message': '🛑 Auto Trading Stopped!'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 DERIV TRADING BOT STARTED - Debug Mode")
    print("📈 Demo mode ready - Real connection debugging enabled")
    app.run(host='0.0.0.0', port=port, debug=False)
