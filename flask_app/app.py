from flask import Flask, render_template, request, jsonify
import subprocess
import os
import sys

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_code():
    try:
        # Path to main.py in the root directory
        main_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main.py')
        
        if os.path.exists(main_path):
            # Run main.py using the same python interpreter
            # Use -u for unbuffered output
            result = subprocess.run(
                [sys.executable, main_path], 
                capture_output=True, 
                text=True, 
                timeout=30,
                cwd=os.path.dirname(main_path)
            )
            return jsonify({
                'stdout': result.stdout,
                'stderr': result.stderr,
                'exit_code': result.returncode
            })
        else:
            return jsonify({'error': f'main.py not found at {main_path}'}), 404
    except subprocess.TimeoutExpired as e:
        return jsonify({
            'error': 'Execution timed out',
            'stdout': e.stdout,
            'stderr': e.stderr
        }), 408
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Bind to 0.0.0.0:5000 for Replit webview
    app.run(host='0.0.0.0', port=5000)
