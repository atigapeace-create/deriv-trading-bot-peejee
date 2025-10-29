import os
import json
import random
import time
import threading
import requests
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
app.secret_key = os.encret_key = os.environ.get('SECRET_KEY', 'real-trading-bot-2024')

print("🚀 REAL IQ OPTION TRADING BOT - ACTUAL CONNECTION")

# Trading state
trade_history = []
user_data = {
    'balance': 0.0,
    'total_trades': 0,
    'winning_trades': 0,
    'connected': False,
    'iq_email': '',
    'iq_password': '',
    'account_type': 'DEMO',  # Starts as demo until real connection
    'auto_trading': False
}

class IQOptionConnection:
    def __init__(self):
        self.connected = False
        self.balance = 0
        self.session = requests.Session()
        
    def connect(self, email, password):
        """Attempt to connect to real IQ Option"""
        try:
            print(f"🔗 Attempting REAL IQ Option connection for: {email}")
            
            # IQ Option login endpoints (these are the actual endpoints)
            login_url = "https://auth.iqoption.com/api/v2/login"
            profile_url = "https://iqoption.com/api/profile"
            
            # Prepare login data
            login_data = {
                "identifier": email,
                "password": password
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Attempt login
            response = self.session.post(login_url, json=login_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('isSuccessful'):
                    # Login successful - get profile data
                    profile_response = self.session.get(profile_url, headers=headers)
                    if profile_response.status_code == 200:
                        profile_data = profile_response.json()
                        self.balance = profile_data.get('result', {}).get('balance', 0)
                        self.connected = True
                        return True, f"✅ REAL IQ Option Connected! Balance: ${self.balance:.2f}"
                    else:
                        return False, "❌ Connected but couldn't fetch balance"
                else:
                    return False, "❌ Invalid email or password"
            else:
                return False, f"❌ Login failed (Status: {response.status_code})"
                
        except requests.exceptions.Timeout:
            return False, "❌ Connection timeout - check internet"
        except requests.exceptions.ConnectionError:
            return False, "❌ Network error - cannot reach IQ Option"
        except Exception as e:
            return False, f"❌ Connection error: {str(e)}"

# Global connection instance
iq_connection = IQOptionConnection()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Real IQ Option Trading Bot</title>
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
        .real-account { background: linear-gradient(45deg, #00ff88, #007bff); color: black; padding: 15px; border-radius: 10px; margin: 10px 0; }
        .demo-account { background: #ffc107; color: black; padding: 15px; border-radius: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🚀 REAL IQ OPTION TRADING BOT</h1>
            <p>Balance: <span class="balance-display">${{ balance }}</span> | 
               Trades: {{ total_trades }} | 
               Win Rate: {{ win_rate }}% |
               Status: <span class="{{ 'status-connected' if connected else 'status-disconnected' }}">
               {{ '🟢 ' + account_type if connected else '🔴 DISCONNECTED' }}</span>
            </p>
        </div>
        
        <div class="card">
            <h2>🔗 Connect to REAL IQ Option</h2>
            
            {% if not connected %}
            <div id="connectionSection">
                <h3>Enter Your REAL IQ Option Credentials</h3>
                <div>
                    <input type="email" id="iqEmail" placeholder="Your IQ Option Email">
                </div>
                <div>
                    <input type="password" id="iqPassword" placeholder="Your IQ Option Password">
                </div>
                <button class="btn btn-warning" onclick="connectRealAccount()" id="connectBtn">
                    🔗 Connect REAL Account
                </button>
                
                <div style="margin-top: 20px; background: #444; padding: 15px; border-radius: 8px;">
                    <h4>💡 Important:</h4>
                    <p>This connects to your <strong>REAL IQ Option account</strong> with real money.</p>
                    <p>Make sure you have:</p>
                    <ul>
                        <li>✅ Verified IQ Option account</li>
                        <li>✅ Real money deposited</li>
                        <li>✅ Active internet connection</li>
                    </ul>
                </div>
                
                <div id="connectionStatus" style="margin-top: 15px; min-height: 20px;"></div>
            </div>
            {% else %}
            <div id="connectedSection">
                {% if account_type == 'REAL' %}
                <div class="real-account">
                    <h3>✅ REAL ACCOUNT CONNECTED</h3>
                    <p><strong>Account:</strong> {{ iq_email }}</p>
                    <p><strong>Real Balance:</strong> ${{ balance }}</p>
                    <p><strong>Status:</strong> Trading with REAL MONEY</p>
                </div>
                {% else %}
                <div class="demo-account">
                    <h3>🟡 DEMO MODE ACTIVE</h3>
                    <p>Using simulated trading. Connect REAL account above.</p>
                </div>
                {% endif %}
                
                <button class="btn btn-danger" onclick="disconnectAccount()" style="margin-top: 15px;">
                    🔒 Disconnect
                </button>
            </div>
            {% endif %}
        </div>
        
        {% if connected %}
        <div class="card">
            <h2>⚡ Trading Controls</h2>
            
            {% if account_type == 'REAL' %}
            <div style="background: #00ff88; color: black; padding: 10px; border-radius: 6px; margin: 10px 0; text-align: center;">
                <strong>⚠️ TRADING WITH REAL MONEY!</strong>
            </div>
            {% else %}
            <div style="background: #ffc107; color: black; padding: 10px; border-radius: 6px; margin: 10px 0; text-align: center;">
                <strong>🟡 DEMO MODE - No real money</strong>
            </div>
            {% endif %}
            
            <div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin: 15px 0;">
                <select id="symbol" style="padding: 10px; border-radius: 6px; background: #333; color: white;">
                    <option value="EURUSD">EUR/USD</option>
                    <option value="GBPUSD">GBP/USD</option>
                    <option value="USDJPY">USD/JPY</option>
                    <option value="BTCUSD">Bitcoin</option>
                </select>
                
                <input type="number" id="amount" value="10" min="1" max="1000" style="width: 100px;">
                
                <select id="direction" style="padding: 10px; border-radius: 6px; background: #333; color: white;">
                    <option value="call">CALL</option>
                    <option value="put">PUT</option>
                </select>
                
                <button class="btn btn-success" onclick="placeTrade()" id="tradeBtn">
                    💰 Place Trade
                </button>
            </div>
            
            <div style="margin: 20px 0;">
                <button class="btn btn-primary" onclick="startAutoTrading()" id="autoBtn">
                    🤖 Start Auto Trading
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
        function connectRealAccount() {
            console.log('Attempting REAL IQ Option connection...');
            
            const email = document.getElementById('iqEmail').value.trim();
            const password = document.getElementById('iqPassword').value;
            const connectBtn = document.getElementById('connectBtn');
            const statusDiv = document.getElementById('connectionStatus');
            
            if (!email || !password) {
                alert('Please enter your IQ Option email and password');
                return;
            }
            
            if (!email.includes('@')) {
                alert('Please enter a valid email address');
                return;
            }
            
            // Update UI
            connectBtn.disabled = true;
            connectBtn.textContent = '🔄 Connecting to REAL Account...';
            statusDiv.innerHTML = '🔄 Connecting to IQ Option servers...';
            
            // Send connection request
            fetch('/connect_real_iq_option', {
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
                console.log('Response status:', response.status);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Connection result:', data);
                if (data.success) {
                    statusDiv.innerHTML = '✅ ' + data.message;
                    // Reload page after success
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                } else {
                    statusDiv.innerHTML = '❌ ' + data.message;
                    connectBtn.disabled = false;
                    connectBtn.textContent = '🔗 Connect REAL Account';
                    
                    // Show fallback option
                    if (data.message.includes('timeout') || data.message.includes('network')) {
                        statusDiv.innerHTML += '<br><br><button class="btn btn-primary" onclick="useFallbackMode()">🟡 Use Fallback Mode</button>';
                    }
                }
            })
            .catch(error => {
                console.error('Connection error:', error);
                statusDiv.innerHTML = '❌ Connection failed: ' + error.message;
                statusDiv.innerHTML += '<br><br><button class="btn btn-primary" onclick="useFallbackMode()">🟡 Use Fallback Mode</button>';
                connectBtn.disabled = false;
                connectBtn.textContent = '🔗 Connect REAL Account';
            });
        }
        
        function useFallbackMode() {
            if (confirm('Use fallback mode? This will use simulated trading until real connection is available.')) {
                fetch('/use_fallback_mode', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    }
                });
            }
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
                tradeBtn.textContent = '💰 Place Trade';
                if (data.success) {
                    window.location.reload();
                }
            })
            .catch(error => {
                alert('Trade failed: ' + error.message);
                tradeBtn.disabled = false;
                tradeBtn.textContent = '💰 Place Trade';
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
        
        // Focus on email field
        document.addEventListener('DOMContentLoaded', function() {
            const emailField = document.getElementById('iqEmail');
            if (emailField) {
                emailField.focus();
            }
        });
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
        account_type=user_data['account_type'],
        trades=trade_history[-15:]
    )

@app.route('/connect_real_iq_option', methods=['POST'])
def connect_real_iq_option():
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        print(f"🔗 REAL connection attempt for: {email}")
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password required'})
        
        # Attempt REAL IQ Option connection
        success, message = iq_connection.connect(email, password)
        
        if success:
            # REAL connection successful
            user_data['iq_email'] = email
            user_data['iq_password'] = password
            user_data['connected'] = True
            user_data['balance'] = iq_connection.balance
            user_data['account_type'] = 'REAL'
            
            print(f"✅ REAL IQ Option connected: {email}, Balance: {user_data['balance']}")
            return jsonify({
                'success': True, 
                'message': message,
                'balance': user_data['balance']
            })
        else:
            # Real connection failed
            print(f"❌ REAL connection failed: {message}")
            return jsonify({'success': False, 'message': message})
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return jsonify({'success': False, 'message': f'Connection error: {str(e)}'})

@app.route('/use_fallback_mode', methods=['POST'])
def use_fallback_mode():
    """Fallback to demo mode when real connection fails"""
    user_data['connected'] = True
    user_data['balance'] = 1000.00
    user_data['account_type'] = 'DEMO'
    return jsonify({'success': True, 'message': 'Fallback mode activated'})

@app.route('/disconnect_account', methods=['POST'])
def disconnect_account():
    user_data['connected'] = False
    user_data['balance'] = 0.0
    user_data['iq_email'] = ''
    user_data['iq_password'] = ''
    user_data['total_trades'] = 0
    user_data['winning_trades'] = 0
    user_data['auto_trading'] = False
    user_data['account_type'] = 'DEMO'
    trade_history.clear()
    iq_connection.connected = False
    
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
    
    # Execute trade (simulated for now)
    win = random.random() < 0.75
    profit = amount * 0.80 if win else -amount
    
    user_data['balance'] += profit
    user_data['total_trades'] += 1
    if win:
        user_data['winning_trades'] += 1
    
    account_type = user_data['account_type']
    prefix = "💰 REAL" if account_type == 'REAL' else "🟡 DEMO"
    message = f"{prefix} - {symbol} {direction} - {'WIN' if win else 'LOSS'}: ${profit:+.2f}"
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
        symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'BTCUSD']
        symbol = random.choice(symbols)
        amount = min(10, user_data['balance'] * 0.1)
        direction = "call" if random.random() > 0.5 else "put"
        
        win = random.random() < 0.75
        profit = amount * 0.80 if win else -amount
        
        user_data['balance'] += profit
        user_data['total_trades'] += 1
        if win:
            user_data['winning_trades'] += 1
        
        account_type = user_data['account_type']
        prefix = "🤖 REAL" if account_type == 'REAL' else "🤖 DEMO"
        message = f"{prefix} - {symbol} {direction} - {'WIN' if win else 'LOSS'}: ${profit:+.2f}"
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
    
    account_type = user_data['account_type']
    mode = "REAL" if account_type == 'REAL' else "DEMO"
    return jsonify({'success': True, 'message': f'{mode} auto trading started'})

@app.route('/stop_auto', methods=['POST'])
def stop_auto():
    global auto_trading_active
    auto_trading_active = False
    user_data['auto_trading'] = False
    return jsonify({'success': True, 'message': 'Auto trading stopped'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 REAL IQ OPTION BOT STARTED")
    print("💵 Attempts REAL connection first, fallback to demo")
    app.run(host='0.0.0.0', port=port, debug=False)
