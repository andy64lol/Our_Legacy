"""
Account Manager - Client-side module for Our Legacy CLI game
Handles account operations via API calls to Vercel serverless functions
No backend logic or environment variables - pure client-side
"""

import json
import os
from typing import Dict, Any, Optional, Tuple
import requests


class AccountManager:
    """Client-side account manager for CLI game - calls Vercel API endpoints"""
    
    def __init__(self, api_base_url: str = "https://our-legacy.vercel.app/api"):
        self.api_base_url = api_base_url
        self.auth_endpoint = f"{api_base_url}/auth"
        self.login_endpoint = f"{api_base_url}/login_fetch"
        self.session_file = "data/account_session.json"
        self.saves_dir = "data/saves"
        self.current_account: Optional[Dict[str, Any]] = None
        
        # Ensure saves directory exists
        os.makedirs(self.saves_dir, exist_ok=True)
        os.makedirs("data", exist_ok=True)
        
        # Load existing session
        self._load_session()
    
    def _load_session(self) -> None:
        """Load saved session from local file"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    session = json.load(f)
                    if session.get('logged_in') and session.get('account'):
                        self.current_account = session['account']
        except (json.JSONDecodeError, IOError):
            self.current_account = None
    
    def _save_session(self) -> None:
        """Save current session to local file"""
        try:
            session = {
                'logged_in': self.current_account is not None,
                'account': self.current_account,
                'timestamp': self._get_timestamp()
            }
            with open(self.session_file, 'w') as f:
                json.dump(session, f, separators=(',', ':'))
        except IOError:
            pass
    
    def _clear_session(self) -> None:
        """Clear local session file"""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
        except IOError:
            pass
    
    def _get_timestamp(self) -> str:
        """Get current ISO timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def is_logged_in(self) -> bool:
        """Check if user is currently logged in"""
        return self.current_account is not None
    
    def get_current_account(self) -> Optional[Dict[str, Any]]:
        """Get current logged in account info"""
        return self.current_account
    
    def get_account_id(self) -> Optional[str]:
        """Get current account ID"""
        if self.current_account:
            return self.current_account.get('account_id')
        return None
    
    def get_username(self) -> Optional[str]:
        """Get current username"""
        if self.current_account:
            return self.current_account.get('username')
        return None
    
    def register(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        """
        Register a new account via API
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            payload = {
                'username': username,
                'email': email,
                'password': password
            }
            
            response = requests.post(
                f"{self.auth_endpoint}?action=register",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            data = response.json()
            
            if response.status_code == 201 and data.get('ok'):
                # Auto-login after registration
                self.current_account = data.get('account')
                self._save_session()
                return True, "Account created successfully!"
            else:
                error_msg = data.get('message', 'Registration failed')
                return False, error_msg
                
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Login to existing account via API
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            payload = {
                'username': username,
                'password': password
            }
            
            # Use dedicated login endpoint
            response = requests.post(
                self.login_endpoint,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get('ok'):
                account_data = data.get('account')
                if account_data:
                    self.current_account = account_data
                    self._save_session()
                    username = account_data.get('username', 'User')
                    return True, f"Welcome back, {username}!"
                else:
                    return False, "Login failed: Invalid account data"
            else:
                error_msg = data.get('message', 'Login failed')
                return False, error_msg
                
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def logout(self) -> None:
        """Logout and clear local session"""
        self.current_account = None
        self._clear_session()
    
    def request_recovery(self, email: str) -> Tuple[bool, str, Optional[str]]:
        """
        Request password recovery via API
        
        Returns:
            Tuple of (success: bool, message: str, token: Optional[str])
            Note: In production, token would be emailed, not returned
        """
        try:
            payload = {'email': email}
            
            response = requests.post(
                f"{self.auth_endpoint}?action=recover",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get('ok'):
                # In production, token is emailed. For testing, it's returned
                token = data.get('recovery_token')
                return True, data.get('message', 'Recovery email sent'), token
            else:
                error_msg = data.get('message', 'Recovery request failed')
                return False, error_msg, None
                
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}", None
        except Exception as e:
            return False, f"Error: {str(e)}", None
    
    def verify_recovery_token(self, email: str, token: str) -> Tuple[bool, str]:
        """
        Verify recovery token via API
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            payload = {
                'email': email,
                'token': token
            }
            
            response = requests.post(
                f"{self.auth_endpoint}?action=verify",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get('ok'):
                return True, "Token verified successfully"
            else:
                error_msg = data.get('message', 'Token verification failed')
                return False, error_msg
                
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def reset_password(self, email: str, token: str, new_password: str) -> Tuple[bool, str]:
        """
        Reset password with verified token via API
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            payload = {
                'email': email,
                'token': token,
                'new_password': new_password
            }
            
            response = requests.post(
                f"{self.auth_endpoint}?action=reset",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get('ok'):
                return True, "Password reset successfully"
            else:
                error_msg = data.get('message', 'Password reset failed')
                return False, error_msg
                
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_account_info(self, account_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Get account info by ID via API
        
        Returns:
            Tuple of (success: bool, data: dict)
        """
        try:
            response = requests.get(
                f"{self.auth_endpoint}?action=info&account_id={account_id}",
                timeout=10
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get('ok'):
                return True, data.get('account', {})
            else:
                return False, {'error': data.get('message', 'Failed to get account info')}
                
        except requests.exceptions.RequestException as e:
            return False, {'error': f"Connection error: {str(e)}"}
        except Exception as e:
            return False, {'error': f"Error: {str(e)}"}
    
    # === Account-Linked Save Game Methods ===
    
    def get_account_save_path(self) -> Optional[str]:
        """Get the save file path for current account"""
        account_id = self.get_account_id()
        if not account_id:
            return None
        return os.path.join(self.saves_dir, f"account_{account_id}.json")
    
    def has_account_save(self) -> bool:
        """Check if account has a linked save game"""
        save_path = self.get_account_save_path()
        if not save_path:
            return False
        return os.path.exists(save_path)
    
    def save_account_game(self, game_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Save game data linked to account (local file only, no API call)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.is_logged_in():
            return False, "Not logged in"
        
        save_path = self.get_account_save_path()
        if not save_path:
            return False, "Invalid account"
        
        try:
            # Add metadata
            save_data = {
                'account_id': self.get_account_id(),
                'username': self.get_username(),
                'saved_at': self._get_timestamp(),
                'game_data': game_data
            }
            
            # Save without spaces (compact JSON)
            with open(save_path, 'w') as f:
                json.dump(save_data, f, separators=(',', ':'))
            
            return True, "Game saved to account"
            
        except IOError as e:
            return False, f"Failed to save: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def load_account_game(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Load game data linked to account
        
        Returns:
            Tuple of (success: bool, data: dict)
        """
        if not self.is_logged_in():
            return False, {'error': 'Not logged in'}
        
        save_path = self.get_account_save_path()
        if not save_path:
            return False, {'error': 'Invalid account'}
        
        if not os.path.exists(save_path):
            return False, {'error': 'No save found for this account'}
        
        try:
            with open(save_path, 'r') as f:
                save_data = json.load(f)
            
            # Verify account ID matches
            if save_data.get('account_id') != self.get_account_id():
                return False, {'error': 'Save file does not match account'}
            
            return True, save_data.get('game_data', {})
            
        except (json.JSONDecodeError, IOError) as e:
            return False, {'error': f'Failed to load: {str(e)}'}
        except Exception as e:
            return False, {'error': f'Error: {str(e)}'}
    
    def delete_account_save(self) -> Tuple[bool, str]:
        """
        Delete account-linked save file
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.is_logged_in():
            return False, "Not logged in"
        
        save_path = self.get_account_save_path()
        if not save_path:
            return False, "Invalid account"
        
        try:
            if os.path.exists(save_path):
                os.remove(save_path)
                return True, "Account save deleted"
            else:
                return False, "No save to delete"
        except IOError as e:
            return False, f"Failed to delete: {str(e)}"


# Global instance for easy import
account_manager = AccountManager()


# === CLI Interface Functions ===

def show_account_menu():
    """Display account menu for CLI"""
    print("\n" + "="*50)
    print("ACCOUNT MANAGEMENT")
    print("="*50)
    
    if account_manager.is_logged_in():
        username = account_manager.get_username()
        print(f"Logged in as: {username}")
        print("\n1. Logout")
        print("2. Save Game to Account")
        print("3. Load Game from Account")
        print("4. Delete Account Save")
        print("5. Back to Main Menu")
    else:
        print("Not logged in")
        print("\n1. Login")
        print("2. Create Account")
        print("3. Recover Password")
        print("4. Back to Main Menu")
    
    print("="*50)


def handle_login() -> bool:
    """Handle CLI login prompt"""
    print("\n--- Login ---")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    
    if not username or not password:
        print("Error: Username and password required")
        return False
    
    success, message = account_manager.login(username, password)
    print(message)
    return success


def handle_register() -> bool:
    """Handle CLI registration prompt"""
    print("\n--- Create Account ---")
    username = input("Username (3-20 chars, alphanumeric): ").strip()
    email = input("Email: ").strip()
    password = input("Password (min 8 chars): ").strip()
    confirm = input("Confirm Password: ").strip()
    
    if not all([username, email, password]):
        print("Error: All fields required")
        return False
    
    if password != confirm:
        print("Error: Passwords do not match")
        return False
    
    success, message = account_manager.register(username, email, password)
    print(message)
    return success


def handle_recovery() -> bool:
    """Handle CLI password recovery"""
    print("\n--- Password Recovery ---")
    print("1. Request recovery token")
    print("2. Reset password with token")
    choice = input("Choice: ").strip()
    
    if choice == "1":
        email = input("Enter your email: ").strip()
        if not email:
            print("Error: Email required")
            return False
        
        success, message, token = account_manager.request_recovery(email)
        print(message)
        if token:
            print(f"Recovery token (save this): {token}")
        return success
    
    elif choice == "2":
        email = input("Email: ").strip()
        token = input("Recovery token: ").strip()
        
        # Verify token first
        success, message = account_manager.verify_recovery_token(email, token)
        print(message)
        
        if not success:
            return False
        
        new_password = input("New password (min 8 chars): ").strip()
        confirm = input("Confirm new password: ").strip()
        
        if new_password != confirm:
            print("Error: Passwords do not match")
            return False
        
        success, message = account_manager.reset_password(email, token, new_password)
        print(message)
        return success
    
    else:
        print("Invalid choice")
        return False


def handle_account_save_game(game_data: Dict[str, Any]) -> bool:
    """Handle saving game to account"""
    if not account_manager.is_logged_in():
        print("Error: Must be logged in to save to account")
        return False
    
    success, message = account_manager.save_account_game(game_data)
    print(message)
    return success


def handle_account_load_game() -> Optional[Dict[str, Any]]:
    """Handle loading game from account"""
    if not account_manager.is_logged_in():
        print("Error: Must be logged in to load from account")
        return None
    
    success, data = account_manager.load_account_game()
    if success:
        print("Game loaded from account")
        return data
    else:
        print(f"Error: {data.get('error', 'Failed to load')}")
        return None


def handle_account_menu() -> Optional[Dict[str, Any]]:
    """
    Main account menu handler for CLI integration
    
    Returns:
        Game data if loaded from account, None otherwise
    """
    loaded_game = None
    
    while True:
        show_account_menu()
        choice = input("Choice: ").strip()
        
        if account_manager.is_logged_in():
            # Logged in options
            if choice == "1":
                account_manager.logout()
                print("Logged out")
            elif choice == "2":
                print("Use this from the main game menu when quitting")
            elif choice == "3":
                loaded_game = handle_account_load_game()
                if loaded_game:
                    return loaded_game
            elif choice == "4":
                success, message = account_manager.delete_account_save()
                print(message)
            elif choice == "5":
                break
            else:
                print("Invalid choice")
        else:
            # Not logged in options
            if choice == "1":
                handle_login()
            elif choice == "2":
                handle_register()
            elif choice == "3":
                handle_recovery()
            elif choice == "4":
                break
            else:
                print("Invalid choice")
    
    return loaded_game


# For testing
if __name__ == "__main__":
    handle_account_menu()
