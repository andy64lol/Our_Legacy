from flask import Flask, render_template, request, jsonify, send_file, after_this_request
import subprocess
import os
import sys
import pty
import select
import threading
import json
import io
import time

app = Flask(__name__)

# Dictionary to store active processes
active_processes = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_terminal', methods=['POST'])
def start_terminal():
    # Use pty to simulate a real terminal for TUI support
    master_fd, slave_fd = pty.openpty()
    
    main_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main.py')
    
    # Environment variables to handle terminal colors and encoding
    env = os.environ.copy()
    env['TERM'] = 'xterm-256color'
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUNBUFFERED'] = '1'
    
    # Run with --json-api if supported or detect it
    process = subprocess.Popen(
        [sys.executable, main_path, "--json-api"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.dirname(main_path),
        env=env
    )
    
    session_id = str(process.pid)
    active_processes[session_id] = {
        'process': process
    }
    
    return jsonify({'session_id': session_id})

@app.route('/read_output/<session_id>')
def read_output(session_id):
    if session_id not in active_processes:
        return jsonify({'error': 'Invalid session'}), 404
    
    process = active_processes[session_id]['process']
    
    output = ""
    # Use select for non-blocking read from pipe
    if process.stdout:
        import select
        r, w, e = select.select([process.stdout], [], [], 0.05)
        if r:
            output = process.stdout.readline()
            
    return jsonify({
        'output': output,
        'is_alive': process.poll() is None
    })

@app.route('/send_input/<session_id>', methods=['POST'])
def send_input(session_id):
    if session_id not in active_processes:
        return jsonify({'error': 'Invalid session'}), 404
    
    input_text = (request.json or {}).get('input', '')
    process = active_processes[session_id]['process']
    try:
        process.stdin.write(input_text + '\n')
        process.stdin.flush()
    except (OSError, BrokenPipeError):
        return jsonify({'error': 'Process closed'}), 500
    
    return jsonify({'status': 'ok'})

@app.route('/upload_save', methods=['POST'])
def upload_save():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    
    # Save the uploaded file to data/saves/ directory for main.py access
    saves_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'saves')
    os.makedirs(saves_dir, exist_ok=True)
    
    # Save as uploaded_save.json so main.py can detect and load it
    save_path = os.path.join(saves_dir, 'uploaded_save.json')
    file.save(save_path)
    
    return jsonify({'status': 'File uploaded to data/saves/uploaded_save.json'})

@app.route('/download_save')
def download_save():
    # Look for save files in data/saves/ directory where main.py saves them
    saves_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'saves')
    
    target_file = None
    if os.path.exists(saves_dir):
        # Get the most recent save file (excluding uploaded_save.json and flask_save.json)
        save_files = [f for f in os.listdir(saves_dir) if f.endswith('.json') 
                      and f not in ['uploaded_save.json', 'flask_save.json']]
        if save_files:
            # Sort by modification time, most recent first
            save_files.sort(key=lambda f: os.path.getmtime(os.path.join(saves_dir, f)), reverse=True)
            target_file = os.path.join(saves_dir, save_files[0])
    
    if target_file:
        return send_file(target_file, as_attachment=True)
    else:
        # If no file exists, return an empty template
        buffer = io.BytesIO(b'{}')
        return send_file(buffer, as_attachment=True, download_name='save.json', mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
