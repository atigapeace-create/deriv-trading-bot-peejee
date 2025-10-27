import requests

@app.route('/connect_deriv', methods=['POST'])
def connect_deriv():
    global real_api, user_data
    
    deriv_token = request.json.get('deriv_token')
    if not deriv_token:
        return jsonify({'success': False, 'message': 'No token provided'})
    
    try:
        # Test connection and get real balance
        response = requests.get(
            'https://api.deriv.com/api/v1/balance',
            params={'account': 'all', 'token': deriv_token},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            real_balance = 0
            
            # Try different balance paths in response
            if 'balance' in data and 'balance' in data['balance']:
                real_balance = data['balance']['balance']
            elif 'authorize' in data and 'balance' in data['authorize']:
                real_balance = data['authorize']['balance']
            elif 'get_account_status' in data and 'balance' in data['get_account_status']:
                real_balance = data['get_account_status']['balance']
            
            # Initialize API
            real_api = RealDerivAPI(deriv_token)
            success, message = real_api.connect_websocket()
            
            if success:
                user_data['real_connected'] = True
                user_data['balance'] = float(real_balance) if real_balance else 0.0
                user_data['deriv_token'] = deriv_token
                
                balance_msg = f'${user_data["balance"]:.2f}' if real_balance else 'Connected (balance unavailable)'
                
                return jsonify({
                    'success': True, 
                    'message': f'✅ Connected to Deriv! Balance: {balance_msg}',
                    'balance': user_data['balance']
                })
            else:
                return jsonify({'success': False, 'message': f'WebSocket failed: {message}'})
        else:
            return jsonify({'success': False, 'message': f'API Error: {response.status_code}'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Connection error: {str(e)}'})
