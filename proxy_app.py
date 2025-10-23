from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Your PythonAnywhere server
TARGET_SERVER = "http://isuru.pythonanywhere.com"

@app.route('/solar-data', methods=['POST', 'GET'])
def proxy_solar_data():
    try:
        target_url = f"{TARGET_SERVER}/solar-data"
        
        if request.method == 'POST':
            # Forward POST request with JSON data
            response = requests.post(
                target_url, 
                json=request.get_json(),
                headers={'Content-Type': 'application/json'}
            )
        else:  # GET
            response = requests.get(target_url)
            
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        return jsonify({'error': f'Proxy error: {str(e)}'}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({
        'status': 'proxy_working',
        'message': 'Proxy server is running correctly',
        'target_server': TARGET_SERVER
    })

@app.route('/')
def home():
    return jsonify({
        'message': 'Solar Data Proxy Server', 
        'target': TARGET_SERVER,
        'usage': 'POST/GET to /solar-data'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
