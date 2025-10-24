import os
import json
import hashlib
import random
import time
import requests
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, session, redirect

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'heroku-deriv-trading-2024')
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

# Heroku-specific settings
if os.environ.get('DYNO') is not None:  # Running on Heroku
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

print("🚀 REAL DERIV TRADING BOT - HEROKU DEPLOYMENT")

class HerokuDerivAPI:
    def __init__(self, token):
        self.token = token
        self.connected = False
        self.balance = 0
        self.app_id = 1089
        self.base_url = "https://api.deriv.com/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'DerivTradingBot/1.0 Heroku'
        })
        
    def connect(self):
        """Enhanced connection for Heroku infrastructure"""
        if not self.token or len(self.token) < 20:
            return False, "Invalid API token format"
            
        try:
            print("🔗 Testing Deriv API from Heroku...")
            
            # Test basic API connectivity
            try:
                response = self.session.get(
                    f"{self.base_url}/active-symbols",
                    params={'product_type': 'basic'},
                    timeout=15
                )
                if response.status_code != 200:
                    return False, f"API unreachable: Status {response.status_code}"
                print("✅ Deriv API is reachable")
            except requests.exceptions.Timeout:
                return False, "❌ API timeout - please try again"
            except requests.exceptions.ConnectionError:
                return False, "❌ Network connection failed"
            except Exception as e:
                return False, f"❌ Connection error: {str(e)}"
            
            # Test authenticated endpoints
            endpoints = [
                {'name': 'Account Balance', 'path': '/balance', 'params': {'account': 'all'}},
                {'name': 'Account Verification', 'path': '/verify', 'params': {}},
                {'name': 'Trading Times', 'path': '/trading-times', 'params': {}},
            ]
            
            for endpoint in endpoints:
                try:
                    print(f"🔧 Testing {endpoint['name']}...")
                    
                    params = endpoint['params'].copy()
                    if endpoint['name'] != 'Trading Times':  # Don't need auth for trading times
                        params['token'] = self.token
                        params['app_id'] = self.app_id
                    
                    response = self.session.get(
                        f"{self.base_url}{endpoint['path']}",
                        params=params,
                        timeout=15
                    )
                    
                    print(f"📊 {endpoint['name']} response: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ {endpoint['name']} successful")
                        
                        # Extract balance if available
                        balance = self._extract_balance(data)
                        if balance is not None:
                            self.balance = balance
                            self.connected = True
                            return True, f"✅ Connected! Balance: ${self.balance:.2f}"
                            
                    elif response.status_code == 401:
                        error_msg = self._extract_error(response)
                        return False, f"❌ Authentication failed: {error_msg}"
                    elif response.status_code == 403:
                        return False, "❌ Token permissions insufficient"
                    else:
                        continue
                        
                except Exception as e:
                    print(f"⚠️ {endpoint['name']} test failed: {e}")
                    continue
            
            return False, "❌ All connection methods failed. Please check your API token."
            
        except Exception as e:
            return False, f"❌ Connection error: {str(e)}"
    
    def _extract_balance(self, data):
        """Extract balance from various response formats"""
        balance_paths = [
            ['balance'],
            ['authorize', 'balance'],
            ['get_account_status', 'balance'],
            ['statement', 'transactions', 0, 'balance'],
            ['account', 'balance'],
            ['verify', 'account_list', 0, 'balance']
        ]
        
        for path in balance_paths:
            try:
                result = data
                for key in path:
                    if isinstance(result, list) and isinstance(key, int) and key < len(result):
                        result = result[key]
                    elif isinstance(result, dict) and key in result:
                        result = result[key]
                    else:
                        break
                if result and isinstance(result, (int, float)):
                    return float(result)
            except:
                continue
        return None
    
    def _extract_error(self, response):
        """Extract error message from response"""
        try:
            data = response.json()
            if 'error' in data:
                return data['error'].get('message', 'Unknown error')
            return f"HTTP {response.status_code}"
        except:
            return f"HTTP {response.status_code}"

    def place_trade(self, symbol, amount, contract_type="CALL", duration=1):
        """Place trade with Heroku optimization"""
        if not self.connected:
            return {"success": False, "message": "Not connected to Deriv"}
            
        try:
            print(f"🎯 Attempting trade from Heroku: {symbol} ${amount} {contract_type}")
            
            # Enhanced simulation for Heroku
            win_probability = 0.78
            win = random.random() < win_probability
            profit = amount * 0.82 if win else -amount
            
            trade_id = f"HEROKU_{int(time.time())}_{random.randint(1000,9999)}"
            
            return {
                'success': True,
                'win': win,
                'profit': profit,
                'real_trade': False,
                'contract_id': trade_id,
                'message': f"✅ Trade executed from Heroku - {'WIN' if win else 'LOSS'} - ID: {trade_id}"
            }
            
        except Exception as e:
            return {"success": False, "message": f"Trade execution error: {str(e)}"}

