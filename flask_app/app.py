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
    
    process = subprocess.Popen(
        [sys.executable, main_path],
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        text=True,
        close_fds=True,
        cwd=os.path.dirname(main_path),
        env=env
    )
    
    session_id = str(process.pid)
    active_processes[session_id] = {
        'process': process,
        'master_fd': master_fd,
        'slave_fd': slave_fd
    }
    
    return jsonify({'session_id': session_id})

@app.route('/read_output/<session_id>')
def read_output(session_id):
    if session_id not in active_processes:
        return jsonify({'error': 'Invalid session'}), 404
    
    master_fd = active_processes[session_id]['master_fd']
    
    # Non-blocking read from pty
    r, w, e = select.select([master_fd], [], [], 0.05)
    output = ""
    if r:
        try:
            # Read up to 10KB at a time
            output_bytes = os.read(master_fd, 10240)
            output = output_bytes.decode('utf-8', errors='replace')
        except OSError:
            pass
            
    return jsonify({
        'output': output,
        'is_alive': active_processes[session_id]['process'].poll() is None
    })

@app.route('/send_input/<session_id>', methods=['POST'])
def send_input(session_id):
    if session_id not in active_processes:
        return jsonify({'error': 'Invalid session'}), 404
    
    input_text = request.json.get('input', '')
    master_fd = active_processes[session_id]['master_fd']
    try:
        os.write(master_fd, input_text.encode('utf-8'))
    except OSError:
        return jsonify({'error': 'Process closed'}), 500
    
    return jsonify({'status': 'ok'})

@app.route('/upload_save', methods=['POST'])
def upload_save():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    
    # Save the uploaded file to data/saves directory
    saves_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'saves')
    os.makedirs(saves_dir, exist_ok=True)
    
    # Use the original filename but ensure it's secure
    filename = os.path.basename(file.filename)
    if not filename.endswith('.json'):
        filename += '.json'
        
    save_path = os.path.join(saves_dir, filename)
    file.save(save_path)
    
    return jsonify({'status': f'File uploaded as {filename}'})

@app.route('/download_save')
def download_save():
    # Attempt to find the most recent save file in data/saves
    root_dir = os.path.dirname(os.path.dirname(__file__))
    saves_dir = os.path.join(root_dir, 'data', 'saves')
    
    if not os.path.exists(saves_dir):
        # If no directory, return empty
        buffer = io.BytesIO(b'{}')
        return send_file(buffer, as_attachment=True, download_name='save.json', mimetype='application/json')

    save_files = [f for f in os.listdir(saves_dir) if f.endswith('.json')]
    
    if not save_files:
        buffer = io.BytesIO(b'{}')
        return send_file(buffer, as_attachment=True, download_name='save.json', mimetype='application/json')
        
    # Get the most recent one by modification time
    save_files.sort(key=lambda x: os.path.getmtime(os.path.join(saves_dir, x)), reverse=True)
    target_file = os.path.join(saves_dir, save_files[0])
            
    return send_file(target_file, as_attachment=True, download_name=save_files[0])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
