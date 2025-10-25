cat > app.py << 'EOF'
import os
import random
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'auto-trading-bot-2024')

user_data = {
    'balance': 1000.00,
    'total_trades': 0,
    'winning_trades': 0
}
trade_history = []

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Auto Trading Bot</title>
    <style>
        body { font-family: Arial; background: #1e1e1e; color: white; padding: 20px; }
        .card { background: #2d2d2d; padding: 20px; margin: 10px 0; border-radius: 10px; }
        .btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; }
        .btn-success { background: #00ff88; color: black; }
        .btn-primary { background: #007bff; color: white; }
        .trade-log { background: #1a1a1a; padding: 10px; border-radius: 5px; height: 200px; overflow-y: auto; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🚀 Auto Trading Bot</h1>
        <p>Balance: ${{ balance }} | Trades: {{ total_trades }} | Win Rate: {{ win_rate }}%</p>
    </div>
    
    <div class="card">
        <h2>⚡ Trading Controls</h2>
        <button class="btn btn-success" onclick="startAutoTrading()">🚀 Start Auto Trading (5 trades)</button>
        <button class="btn btn-primary" onclick="placeTrade()">🎯 Single Trade</button>
    </div>
    
    <div class="card">
        <h2>📊 Trade Log</h2>
        <div class="trade-log" id="tradeLog">
            {% for trade in trades %}
                <div>[{{ trade.time }}] {{ trade.message }}</div>
            {% endfor %}
        </div>
    </div>

    <script>
        function startAutoTrading() {
            fetch('/start_auto', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    alert(data.message);
                    setTimeout(() => location.reload(), 3000);
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

@app.route('/')
def index():
    win_rate = (user_data['winning_trades'] / user_data['total_trades'] * 100) if user_data['total_trades'] > 0 else 0
    return render_template_string(
        HTML,
        balance=user_data['balance'],
        total_trades=user_data['total_trades'],
        win_rate=round(win_rate, 1),
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
    
    outcome = "WIN" if win else "LOSS"
    message = f"🎯 {outcome}! Profit: ${profit:+.2f}"
    trade_history.append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'message': message
    })
    
    return jsonify({'success': True, 'message': message})

@app.route('/start_auto', methods=['POST'])
def start_auto():
    for i in range(5):
        win = random.random() < 0.70
        amount = 10.00
        profit = amount * 0.80 if win else -amount
        
        user_data['balance'] += profit
        user_data['total_trades'] += 1
        if win:
            user_data['winning_trades'] += 1
        
        outcome = "WIN" if win else "LOSS"
        message = f"🤖 Auto Trade {i+1}: {outcome}! Profit: ${profit:+.2f}"
        trade_history.append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'message': message
        })
    
    return jsonify({'success': True, 'message': '✅ Auto trading completed! 5 trades executed.'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Auto Trading Bot running...")
    app.run(host='0.0.0.0', port=port, debug=False)
EOF
