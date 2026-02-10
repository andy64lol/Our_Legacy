#!/usr/bin/env python3
"""
Chat CLI for Our Legacy
Uses Vercel serverless functions for messaging.
"""

import os
import sys
import time
import json
import requests
from datetime import datetime

# Configuration
PING_URL = "https://our-legacy.vercel.app/api/ping"
SEND_MESSAGE_URL = "https://our-legacy.vercel.app/api/send_message"
GLOBAL_CHAT_URL = "https://raw.githubusercontent.com/andy64lol/globalchat/refs/heads/main/global_chat.json"
ALIAS_FILE = "data/saves/username.txt"
COOLDOWN_SECONDS = 60  # 1 minute cooldown

class ChatClient:
    def __init__(self):
        self.alias = None
        self.last_message_time = 0
        self.messages = []
        self.check_alias()
    
    def check_alias(self):
        """Check if alias exists, if not create one."""
        if os.path.exists(ALIAS_FILE):
            with open(ALIAS_FILE, 'r') as f:
                self.alias = f.read().strip()
            print(f"Welcome back, {self.alias}!")
        else:
            self.create_alias()
    
    def create_alias(self):
        """Create a new alias and save it with restricted permissions."""
        print("Welcome to Our Legacy Chat!")
        print("Please create an alias (max 50 characters):")
        
        while True:
            alias = input("Alias: ").strip()
            
            if not alias:
                print("Alias cannot be empty. Please try again.")
                continue
            
            if len(alias) > 50:
                print("Alias too long (max 50 characters). Please try again.")
                continue
            
            # Check for valid characters
            if not all(c.isalnum() or c in '_-' for c in alias):
                print("Alias can only contain letters, numbers, underscores, and hyphens.")
                continue
            
            confirm = input(f"Use '{alias}' as your alias? (y/n): ").lower().strip()
            if confirm == 'y':
                self.alias = alias
                self.save_alias()
                break
            else:
                print("Let's try again.")
    
    def save_alias(self):
        """Save alias to file with chmod 444 and chattr +i."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(ALIAS_FILE), exist_ok=True)
            
            # Write alias to file
            if self.alias is None:
                raise ValueError("Alias cannot be None")
            with open(ALIAS_FILE, 'w') as f:
                f.write(self.alias)
            
            # Set read-only permissions (444 = r--r--r--)
            os.chmod(ALIAS_FILE, 0o444)
            
            # Try to make immutable (may require root on some systems)
            try:
                os.system(f'chattr +i "{ALIAS_FILE}" 2>/dev/null')
            except:
                pass  # chattr may not be available or may require root
            
            print(f"Alias '{self.alias}' saved successfully!")
            
        except Exception as e:
            print(f"Error saving alias: {e}")
            sys.exit(1)
    
    def check_connection(self):
        """Check if server is reachable."""
        try:
            response = requests.get(PING_URL, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def fetch_messages(self):
        """Fetch messages from global chat."""
        try:
            response = requests.get(GLOBAL_CHAT_URL, timeout=10)
            if response.status_code == 200:
                self.messages = response.json()
                return True
            return False
        except Exception as e:
            print(f"Error fetching messages: {e}")
            return False
    
    def display_messages(self, limit=20):
        """Display recent messages."""
        if not self.messages:
            print("No messages yet.")
            return
        
        print("\n" + "="*60)
        print("RECENT MESSAGES")
        print("="*60)
        
        recent = self.messages[-limit:] if len(self.messages) > limit else self.messages
        
        for msg in recent:
            author = msg.get('author', 'Unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')
            
            # Format timestamp
            if timestamp:
                try:
                    ts = int(timestamp) / 1000  # Convert from milliseconds if needed
                    time_str = datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                except:
                    time_str = str(timestamp)
            else:
                time_str = '??:??:??'
            
            print(f"[{time_str}] {author}: {content}")
        
        print("="*60 + "\n")
    
    def send_message(self, content):
        """Send a message to the server."""
        # Check cooldown
        current_time = time.time()
        time_since_last = current_time - self.last_message_time
        
        if time_since_last < COOLDOWN_SECONDS:
            remaining = COOLDOWN_SECONDS - int(time_since_last)
            print(f"Cooldown active. Please wait {remaining} seconds.")
            return False
        
        # Prepare message with alias prefix
        full_message = f"{self.alias}: {content}"
        
        try:
            payload = {
                "message": full_message,
                "author": self.alias
            }
            
            response = requests.post(
                SEND_MESSAGE_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                self.last_message_time = current_time
                print("Message sent successfully!")
                return True
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', f'HTTP {response.status_code}')
                print(f"Failed to send message: {error_msg}")
                return False
                
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def get_cooldown_status(self):
        """Get remaining cooldown time."""
        current_time = time.time()
        time_since_last = current_time - self.last_message_time
        
        if time_since_last < COOLDOWN_SECONDS:
            return COOLDOWN_SECONDS - int(time_since_last)
        return 0
    
    def run(self):
        """Main chat loop."""
        print("\n" + "="*60)
        print("OUR LEGACY CHAT")
        print("="*60)
        print(f"Alias: {self.alias}")
        print("Commands:")
        print("  /r     - Refresh messages")
        print("  /exit  - Quit chat")
        print("  /help  - Show help")
        print(f"Cooldown: {COOLDOWN_SECONDS} seconds between messages")
        print("="*60 + "\n")
        
        # Initial fetch
        if self.check_connection():
            print("Connected to server.")
            self.fetch_messages()
            self.display_messages()
        else:
            print("Warning: Cannot connect to server. Messages may not send.")
        
        while True:
            try:
                # Show prompt with cooldown indicator
                cooldown = self.get_cooldown_status()
                if cooldown > 0:
                    prompt = f"[CD:{cooldown}s] {self.alias}> "
                else:
                    prompt = f"{self.alias}> "
                
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input == '/r':
                    print("Refreshing messages...")
                    if self.fetch_messages():
                        self.display_messages()
                    else:
                        print("Failed to refresh messages.")
                    continue
                
                if user_input == '/exit':
                    print("Goodbye!")
                    break
                
                if user_input == '/help':
                    print("\nCommands:")
                    print("  /r     - Refresh messages from global chat")
                    print("  /exit  - Quit the chat")
                    print("  /help  - Show this help message")
                    print(f"\nCooldown: {COOLDOWN_SECONDS} seconds between messages")
                    print("Messages are sent with format: alias: message")
                    continue
                
                if user_input.startswith('/'):
                    print(f"Unknown command: {user_input}")
                    continue
                
                # Send message
                self.send_message(user_input)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break


def main():
    """Entry point."""
    chat = ChatClient()
    chat.run()


if __name__ == "__main__":
    main()
