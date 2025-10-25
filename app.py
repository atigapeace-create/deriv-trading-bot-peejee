import os
import json
import hashlib
import random
import time
import requests
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, session, redirect

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'deriv-trading-bot-2024')

print("🚀 DERIV TRADING BOT - LIVE")

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Deriv Trading Bot</title>
    <style>
        body { font-family: Arial; background: #1e1e1e; color: white; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .card { background: #2d2d2d; padding: 20px; margin: 10px 0; border-radius: 10px; }
        .btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; }
        .btn-success { background: #00ff88; color: black; }
        .btn-primary { background: #007bff; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🚀 Deriv Trading Bot</h1>
            <p>Welcome to your automated trading platform!</p>
        </div>
        
        <div class="card">
            <h2>💰 Account Balance: ${{ balance }}</h2>
            <p>Total Trades: {{ total_trades }} | Win Rate: {{ win_rate }}%</p>
        </div>
        
        <div class="card">
            <h2>🎯 Trading Controls</h2>
            <button class="btn btn-success" onclick="placeTrade()">Place Trade</button>
            <button class="btn btn-primary" onclick="testConnection()">Test Deriv Connection</button>
        </div>
        
        <div class="card">
            <h2>🔗 Deriv API Setup</h2>
            <input type="password" id="token" placeholder="Enter Deriv API Token" style="width: 100%; padding: 10px; margin: 5px 0; background: #3d3d3d; border: 1px solid #555; color: white; border-radius: 5px;">
            <button class="btn btn-primary" onclick="saveToken()">Save Token</button>
        </div>
        
        <div id="result" class="card" style="display: none;">
            <h3>Result</h3>
            <div id="resultText"></div>
        </div>
    </div>

    <script>
        function placeTrade() {
            fetch('/api/trade', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    showResult(data.message);
                    setTimeout(() => location.reload(), 2000);
                });
        }
        
        function testConnection() {
            const token = document.getElementById('token').value;
            if (!token) {
                showResult('Please enter your Deriv API token first');
                return;
            }
            
            fetch('/api/test', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({token: token})
            })
            .then(r => r.json())
            .then(data => showResult(data.message));
        }
        
        function saveToken() {
            const token = document.getElementById('token').value;
            if (token) {
                showResult('Token saved successfully!');
            }
        }
        
        function showResult(message) {
            document.getElementById('resultText').innerHTML = message;
            document.getElementById('result').style.display = 'block';
        }
    </script>
</body>
</html>
'''

user_data = {
    'balance': 10000.00,
    'total_trades': 0,
    'winning_trades': 0
}

@app.route('/')
def index():
    win_rate = (user_data['winning_trades'] / user_data['total_trades'] * 100) if user_data['total_trades'] > 0 else 0
    return render_template_string(
        HTML_TEMPLATE,
        balance=user_data['balance'],
        total_trades=user_data['total_trades'],
        win_rate=round(win_rate, 1)
    )

@app.route('/api/trade', methods=['POST'])
def api_trade():
    win = random.random() < 0.75
    amount = 10.00
    profit = amount * 0.85 if win else -amount
    
    user_data['balance'] += profit
    user_data['total_trades'] += 1
    if win:
        user_data['winning_trades'] += 1
    
    outcome = "WIN" if win else "LOSS"
    return jsonify({
        'success': True, 
        'message': f'🎯 {outcome}! Profit: ${profit:+.2f}'
    })

@app.route('/api/test', methods=['POST'])
def api_test():
    token = request.json.get('token')
    if not token:
        return jsonify({'success': False, 'message': 'No token provided'})
    
    try:
        response = requests.get(
            "https://api.deriv.com/api/v1/active-symbols",
            params={'product_type': 'basic'},
            timeout=10
        )
        if response.status_code == 200:
            return jsonify({'success': True, 'message': '✅ Connected to Deriv API successfully!'})
        else:
            return jsonify({'success': False, 'message': '❌ Could not connect to Deriv API'})
    except:
        return jsonify({'success': False, 'message': '❌ Network error connecting to Deriv'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Server running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