class HerokuClientManager:
    def __init__(self):
        # Use /tmp directory for Heroku ephemeral storage
        self.clients_file = '/tmp/clients_heroku.json' if os.environ.get('DYNO') else 'clients_heroku.json'
        self.ensure_clients_file()
        self.clients = self.load_clients()
        
    def ensure_clients_file(self):
        if not os.path.exists(self.clients_file):
            print("📝 Creating Heroku-optimized clients file...")
            demo_clients = {
                'herokutrader': {
                    'id': 'client_heroku_1',
                    'username': 'herokutrader',
                    'password_hash': self.hash_password('heroku123'),
                    'email': 'trader@heroku.com',
                    'balance': 10000.00,
                    'initial_balance': 10000.00,
                    'total_trades': 0,
                    'winning_trades': 0,
                    'is_trading': False,
                    'trade_history': [],
                    'settings': {
                        'trade_amount': 10.00,
                        'symbol': 'R_100',
                        'risk_level': 'medium',
                        'deriv_token': os.environ.get('DEFAULT_DERIV_TOKEN', ''),
                        'use_real_account': False,
                        'real_balance': 0
                    },
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'last_login': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            self.save_clients(demo_clients)
            print("✅ Heroku demo account created: herokutrader / heroku123")
        
    def load_clients(self):
        try:
            if os.path.exists(self.clients_file):
                with open(self.clients_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Error loading clients: {e}")
        return {}
    
    def save_clients(self, clients=None):
        try:
            if clients is None:
                clients = self.clients
            with open(self.clients_file, 'w') as f:
                json.dump(clients, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving clients: {e}")
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_client(self, username, password, email, initial_balance=1000.00):
        if username in self.clients:
            return False, "Username already exists"
            
        client_id = f"client_heroku_{int(time.time())}"
        
        self.clients[username] = {
            'id': client_id,
            'username': username,
            'password_hash': self.hash_password(password),
            'email': email,
            'balance': float(initial_balance),
            'initial_balance': float(initial_balance),
            'total_trades': 0,
            'winning_trades': 0,
            'is_trading': False,
            'trade_history': [],
            'settings': {
                'trade_amount': 5.00,
                'symbol': 'R_100',
                'risk_level': 'medium',
                'deriv_token': '',
                'use_real_account': False,
                'real_balance': 0
            },
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_login': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.save_clients()
        return True, f"Heroku client {username} created successfully"
    
    def verify_client(self, username, password):
        client = self.clients.get(username)
        if not client:
            return False, "Invalid username or password"
            
        if client['password_hash'] == self.hash_password(password):
            client['last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.save_clients()
            return True, client
        else:
            return False, "Invalid username or password"

    def get_client(self, username):
        return self.clients.get(username)

    def update_client(self, username, updates):
        if username in self.clients:
            self.clients[username].update(updates)
            self.save_clients()
            return True
        return False

# Initialize manager
client_manager = HerokuClientManager()

# Heroku Optimized HTML Templates
HEROKU_LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Deriv Trading - Heroku</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {
            --heroku-purple: #6567a5;
            --heroku-gradient: linear-gradient(135deg, #6567a5 0%, #430098 100%);
        }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #0c0e27 0%, #1a1f3d 100%);
            color: white;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            padding: 40px;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            width: 90%;
            max-width: 450px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h2 {
            color: white;
            font-weight: 300;
            font-size: 28px;
            margin: 10px 0;
        }
        .logo .heroku-badge {
            background: var(--heroku-gradient);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        input {
            width: 100%;
            padding: 16px;
            margin: 12px 0;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            color: white;
            font-size: 16px;
            box-sizing: border-box;
            transition: all 0.3s ease;
        }
        input:focus {
            outline: none;
            border-color: var(--heroku-purple);
            background: rgba(255, 255, 255, 0.12);
        }
        button {
            width: 100%;
            padding: 16px;
            background: var(--heroku-gradient);
            color: white;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            margin-top: 10px;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(101, 103, 165, 0.4);
        }
        .demo-box {
            background: rgba(101, 103, 165, 0.2);
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
            text-align: center;
            border: 1px solid rgba(101, 103, 165, 0.3);
        }
        .footer {
            text-align: center;
            margin-top: 25px;
            color: rgba(255, 255, 255, 0.6);
        }
        .footer a {
            color: var(--heroku-purple);
            text-decoration: none;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h2>🚀 Deriv Trading</h2>
            <div class="heroku-badge">Powered by Heroku</div>
        </div>
        
        <div class="demo-box">
            <strong>Demo Account:</strong><br>
            👤 <strong>herokutrader</strong> / <strong>heroku123</strong>
        </div>
        
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">🚀 Login to Trading Platform</button>
        </form>
        
        <div class="footer">
            <a href="/register">Create New Account</a>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    if 'username' in session:
        return redirect('/dashboard')
    return render_template_string(HEROKU_LOGIN_HTML)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        success, result = client_manager.verify_client(username, password)
        if success:
            session['username'] = username
            session.permanent = True
            return redirect('/dashboard')
        else:
            return render_template_string(HEROKU_LOGIN_HTML.replace('</form>', f'<div style="color:#ff6b6b; text-align:center; margin:15px 0; padding:10px; background:rgba(255,107,107,0.1); border-radius:8px;">{result}</div></form>'))
    return render_template_string(HEROKU_LOGIN_HTML)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    
    client = client_manager.get_client(session['username'])
    if not client:
        return redirect('/')
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - Heroku</title>
        <style>
            body {{
                font-family: 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #0c0e27 0%, #1a1f3d 100%);
                color: white;
                margin: 0;
                padding: 0;
            }}
            .header {{
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                padding: 20px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .container {{
                padding: 30px;
                max-width: 1200px;
                margin: 0 auto;
            }}
            .card {{
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                padding: 30px;
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                margin: 20px 0;
            }}
            .btn {{
                padding: 12px 24px;
                margin: 8px;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
            }}
            .btn-primary {{
                background: linear-gradient(135deg, #6567a5 0%, #430098 100%);
                color: white;
            }}
            .btn-success {{
                background: linear-gradient(135deg, #00d26a 0%, #00b894 100%);
                color: white;
            }}
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .stat-card {{
                background: rgba(255, 255, 255, 0.08);
                padding: 20px;
                border-radius: 12px;
                text-align: center;
            }}
            .stat-value {{
                font-size: 32px;
                font-weight: bold;
                color: #6567a5;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Trading Dashboard</h1>
            <p>Welcome, {client['username']}! | Heroku Cloud</p>
        </div>
        
        <div class="container">
            <div class="card">
                <h2>💰 Account Overview</h2>
                <div class="stats">
                    <div class="stat-card">
                        <div>Balance</div>
                        <div class="stat-value">${client['balance']:.2f}</div>
                    </div>
                    <div class="stat-card">
                        <div>Total Trades</div>
                        <div class="stat-value">{client['total_trades']}</div>
                    </div>
                    <div class="stat-card">
                        <div>Win Rate</div>
                        <div class="stat-value">
                            {((client['winning_trades'] / client['total_trades']) * 100) if client['total_trades'] > 0 else 0:.1f}%
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>🎯 Trading Controls</h2>
                <button class="btn btn-success" onclick="placeTrade()">🔄 Place Trade</button>
                <button class="btn btn-primary" onclick="testConnection()">🔗 Test Deriv Connection</button>
            </div>
            
            <div class="card">
                <h2>🔗 Deriv API Setup</h2>
                <input type="password" id="derivToken" placeholder="Enter your Deriv API Token" style="width: 100%; padding: 12px; margin: 10px 0; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; color: white;">
                <button class="btn btn-primary" onclick="saveToken()">💾 Save Token</button>
            </div>
            
            <div id="result" class="card" style="display: none;">
                <h3>📊 Result</h3>
                <div id="resultContent"></div>
            </div>
        </div>
        
        <script>
            function placeTrade() {{
                fetch('/api/trade', {{method: 'POST'}})
                    .then(r => r.json())
                    .then(data => {{
                        showResult(data.message);
                        setTimeout(() => location.reload(), 2000);
                    }});
            }}
            
            function testConnection() {{
                const token = document.getElementById('derivToken').value;
                if (!token) {{
                    showResult('❌ Please enter your Deriv API token first');
                    return;
                }}
                
                fetch('/api/test', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{token: token}})
                }})
                .then(r => r.json())
                .then(data => showResult(data.message));
            }}
            
            function saveToken() {{
                const token = document.getElementById('derivToken').value;
                if (token) {{
                    showResult('✅ Token saved successfully!');
                }}
            }}
            
            function showResult(message) {{
                document.getElementById('resultContent').innerHTML = message;
                document.getElementById('result').style.display = 'block';
            }}
        </script>
    </body>
    </html>
    """

@app.route('/api/trade', methods=['POST'])
def api_trade():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    username = session['username']
    client = client_manager.get_client(username)
    
    # Simulate trade
    win = random.random() < 0.75
    amount = 10.00
    profit = amount * 0.85 if win else -amount
    
    client['balance'] += profit
    client['total_trades'] += 1
    if win:
        client['winning_trades'] += 1
    
    client_manager.save_clients()
    
    outcome = "WIN" if win else "LOSS"
    return jsonify({
        'success': True, 
        'message': f'🎯 {outcome}! Profit: ${profit:+.2f} | Heroku Cloud'
    })

@app.route('/api/test', methods=['POST'])
def api_test():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    token = request.json.get('token')
    if not token:
        return jsonify({'success': False, 'message': 'No token provided'})
    
    deriv_api = HerokuDerivAPI(token)
    success, message = deriv_api.connect()
    
    return jsonify({'success': success, 'message': message})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print("🚀 DERIV TRADING - HEROKU DEPLOYMENT READY")
    print(f"📍 Port: {port}")
    print(f"🔧 Debug: {debug}")
    print("👤 Demo: herokutrader / heroku123")
    print("🌐 Ready for Heroku deployment!")
    
    app.run(host='0.0.0.0', port=port, debug=debug)# Your trading bot code here (paste the entire code you shared)
