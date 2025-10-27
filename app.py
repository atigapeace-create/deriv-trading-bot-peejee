import os
import random
import time
import threading
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
app.secret_key = os.encret_key = os.environ.get('SECRET_KEY', 'deriv-bot-2024')

print("🚀 DERIV TRADING BOT - READY")

trade_history = []
user_data = {
    'balance': 0.0,
    'total_trades': 0,
    'winning_trades': 0,
    'connected': False
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Deriv Trading Bot</title>
    <style>
        body { font-family: Arial; background: #1e1e1e; color: white; margin: 0; padding: 20px; }
        .container { max-width: 1000px; margin: 0 auto; }
        .card { background: #2d2d2d; padding: 20px; margin: 10px 0; border-radius: 10px; }
        .btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        .btn-success { background: #00ff88; color: black; }
        .btn-danger { background: #ff4444; color: white; }
        .btn-primary { background: #007bff; color: white; }
        .trade-log { background: #1a1a1a; padding: 10px; border-radius: 5px; height: 300px; overflow-y: auto; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🚀 DERIV TRADING BOT</h1>
            <p>Balance: $<span id="balance">{{ balance }}</span> | 
               Trades: {{ total_trades }} | 
               Win Rate: {{ win_rate }}%</p>
        </div>
        
        <div class="card">
            <h2>⚡ Trading Controls</h2>
            <button class="btn btn-primary" onclick="addBalance()">💰 Add $1000 Demo Balance</button>
            <select id="symbol" style="padding: 8px; margin: 5px;">
                <option value="R_100">Volatility 100</option>
                <option value="R_50">Volatility 50</option>
            </select>
            <input type="number" id="amount" value="10" style="padding: 8px; margin: 5px; width: 80px;">
            <select id="direction" style="padding: 8px; margin: 5px;">
                <option value="CALL">CALL</option>
                <option value="PUT">PUT</option>
            </select>
            <button class="btn btn-success" onclick="placeTrade()">🎯 Place Trade</button>
            <button class="btn btn-primary" onclick="startAutoTrading()">🤖 Start Auto Trading</button>
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
        function addBalance() {
            fetch('/add_balance', {method: 'POST'})
            .then(r => r.json())
            .then(data => {
                alert(data.message);
                location.reload();
            });
        }
        
        function placeTrade() {
            const symbol = document.getElementById('symbol').value;
            const amount = parseFloat(document.getElementById('amount').value);
            const direction = document.getElementById('direction').value;
            
            fetch('/trade', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({symbol, amount, direction})
            })
            .then(r => r.json())
            .then(data => {
                alert(data.message);
                location.reload();
            });
        }
        
        function startAutoTrading() {
            fetch('/start_auto', {method: 'POST'})
            .then(r => r.json())
            .then(data => alert(data.message));
        }
        
        function stopAutoTrading() {
            fetch('/stop_auto', {method: 'POST'})
            .then(r => r.json())
            .then(data => alert(data.message));
        }
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
        trades=trade_history[-15:]
    )

@app.route('/add_balance', methods=['POST'])
def add_balance():
    user_data['balance'] = 1000.00
    user_data['connected'] = True
    return jsonify({'success': True, 'message': '✅ $1000 demo balance added!'})

@app.route('/trade', methods=['POST'])
def trade():
    if user_data['balance'] <= 0:
        return jsonify({'success': False, 'message': '❌ Add balance first!'})
    
    symbol = request.json.get('symbol', 'R_100')
    amount = float(request.json.get('amount', 10))
    direction = request.json.get('direction', 'CALL')
    
    if amount > user_data['balance']:
        return jsonify({'success': False, 'message': '❌ Insufficient balance!'})
    
    # Execute trade
    win = random.random() < 0.70
    profit = amount * 0.85 if win else -amount
    
    user_data['balance'] += profit
    user_data['total_trades'] += 1
    if win:
        user_data['winning_trades'] += 1
    
    message = f"🎯 {symbol} {direction} - {'WIN' if win else 'LOSS'}: ${profit:+.2f}"
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
        symbols = ['R_100', 'R_50']
        symbol = random.choice(symbols)
        amount = min(10, user_data['balance'] * 0.1)  # 10% of balance max
        direction = "CALL" if random.random() > 0.5 else "PUT"
        
        win = random.random() < 0.70
        profit = amount * 0.85 if win else -amount
        
        user_data['balance'] += profit
        user_data['total_trades'] += 1
        if win:
            user_data['winning_trades'] += 1
        
        message = f"🤖 AUTO - {symbol} {direction} - {'WIN' if win else 'LOSS'}: ${profit:+.2f}"
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
        return jsonify({'success': False, 'message': '❌ Add balance first!'})
    
    auto_trading_active = True
    thread = threading.Thread(target=auto_trade_worker)
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': '🤖 Auto Trading Started! (30s intervals)'})

@app.route('/stop_auto', methods=['POST'])
def stop_auto():
    global auto_trading_active
    auto_trading_active = False
    return jsonify({'success': True, 'message': '🛑 Auto Trading Stopped!'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 TRADING BOT STARTED - Ready for demo trading")
    app.run(host='0.0.0.0', port=port, debug=False)
