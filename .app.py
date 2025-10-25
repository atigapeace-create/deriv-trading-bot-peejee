# Create a new working app.py
cat > app.py << 'EOF'
import os
import random
import time
import requests
import threading
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'auto-trading-bot-2024')

print("🚀 AUTO TRADING BOT - LIVE")

auto_trading_active = False
trade_history = []

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Auto Trading Bot</title>
    <style>
        body { font-family: Arial; background: #1e1e1e; color: white; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .card { background: #2d2d2d; padding: 20px; margin: 10px 0; border-radius: 10px; }
        .btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        .btn-success { background: #00ff88; color: black; }
        .btn-danger { background: #ff4444; color: white; }
        .btn-primary { background: #007bff; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🚀 Auto Trading Bot</h1>
            <p>Balance: ${{ balance }} | Trades: {{ total_trades }} | Win Rate: {{ win_rate }}%</p>
        </div>
        
        <div class="card">
            <h2>⚡ Trading Controls</h2>
            <input type="number" id="amount" value="10" style="padding: 8px; margin: 5px; width: 100px;">
            {% if auto_trading %}
                <button class="btn btn-danger" onclick="stopAutoTrading()">🛑 Stop Auto Trading</button>
                <div style="color: #00ff88;">🟢 AUTO TRADING ACTIVE</div>
            {% else %}
                <button class="btn btn-success" onclick="startAutoTrading()">🚀 Start Auto Trading</button>
                <div style="color: #ff4444;">🔴 AUTO TRADING INACTIVE</div>
            {% endif %}
            <button class="btn btn-primary" onclick="placeTrade()">🎯 Single Trade</button>
        </div>
        
        <div class="card">
            <h2>📊 Trade Log</h2>
            <div style="background: #1a1a1a; padding: 10px; border-radius: 5px; height: 200px; overflow-y: auto;">
                {% for trade in trades %}
                    <div>[{{ trade.time }}] {{ trade.message }}</div>
                {% endfor %}
            </div>
        </div>
    </div>

    <script>
        function startAutoTrading() {
            fetch('/start_auto', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    alert(data.message);
                    location.reload();
                });
        }
        
        function stopAutoTrading() {
            fetch('/stop_auto', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    alert(data.message);
                    location.reload();
                });
        }
        
        function placeTrade() {
            fetch('/trade', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    alert(data.message);
                    location.reload();
                });
        }
    </script>
</body>
</html>
'''

user_data = {
    'balance': 1000.00,
    'total_trades': 0,
    'winning_trades': 0,
    'auto_trading': False
}

def auto_trade_worker():
    global auto_trading_active
    count = 0
    while auto_trading_active and count < 10:
        win = random.random() < 0.7
        amount = 10.00
        profit = amount * 0.8 if win else -amount
        
        user_data['balance'] += profit
        user_data['total_trades'] += 1
        if win:
            user_data['winning_trades'] += 1
        
        message = f"{'WIN' if win else 'LOSS'}! Profit: ${profit:+.2f}"
        trade_history.append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'message': message
        })
        
        count += 1
        time.sleep(30)
    
    auto_trading_active = False
    user_data['auto_trading'] = False

@app.route('/')
def index():
    win_rate = (user_data['winning_trades'] / user_data['total_trades'] * 100) if user_data['total_trades'] > 0 else 0
    return render_template_string(
        HTML_TEMPLATE,
        balance=user_data['balance'],
        total_trades=user_data['total_trades'],
        win_rate=round(win_rate, 1),
        auto_trading=user_data['auto_trading'],
        trades=trade_history[-10:]
    )

@app.route('/trade', methods=['POST'])
def trade():
    win = random.random() < 0.75
    amount = 10.00
    profit = amount * 0.85 if win else -amount
    
    user_data['balance'] += profit
    user_data['total_trades'] += 1
    if win:
        user_data['winning_trades'] += 1
    
    message = f"Single trade: {'WIN' if win else 'LOSS'}! Profit: ${profit:+.2f}"
    trade_history.append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'message': message
    })
    
    return jsonify({'success': True, 'message': message})

@app.route('/start_auto', methods=['POST'])
def start_auto():
    global auto_trading_active
    if auto_trading_active:
        return jsonify({'success': False, 'message': 'Already running!'})
    
    user_data['auto_trading'] = True
    auto_trading_active = True
    
    thread = threading.Thread(target=auto_trade_worker)
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': 'Auto trading started!'})

@app.route('/stop_auto', methods=['POST'])
def stop_auto():
    global auto_trading_active
    auto_trading_active = False
    user_data['auto_trading'] = False
    return jsonify({'success': True, 'message': 'Auto trading stopped!'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Server running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
EOF
