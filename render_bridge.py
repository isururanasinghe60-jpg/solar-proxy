from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Your PythonAnywhere server
TARGET_SERVER = "http://isuru.pythonanywhere.com"

@app.route('/bridge-endpoint', methods=['POST', 'GET'])
def bridge_endpoint():
    """
    Receives data from Arduino and forwards to PythonAnywhere
    """
    if request.method == 'POST':
        try:
            # Get data from Arduino
            arduino_data = request.get_json()
            
            if not arduino_data:
                return jsonify({'error': 'No data received'}), 400
            
            # Add bridge timestamp
            arduino_data['bridge_received_at'] = datetime.now().isoformat()
            arduino_data['bridge_source'] = 'render'
            
            print(f"📨 Received from Arduino: {arduino_data}")
            
            # Forward to your PythonAnywhere solar-data endpoint
            response = requests.post(
                f"{TARGET_SERVER}/solar-data",
                json=arduino_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"✅ Forwarded to PythonAnywhere - Status: {response.status_code}")
            
            if response.status_code == 200:
                return jsonify({
                    'status': 'success', 
                    'message': 'Data forwarded to PythonAnywhere successfully',
                    'bridge_response': response.json()
                }), 200
            else:
                return jsonify({
                    'error': f'PythonAnywhere returned {response.status_code}',
                    'details': response.text
                }), 500
                
        except Exception as e:
            print(f"❌ Bridge error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'GET':
        # Test endpoint
        return jsonify({
            'status': 'bridge_working',
            'message': 'Render.com bridge is running',
            'target_server': TARGET_SERVER,
            'timestamp': datetime.now().isoformat()
        })

@app.route('/test-connection', methods=['GET'])
def test_connection():
    """Test connection to PythonAnywhere"""
    try:
        response = requests.get(f"{TARGET_SERVER}/solar-data", timeout=10)
        return jsonify({
            'pythonanywhere_status': 'reachable',
            'response_code': response.status_code,
            'test_time': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'pythonanywhere_status': 'unreachable',
            'error': str(e)
        }), 500

@app.route('/')
def home():
    return jsonify({
        'service': 'Solar Data Bridge',
        'provider': 'Render.com',
        'target': TARGET_SERVER,
        'endpoints': {
            'POST data': '/bridge-endpoint',
            'Test bridge': '/bridge-endpoint (GET)',
            'Test PythonAnywhere': '/test-connection'
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
