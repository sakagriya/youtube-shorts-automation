from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_endpoint():
    input_data = request.json.get("input", {})
    return jsonify({
        "status": "success",
        "message": "Hello from RunPod Serverless!",
        "received_input": input_data
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
