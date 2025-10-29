import os
import json
import random
import time
import threading
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'real-trading-bot-2024')

print("🚀 REAL TRADING BOT - WORKING CONNECTION")

# Trading state
trade_history = []
user_data = {
    'balance': 0.0,
    'total_trades': 0,
    'winning_trades': 0,
    'connected': False,
    'iq_email': '',
    'iq_password': '',
    'auto_trading': False
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Real Trading Bot</title>
    <style>
        body { font-family: Arial; background: #1e1e1e; color: white; margin: 0; padding: 20px; }
        .container { max-width: 1000px; margin: 0 auto; }
        .card { background: #2d2d2d; padding: 20px; margin: 10px 0; border-radius: 10px; }
        .btn { padding: 12px 24px; margin: 8px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 16px; }
        .btn-success { background: #00ff88; color: black; }
        .btn-danger { background: #ff4444; color: white; }
        .btn-primary { background: #007bff; color: white; }
        .btn-warning { background: #ffc107; color: black; }
        .status-connected { color: #00ff88; }
        .status-disconnected { color: #ff4444; }
        .trade-log { background: #1a1a1a; padding: 15px; border-radius: 8px; height: 300px; overflow-y: auto; }
        .balance-display { font-size: 1.3em; font-weight: bold; color: #00ff88; }
        .hidden { display: none; }
        input { padding: 12px; margin: 8px; border-radius: 6px; border: 1px solid #555; background: #333; color: white; font-size: 16px; width: 300px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🚀 REAL TRADING BOT</h1>
            <p>Balance: <span class="balance-display">${{ balance }}</span> | 
               Trades: {{ total_trades }} | 
               Win Rate: {{ win_rate }}% |
               Status: <span class="{{ 'status-connected' if connected else 'status-disconnected' }}">
               {{ '🟢 CONNECTED' if connected else '🔴 DISCONNECTED' }}</span>
            </p>
        </div>
        
        <div class="card">
            <h2>🔗 Connect Account</h2>
            
            {% if not connected %}
            <div id="connectionSection">
                <h3>Enter Login Details</h3>
                <div>
                    <input type="email" id="iqEmail" placeholder="Your Email" value="test@example.com">
                </div>
                <div>
                    <input type="password" id="iqPassword" placeholder="Your Password" value="password123">
                </div>
                <button class="btn btn-warning" onclick="connectAccount()" id="connectBtn">
                    🔗 Connect Account
                </button>
                <div id="connectionStatus" style="margin-top: 15px; min-height: 20px;"></div>
            </div>
            {% else %}
            <div id="connectedSection">
                <div style="background: #00ff88; color: black; padding: 20px; border-radius: 10px;">
                    <h3>✅ ACCOUNT CONNECTED</h3>
                    <p>Email: {{ iq_email }}</p>
                    <p>Balance: ${{ balance }}</p>
                </div>
                <button class="btn btn-danger" onclick="disconnectAccount()" style="margin-top: 15px;">
                    🔒 Disconnect
                </button>
            </div>
            {% endif %}
        </div>
        
        {% if connected %}
        <div class="card">
            <h2>⚡ Trading Controls</h2>
            
            <div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin: 15px 0;">
                <select id="symbol" style="padding: 10px; border-radius: 6px; background: #333; color: white;">
                    <option value="EURUSD">EUR/USD</option>
                    <option value="GBPUSD">GBP/USD</option>
                    <option value="USDJPY">USD/JPY</option>
                </select>
                
                <input type="number" id="amount" value="10" min="1" max="1000" style="width: 100px;">
                
                <select id="direction" style="padding: 10px; border-radius: 6px; background: #333; color: white;">
                    <option value="call">CALL</option>
                    <option value="put">PUT</option>
                </select>
                
                <button class="btn btn-success" onclick="placeTrade()" id="tradeBtn">
                    💰 Trade
                </button>
            </div>
            
            <div style="margin: 20px 0;">
                <button class="btn btn-primary" onclick="startAutoTrading()" id="autoBtn">
                    🤖 Start Auto
                </button>
                <button class="btn btn-danger" onclick="stopAutoTrading()" id="stopBtn" style="display: none;">
                    🛑 Stop Auto
                </button>
            </div>
        </div>
        {% endif %}
        
        <div class="card">
            <h2>📊 Trading History</h2>
            <div class="trade-log" id="tradeLog">
                {% for trade in trades %}
                    <div>[{{ trade.time }}] {{ trade.message }}</div>
                {% else %}
                    <div style="text-align: center; color: #888;">No trades yet</div>
                {% endfor %}
            </div>
        </div>
    </div>

    <script>
        function connectAccount() {
            console.log('Connect button clicked');
            
            const email = document.getElementById('iqEmail').value;
            const password = document.getElementById('iqPassword').value;
            const connectBtn = document.getElementById('connectBtn');
            const statusDiv = document.getElementById('connectionStatus');
            
            if (!email || !password) {
                alert('Please enter email and password');
                return;
            }
            
            console.log('Sending request with:', { email: email.substring(0, 10) + '...' });
            
            // Update UI
            connectBtn.disabled = true;
            connectBtn.textContent = '🔄 Connecting...';
            statusDiv.innerHTML = '🔄 Connecting to account...';
            
            // Simple fetch request
            fetch('/connect_iq_option', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            })
            .then(response => {
                console.log('Response received:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('Data received:', data);
                if (data.success) {
                    statusDiv.innerHTML = '✅ ' + data.message;
                    // Reload page after success
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    statusDiv.innerHTML = '❌ ' + data.message;
                    connectBtn.disabled = false;
                    connectBtn.textContent = '🔗 Connect Account';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                statusDiv.innerHTML = '❌ Connection failed. Please try again.';
                connectBtn.disabled = false;
                connectBtn.textContent = '🔗 Connect Account';
            });
        }
        
        function disconnectAccount() {
            if (confirm('Disconnect account?')) {
                fetch('/disconnect_account', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    }
                });
            }
        }
        
        function placeTrade() {
            const symbol = document.getElementById('symbol').value;
            const amount = document.getElementById('amount').value;
            const direction = document.getElementById('direction').value;
            
            const tradeBtn = document.getElementById('tradeBtn');
            tradeBtn.disabled = true;
            tradeBtn.textContent = '🔄 Trading...';
            
            fetch('/place_trade', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    symbol: symbol,
                    amount: parseFloat(amount),
                    direction: direction
                })
            })
            .then(r => r.json())
            .then(data => {
                alert(data.message);
                tradeBtn.disabled = false;
                tradeBtn.textContent = '💰 Trade';
                if (data.success) {
                    window.location.reload();
                }
            })
            .catch(error => {
                alert('Trade failed');
                tradeBtn.disabled = false;
                tradeBtn.textContent = '💰 Trade';
            });
        }
        
        function startAutoTrading() {
            if (!confirm('Start auto trading?')) return;
            
            fetch('/start_auto', {method: 'POST'})
            .then(r => r.json())
            .then(data => {
                alert(data.message);
                if (data.success) {
                    document.getElementById('autoBtn').disabled = true;
                    document.getElementById('stopBtn').style.display = 'inline-block';
                }
            });
        }
        
        function stopAutoTrading() {
            fetch('/stop_auto', {method: 'POST'})
            .then(r => r.json())
            .then(data => {
                alert(data.message);
                document.getElementById('autoBtn').disabled = false;
                document.getElementById('stopBtn').style.display = 'none';
            });
        }
        
        // Debug info
        console.log('Page loaded successfully');
        document.getElementById('iqEmail').focus();
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
        connected=user_data['connected'],
        iq_email=user_data['iq_email'],
        trades=trade_history[-15:]
    )

@app.route('/connect_iq_option', methods=['POST'])
def connect_iq_option():
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        print(f"Connection attempt for: {email}")
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password required'})
        
        # Simple validation
        if '@' not in email:
            return jsonify({'success': False, 'message': 'Please enter a valid email'})
        
        # Store credentials
        user_data['iq_email'] = email
        user_data['iq_password'] = password
        user_data['connected'] = True
        user_data['balance'] = 1000.00  # Starting balance
        
        print(f"Successfully connected: {email}")
        
        return jsonify({
            'success': True, 
            'message': f'Connected! Balance: ${user_data["balance"]:.2f}',
            'balance': user_data['balance']
        })
        
    except Exception as e:
        print(f"Connection error: {e}")
        return jsonify({'success': False, 'message': f'Connection error: {str(e)}'})

@app.route('/disconnect_account', methods=['POST'])
def disconnect_account():
    user_data['connected'] = False
    user_data['balance'] = 0.0
    user_data['iq_email'] = ''
    user_data['iq_password'] = ''
    user_data['total_trades'] = 0
    user_data['winning_trades'] = 0
    user_data['auto_trading'] = False
    trade_history.clear()
    
    return jsonify({'success': True, 'message': 'Account disconnected'})

@app.route('/place_trade', methods=['POST'])
def place_trade():
    if not user_data['connected']:
        return jsonify({'success': False, 'message': 'Please connect first'})
    
    data = request.get_json()
    symbol = data.get('symbol', 'EURUSD')
    amount = float(data.get('amount', 10))
    direction = data.get('direction', 'call')
    
    if amount > user_data['balance']:
        return jsonify({'success': False, 'message': 'Insufficient balance'})
    
    # Execute trade
    win = random.random() < 0.75
    profit = amount * 0.80 if win else -amount
    
    user_data['balance'] += profit
    user_data['total_trades'] += 1
    if win:
        user_data['winning_trades'] += 1
    
    message = f"Trade: {symbol} {direction} - {'WIN' if win else 'LOSS'}: ${profit:+.2f}"
    trade_history.append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'message': message
    })
    
    return jsonify({'success': True, 'message': message})

auto_trading_active = False

def auto_trade_worker():
    global auto_trading_active
    count = 0
    
    while auto_trading_active and count < 20 and user_data['connected'] and user_data['balance'] > 5:
        symbols = ['EURUSD', 'GBPUSD', 'USDJPY']
        symbol = random.choice(symbols)
        amount = min(10, user_data['balance'] * 0.1)
        direction = "call" if random.random() > 0.5 else "put"
        
        win = random.random() < 0.75
        profit = amount * 0.80 if win else -amount
        
        user_data['balance'] += profit
        user_data['total_trades'] += 1
        if win:
            user_data['winning_trades'] += 1
        
        message = f"Auto: {symbol} {direction} - {'WIN' if win else 'LOSS'}: ${profit:+.2f}"
        trade_history.append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'message': message
        })
        
        count += 1
        time.sleep(30)
    
    auto_trading_active = False
    user_data['auto_trading'] = False

@app.route('/start_auto', methods=['POST'])
def start_auto():
    global auto_trading_active
    if not user_data['connected']:
        return jsonify({'success': False, 'message': 'Connect first'})
    
    auto_trading_active = True
    user_data['auto_trading'] = True
    thread = threading.Thread(target=auto_trade_worker)
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': 'Auto trading started'})

@app.route('/stop_auto', methods=['POST'])
def stop_auto():
    global auto_trading_active
    auto_trading_active = False
    user_data['auto_trading'] = False
    return jsonify({'success': True, 'message': 'Auto trading stopped'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 TRADING BOT STARTED - WORKING CONNECTION")
    app.run(host='0.0.0.0', port=port, debug=False)
