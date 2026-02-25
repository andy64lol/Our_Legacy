import sys
import os
import json
from typing import Optional, Any

def running_in_flask():
    try:
        # Flask sets up `flask.app.Flask` objects
        from flask import request
        # `request` exists only during an actual HTTP request context
        return request is not None
    except RuntimeError:
        # Accessing `request` outside a request context raises RuntimeError
        return False
    except ImportError:
        # Flask isn't installed at all
        return False


def get_save_directory() -> str:
    """
    Get the saves directory path.
    Creates the directory if it doesn't exist.
    """
    root_dir = os.path.dirname(os.path.dirname(__file__))
    saves_dir = os.path.join(root_dir, 'data', 'saves')
    os.makedirs(saves_dir, exist_ok=True)
    return saves_dir


def get_flask_upload_path() -> Optional[str]:
    """
    Get the path where Flask uploaded a save file.
    Returns None if not in Flask context or no upload exists.
    """
    if not running_in_flask():
        return None
    
    try:
        from flask import request
        # Check if this is an upload request
        if request.method == 'POST' and 'file' in request.files:
            # Return the path in the saves directory
            saves_dir = get_save_directory()
            return os.path.join(saves_dir, 'uploaded_save.json')
    except Exception:
        pass
    return None


def get_flask_save_path() -> Optional[str]:
    """
    Get the path where Flask expects save files to be saved.
    Returns None if not in Flask context.
    """
    if not running_in_flask():
        return None
    
    saves_dir = get_save_directory()
    return os.path.join(saves_dir, 'flask_save.json')


def save_to_flask(data: Any, filepath: str) -> bool:
    """
    Save data to the Flask-accessible save file.
    Returns True if successful, False otherwise.
    """
    if running_in_flask():
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False
    return False


def load_from_flask(filepath: str) -> Optional[Any]:
    """
    Load data from the Flask-accessible save file.
    Returns None if not in Flask context or load fails.
    """
    if running_in_flask():
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
    return None
