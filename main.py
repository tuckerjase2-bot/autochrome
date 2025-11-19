from flask import Flask, render_template, request, jsonify
from automator import run_plan
from gpt_builder import generate_plan
import threading
import os

app = Flask(__name__, template_folder="templates")
status = {"running": False, "last": None}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/run', methods=['POST'])
def run():
    data = request.json or {}
    headless = data.get('headless', True)

    def target():
        status['running'] = True
        try:
            res = run_plan(data, headless=headless)
            status['last'] = res
        finally:
            status['running'] = False

    t = threading.Thread(target=target, daemon=True)
    t.start()
    return jsonify({'ok': True})


@app.route('/status')
def get_status():
    return jsonify(status)


@app.route('/generate', methods=['POST'])
def generate():
    payload = request.json or {}
    prompt = payload.get('prompt', '')
    plan = generate_plan(prompt)
    return jsonify(plan)


if __name__ == '__main__':
    # Use localhost on port 8080 by default (can override with PORT env var)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='localhost', port=port, debug=True)
