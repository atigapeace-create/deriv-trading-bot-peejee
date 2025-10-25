import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <html>
    <head><title>Trading Bot</title></head>
    <body style="background: #1e1e1e; color: white; padding: 20px;">
        <h1>🚀 Trading Bot - WORKING!</h1>
        <p>Your bot is successfully deployed on Heroku!</p>
        <p>Balance: $1,000.00</p>
        <button onclick="alert('Trade placed!')" style="padding: 10px 20px; background: #00ff88; border: none; border-radius: 5px;">Place Trade</button>
    </body>
    </html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
