#!/usr/bin/env python3
"""
Chat CLI for Our Legacy
Chat-like interface with clean message display and input separation.
"""

import os
import sys
import time
import json
import socket
import threading
import requests
import readline
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ANSI Color Codes with enhanced styling
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright foreground colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Chat-specific colors
    CHAT_NAME_SELF = BRIGHT_GREEN + BOLD
    CHAT_NAME_OTHER = BRIGHT_CYAN
    CHAT_NAME_SYSTEM = BRIGHT_YELLOW
    CHAT_TIMESTAMP = DIM + WHITE
    CHAT_STATUS = BRIGHT_MAGENTA
    CHAT_DIVIDER = BRIGHT_BLUE
    CHAT_WELCOME = BRIGHT_CYAN + BOLD
    CHAT_INPUT = BRIGHT_WHITE
    CHAT_PROMPT = BRIGHT_GREEN


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_terminal_width():
    """Get terminal width, default to 80 if cannot determine."""
    try:
        return os.get_terminal_size().columns
    except:
        return 80

def print_wide_divider(width: Optional[int] = None, color: str = Colors.CHAT_DIVIDER):
    """Print a wide divider line with =============."""
    if width is None:
        width = get_terminal_width()
    divider_length = 12  # Fixed length for =============
    if width < divider_length:
        divider_length = width
    
    # Center the divider
    padding = (width - divider_length) // 2
    padding = max(padding, 0)
    print(f"{color}{' ' * padding}{'=' * divider_length}{Colors.RESET}")

def print_centered_text(text: str, width: Optional[int] = None, color: str = Colors.RESET):
    """Print centered text with wide dividers above and below."""
    if width is None:
        width = get_terminal_width()
    
    # Calculate padding for centering
    padding = (width - len(text)) // 2
    padding = max(padding, 0)
    
    # Print with wide dividers
    print_wide_divider(width, Colors.CHAT_DIVIDER)
    print(f"{color}{' ' * padding}{text}{Colors.RESET}")
    print_wide_divider(width, Colors.CHAT_DIVIDER)

def print_section_header(title: str, width: Optional[int] = None, color: str = Colors.CHAT_STATUS):
    """Print a section header with centered title and wide dividers."""
    if width is None:
        width = get_terminal_width()
    
    print_wide_divider(width, color)
    
    # Center the title
    padding = (width - len(title)) // 2
    padding = max(padding, 0)
    print(f"{color}{' ' * padding}{title}{Colors.RESET}")
    
    print_wide_divider(width, color)

def print_chat_divider(width: Optional[int] = None, color: str = Colors.DIM):
    """Print a chat message divider."""
    if width is None:
        width = get_terminal_width()
    print(f"{color}{'=' * width}{Colors.RESET}")

# Configuration
PING_URL = "https://our-legacy.vercel.app/api/ping"
SEND_MESSAGE_URL = "https://our-legacy.vercel.app/api/send_message"
GLOBAL_CHAT_URL = "https://raw.githubusercontent.com/andy64lol/globalchat/refs/heads/main/global_chat.json"
ALIAS_FILE = "data/saves/username.txt"
COOLDOWN_SECONDS = 60
AUTO_REFRESH_SECONDS = 30
MAX_MESSAGE_LENGTH = 300
MESSAGES_PER_PAGE = 15

class EnhancedChatClient:
    def __init__(self):
        self.alias = None
        self.last_message_time = 0
        self.messages: List[Dict] = []
        self.current_page = 0
        self.auto_refresh = True
        self.connection_ok = False
        self.last_refresh_time = 0
        self.is_exiting = False
        self.terminal_width = get_terminal_width()
        
        # Load or create alias
        self.check_alias()
    
    def check_alias(self):
        """Check if alias exists, if not create one."""
        if os.path.exists(ALIAS_FILE):
            try:
                with open(ALIAS_FILE, 'r') as f:
                    self.alias = f.read().strip()
                self.show_welcome_back()
            except Exception as e:
                print(f"{Colors.BRIGHT_RED}Error loading alias: {e}{Colors.RESET}")
                self.create_alias()
        else:
            self.create_alias()
    
    def show_welcome_back(self):
        """Show enhanced welcome back message."""
        clear_screen()
        width = self.terminal_width
        
        print(f"\n\n")
        print_centered_text("OUR LEGACY CHAT", width, Colors.CHAT_WELCOME)
        print(f"\n")
        print_centered_text(f"Welcome back, {self.alias}!", width, Colors.BRIGHT_GREEN)
        print(f"\n")
        print_centered_text("Connecting to chat server...", width, Colors.DIM)
        
        # Simulate connection animation
        for _ in range(3):
            time.sleep(0.3)
            print(f"{Colors.DIM}.{Colors.RESET}", end='', flush=True)
        print()
        
        time.sleep(1)
        clear_screen()
    
    def create_alias(self):
        """Create a new alias with enhanced UI."""
        clear_screen()
        width = self.terminal_width
        
        print(f"\n\n")
        print_centered_text("OUR LEGACY CHAT", width, Colors.CHAT_WELCOME)
        print(f"\n")
        print_centered_text("Create Your Chat Identity", width, Colors.BRIGHT_WHITE)
        print(f"\n")
        print_wide_divider(width, Colors.DIM)
        
        while True:
            print(f"\n{Colors.BRIGHT_GREEN}Enter your chat alias (max 20 characters):{Colors.RESET}")
            print(f"{Colors.DIM}Allowed: letters, numbers, spaces, underscores, hyphens{Colors.RESET}")
            print(f"\n{Colors.BRIGHT_CYAN}Alias: {Colors.RESET}", end='')
            
            alias = input().strip()
            
            if not alias:
                self.clear_input_line(4)
                print(f"{Colors.BRIGHT_RED}Alias cannot be empty.{Colors.RESET}")
                continue
            
            if len(alias) > 20:
                self.clear_input_line(4)
                print(f"{Colors.BRIGHT_RED}Alias too long (max 20 characters).{Colors.RESET}")
                continue
            
            if not all(c.isalnum() or c in '_- ' for c in alias):
                self.clear_input_line(4)
                print(f"{Colors.BRIGHT_RED}Only letters, numbers, spaces, underscores, and hyphens.{Colors.RESET}")
                continue
            
            # Show confirmation
            self.clear_input_line(4)
            print(f"\n{Colors.BRIGHT_GREEN}You chose: {Colors.BRIGHT_CYAN}{alias}{Colors.RESET}")
            print(f"\n{Colors.DIM}Confirm this alias? (y/n): {Colors.RESET}", end='')
            
            confirm = input().lower().strip()
            
            if confirm == 'y':
                self.alias = alias
                self.save_alias()
                break
            else:
                self.clear_input_line(6)
                print(f"{Colors.YELLOW}Let's try again.{Colors.RESET}")
                continue
    
    def clear_input_line(self, lines: int = 1):
        """Clear the last line(s) of input."""
        for _ in range(lines):
            sys.stdout.write('\033[F')  # Move cursor up one line
            sys.stdout.write('\033[K')  # Clear line
    
    def save_alias(self):
        """Save alias to file with enhanced confirmation."""
        try:
            if self.alias is None:
                return
            
            os.makedirs(os.path.dirname(ALIAS_FILE), exist_ok=True)
            
            with open(ALIAS_FILE, 'w') as f:
                f.write(self.alias)
            
            # Set read-only permissions
            os.chmod(ALIAS_FILE, 0o444)
            
            # Try to make immutable
            try:
                os.system(f'chattr +i "{ALIAS_FILE}" 2>/dev/null')
            except:
                pass
            
            # Enhanced success message
            clear_screen()
            width = self.terminal_width
            
            print(f"\n\n")
            print_centered_text("ALIAS CREATED", width, Colors.BRIGHT_GREEN)
            print(f"\n")
            print_centered_text(f"Welcome, {self.alias}!", width, Colors.BRIGHT_CYAN)
            print(f"\n")
            print_centered_text("Your identity is now secured.", width, Colors.DIM)
            print(f"\n")
            print_centered_text("Entering chat...", width, Colors.DIM)
            
            time.sleep(2)
            
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}Error saving alias: {e}{Colors.RESET}")
            sys.exit(1)
    
    def check_connection(self) -> bool:
        """Check if server is reachable."""
        try:
            response = requests.get(PING_URL, timeout=5)
            self.connection_ok = response.status_code == 200
            return self.connection_ok
        except:
            self.connection_ok = False
            return False
    
    def fetch_messages(self) -> bool:
        """Fetch messages from global chat."""
        try:
            response = requests.get(GLOBAL_CHAT_URL, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle different JSON structures
                if isinstance(data, dict):
                    new_messages = data.get('messages', [])
                elif isinstance(data, list):
                    new_messages = data
                else:
                    new_messages = []
                
                # Normalize messages
                normalized = []
                for msg in new_messages:
                    if isinstance(msg, dict):
                        normalized.append(msg)
                    elif isinstance(msg, str):
                        try:
                            parsed = json.loads(msg)
                            if isinstance(parsed, dict):
                                normalized.append(parsed)
                            else:
                                normalized.append({
                                    'author': 'System',
                                    'content': str(parsed),
                                    'timestamp': int(time.time() * 1000)
                                })
                        except:
                            normalized.append({
                                'author': 'System',
                                'content': msg,
                                'timestamp': int(time.time() * 1000)
                            })
                
                # Update messages if changed
                if normalized != self.messages:
                    self.messages = normalized
                    self.last_refresh_time = time.time()
                    return True
                return False
                
            return False
            
        except Exception as e:
            return False
    
    def format_timestamp(self, timestamp_ms: int) -> str:
        """Format timestamp for display."""
        try:
            dt = datetime.fromtimestamp(timestamp_ms / 1000)
            now = datetime.now()
            
            if dt.date() == now.date():
                return dt.strftime("%H:%M:%S")
            elif (now.date() - dt.date()).days == 1:
                return f"Yesterday {dt.strftime('%H:%M')}"
            else:
                return dt.strftime("%m/%d %H:%M")
        except:
            return "??:??"
    
    def display_messages(self, show_header: bool = True):
        """Display messages in a chat-like format with clean separation."""
        if show_header:
            clear_screen()
        width = self.terminal_width
        
        # Header with connection status
        if show_header:
            status_icon = f"{Colors.BRIGHT_GREEN}●{Colors.RESET}" if self.connection_ok else f"{Colors.BRIGHT_RED}●{Colors.RESET}"
            status_text = f"OUR LEGACY CHAT {status_icon}"
            
            print_section_header(status_text, width, Colors.CHAT_STATUS)
            print(f"{Colors.DIM}Connected as: {self.alias}{Colors.RESET}")
            print_chat_divider(width, Colors.CHAT_STATUS)
        
        if not self.messages:
            print(f"\n{Colors.DIM}No messages yet. Be the first to say something!{Colors.RESET}\n")
            return
        
        # Calculate pagination
        total_messages = len(self.messages)
        total_pages = max((total_messages + MESSAGES_PER_PAGE - 1) // MESSAGES_PER_PAGE, 1)
        
        if self.current_page < 0:
            self.current_page = 0
        if self.current_page >= total_pages:
            self.current_page = total_pages - 1
        
        start_idx = self.current_page * MESSAGES_PER_PAGE
        end_idx = min(start_idx + MESSAGES_PER_PAGE, total_messages)
        
        # Display messages
        for idx in range(start_idx, end_idx):
            msg = self.messages[idx]
            
            if isinstance(msg, dict):
                author = msg.get('author', 'Unknown')
                content = msg.get('content', '')
                timestamp = msg.get('timestamp', int(time.time() * 1000))
            else:
                author = 'Unknown'
                content = str(msg)
                timestamp = int(time.time() * 1000)
            
            # Format timestamp
            time_str = self.format_timestamp(timestamp)
            
            # Determine message style
            if author == self.alias:
                # Own message
                name_color = Colors.CHAT_NAME_SELF
                align = "right"
                prefix = ">>> "
            elif author == 'System' or author == 'Unknown':
                # System message
                name_color = Colors.CHAT_NAME_SYSTEM
                align = "center"
                prefix = "*** "
            else:
                # Other user's message
                name_color = Colors.CHAT_NAME_OTHER
                align = "left"
                prefix = ""
            
            # Display message
            print(f"{Colors.CHAT_TIMESTAMP}{time_str:>8}{Colors.RESET} ", end='')
            
            if align == "right":
                # Right aligned (own message)
                print(f"{name_color}{author:<15}{Colors.RESET} {Colors.BRIGHT_WHITE}{prefix}{content}{Colors.RESET}")
            elif align == "center":
                # Center aligned (system message)
                print(f"{name_color}{prefix}{author}: {content}{Colors.RESET}")
            else:
                # Left aligned (other's message)
                print(f"{Colors.BRIGHT_WHITE}{prefix}{content}{Colors.RESET} {name_color}{author:>15}{Colors.RESET}")
            
            # Message separator
            if idx < end_idx - 1:
                print_chat_divider(width, Colors.DIM)
    
    def display_input_area(self):
        """Display the input area with status information."""
        width = self.terminal_width
        cooldown = self.get_cooldown_status()
        
        # Print input area divider
        print()
        print_chat_divider(width, Colors.CHAT_STATUS)
        print()
        
        # Status information
        status_parts = []
        
        if cooldown > 0:
            status_parts.append(f"{Colors.BRIGHT_RED}Cooldown: {cooldown}s{Colors.RESET}")
        else:
            status_parts.append(f"{Colors.BRIGHT_GREEN}Ready to send{Colors.RESET}")
        
        if self.auto_refresh:
            status_parts.append(f"{Colors.BRIGHT_CYAN}Auto-refresh: ON{Colors.RESET}")
        else:
            status_parts.append(f"{Colors.BRIGHT_YELLOW}Auto-refresh: OFF{Colors.RESET}")
        
        # Calculate pagination info
        total_messages = len(self.messages)
        total_pages = max((total_messages + MESSAGES_PER_PAGE - 1) // MESSAGES_PER_PAGE, 1)
        
        if total_pages > 1:
            status_parts.append(f"{Colors.DIM}Page {self.current_page + 1}/{total_pages}{Colors.RESET}")
        
        # Print status line
        status_line = " | ".join(status_parts)
        padding = (width - len(status_line)) // 2
        padding = max(padding, 0)
        print(f"{' ' * padding}{status_line}")
        print()
    
    def get_cooldown_status(self) -> int:
        """Get remaining cooldown time."""
        current_time = time.time()
        time_since_last = current_time - self.last_message_time
        
        if time_since_last < COOLDOWN_SECONDS:
            return COOLDOWN_SECONDS - int(time_since_last)
        return 0
    
    def send_message(self, content: str) -> bool:
        """Send a message to the server."""
        # Check cooldown
        cooldown = self.get_cooldown_status()
        if cooldown > 0:
            print(f"{Colors.BRIGHT_YELLOW}Please wait {cooldown} seconds before sending another message.{Colors.RESET}")
            return False
        
        # Check message length
        if len(content) > MAX_MESSAGE_LENGTH:
            print(f"{Colors.BRIGHT_RED}Message too long (max {MAX_MESSAGE_LENGTH} characters).{Colors.RESET}")
            return False
        
        if not content.strip():
            print(f"{Colors.BRIGHT_YELLOW}Message cannot be empty.{Colors.RESET}")
            return False
        
        # Show sending indicator
        width = self.terminal_width
        print(f"{Colors.DIM}Sending message...{Colors.RESET}")
        
        try:
            payload = {
                "message": content,
                "author": self.alias
            }
            
            response = requests.post(
                SEND_MESSAGE_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                self.last_message_time = time.time()
                print(f"{Colors.BRIGHT_GREEN}Message sent successfully!{Colors.RESET}")
                time.sleep(0.5)
                return True
            else:
                error_msg = f"HTTP {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('error', error_msg)
                    except:
                        pass
                print(f"{Colors.BRIGHT_RED}Failed to send: {error_msg}{Colors.RESET}")
                return False
                
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}")
            return False
    
    def show_help(self):
        """Show help information with wide dividers."""
        clear_screen()
        width = self.terminal_width
        
        print(f"\n")
        print_centered_text("CHAT COMMANDS HELP", width, Colors.BRIGHT_CYAN)
        
        print(f"\n{Colors.BRIGHT_WHITE}Basic Commands:{Colors.RESET}")
        print_chat_divider(width, Colors.DIM)
        print(f"  {Colors.BRIGHT_GREEN}/r{Colors.RESET}           - {Colors.DIM}Refresh messages{Colors.RESET}")
        print(f"  {Colors.BRIGHT_GREEN}/next{Colors.RESET}       - {Colors.DIM}Next page{Colors.RESET}")
        print(f"  {Colors.BRIGHT_GREEN}/prev{Colors.RESET}       - {Colors.DIM}Previous page{Colors.RESET}")
        print(f"  {Colors.BRIGHT_GREEN}/auto{Colors.RESET}       - {Colors.DIM}Toggle auto-refresh{Colors.RESET}")
        print(f"  {Colors.BRIGHT_GREEN}/clear{Colors.RESET}      - {Colors.DIM}Clear screen{Colors.RESET}")
        print(f"  {Colors.BRIGHT_GREEN}/status{Colors.RESET}     - {Colors.DIM}Show connection status{Colors.RESET}")
        print(f"  {Colors.BRIGHT_GREEN}/exit{Colors.RESET}      - {Colors.DIM}Quit chat{Colors.RESET}")
        print(f"  {Colors.BRIGHT_GREEN}/help{Colors.RESET}       - {Colors.DIM}Show this help{Colors.RESET}")
        
        print(f"\n{Colors.BRIGHT_YELLOW}Message Format:{Colors.RESET}")
        print_chat_divider(width, Colors.DIM)
        print(f"  {Colors.CHAT_NAME_OTHER}Other users{Colors.RESET} - Messages from others")
        print(f"  {Colors.CHAT_NAME_SELF}You{Colors.RESET}        - Your messages (with >>> prefix)")
        print(f"  {Colors.CHAT_NAME_SYSTEM}System{Colors.RESET}     - System notifications")
        
        print(f"\n{Colors.BRIGHT_MAGENTA}Tips:{Colors.RESET}")
        print_chat_divider(width, Colors.DIM)
        print(f"  {Colors.DIM}• Press Ctrl+C to exit anytime{Colors.RESET}")
        print(f"  {Colors.DIM}• Use ↑/↓ arrow keys for message history{Colors.RESET}")
        print(f"  {Colors.DIM}• Cooldown: {COOLDOWN_SECONDS} seconds between messages{Colors.RESET}")
        print(f"  {Colors.DIM}• Auto-refresh: {AUTO_REFRESH_SECONDS}s interval{Colors.RESET}")
        print(f"  {Colors.DIM}• Max message length: {MAX_MESSAGE_LENGTH} characters{Colors.RESET}")
        
        print(f"\n{Colors.DIM}Press Enter to return to chat...{Colors.RESET}")
        input()
    
    def auto_refresh_thread(self):
        """Background thread for auto-refreshing messages."""
        while not self.is_exiting:
            if self.auto_refresh:
                current_time = time.time()
                if current_time - self.last_refresh_time >= AUTO_REFRESH_SECONDS:
                    try:
                        if self.fetch_messages():
                            # Only redisplay if not in input
                            self.display_messages(show_header=True)
                            self.display_input_area()
                    except:
                        pass
            time.sleep(1)
    
    def run(self):
        """Main chat loop with enhanced initialization."""
        # Start with connection check
        width = self.terminal_width
        
        print(f"\n")
        print_centered_text("INITIALIZING CHAT CLIENT", width, Colors.CHAT_WELCOME)
        print(f"\n{Colors.DIM}Checking connection to server...{Colors.RESET}")
        
        if self.check_connection():
            print(f"{Colors.BRIGHT_GREEN}✓ Connected to server{Colors.RESET}")
        else:
            print(f"{Colors.BRIGHT_YELLOW}⚠ Limited connectivity - messages may not send{Colors.RESET}")
        
        time.sleep(1)
        
        # Start auto-refresh thread
        refresh_thread = threading.Thread(target=self.auto_refresh_thread, daemon=True)
        refresh_thread.start()
        
        # Initial message fetch
        print(f"\n{Colors.DIM}Loading messages...{Colors.RESET}")
        self.fetch_messages()
        
        time.sleep(0.5)
        self.display_messages(show_header=True)
        self.display_input_area()
        
        # Chat history for readline
        message_history = []
        
        while not self.is_exiting:
            try:
                # Show input prompt
                cooldown = self.get_cooldown_status()
                
                if cooldown > 0:
                    prompt = f"{Colors.BRIGHT_RED}[CD:{cooldown:02d}s]{Colors.RESET} {Colors.CHAT_PROMPT}{self.alias}>{Colors.RESET} "
                elif not self.connection_ok:
                    prompt = f"{Colors.BRIGHT_YELLOW}[OFFLINE]{Colors.RESET} {Colors.CHAT_PROMPT}{self.alias}>{Colors.RESET} "
                else:
                    prompt = f"{Colors.CHAT_PROMPT}{self.alias}>{Colors.RESET} "
                
                # Get user input
                try:
                    user_input = input(prompt).strip()
                except (KeyboardInterrupt, EOFError):
                    print(f"\n{Colors.BRIGHT_CYAN}Goodbye!{Colors.RESET}")
                    self.is_exiting = True
                    break
                
                if not user_input:
                    continue
                
                # Add to history
                if user_input and (not message_history or message_history[-1] != user_input):
                    message_history.append(user_input)
                
                # Handle commands
                if user_input.startswith('/'):
                    cmd = user_input.lower()
                    
                    if cmd == '/r' or cmd == '/refresh':
                        print(f"{Colors.DIM}Refreshing messages...{Colors.RESET}")
                        if self.fetch_messages():
                            self.display_messages(show_header=True)
                            self.display_input_area()
                        else:
                            print(f"{Colors.BRIGHT_YELLOW}No new messages{Colors.RESET}")
                        continue
                    
                    elif cmd == '/next' or cmd == '/n':
                        self.current_page += 1
                        self.display_messages(show_header=True)
                        self.display_input_area()
                        continue
                    
                    elif cmd == '/prev' or cmd == '/p':
                        self.current_page -= 1
                        if self.current_page < 0:
                            self.current_page = 0
                            print(f"{Colors.BRIGHT_YELLOW}Already at first page{Colors.RESET}")
                        self.display_messages(show_header=True)
                        self.display_input_area()
                        continue
                    
                    elif cmd == '/auto':
                        self.auto_refresh = not self.auto_refresh
                        status = "ON" if self.auto_refresh else "OFF"
                        color = Colors.BRIGHT_CYAN if self.auto_refresh else Colors.BRIGHT_YELLOW
                        print(f"{color}Auto-refresh: {status}{Colors.RESET}")
                        continue
                    
                    elif cmd == '/clear' or cmd == '/c':
                        clear_screen()
                        self.display_messages(show_header=True)
                        self.display_input_area()
                        continue
                    
                    elif cmd == '/status' or cmd == '/s':
                        if self.check_connection():
                            print(f"{Colors.BRIGHT_GREEN}✓ Connected to server{Colors.RESET}")
                        else:
                            print(f"{Colors.BRIGHT_RED}✗ Cannot connect to server{Colors.RESET}")
                        continue
                    
                    elif cmd == '/exit' or cmd == '/quit' or cmd == '/q':
                        print(f"\n{Colors.BRIGHT_CYAN}Goodbye!{Colors.RESET}")
                        self.is_exiting = True
                        break
                    
                    elif cmd == '/help' or cmd == '/h':
                        self.show_help()
                        self.display_messages(show_header=True)
                        self.display_input_area()
                        continue
                    
                    else:
                        print(f"{Colors.BRIGHT_RED}Unknown command: {user_input}{Colors.RESET}")
                        print(f"{Colors.DIM}Type /help for available commands{Colors.RESET}")
                        continue
                
                # Send message
                if self.send_message(user_input):
                    # Refresh messages after sending
                    time.sleep(1)  # Small delay for server to process
                    self.fetch_messages()
                    self.display_messages(show_header=True)
                    self.display_input_area()
                
            except KeyboardInterrupt:
                print(f"\n{Colors.BRIGHT_CYAN}Goodbye!{Colors.RESET}")
                self.is_exiting = True
                break
            except Exception as e:
                print(f"\n{Colors.BRIGHT_RED}Unexpected error: {e}{Colors.RESET}")
                continue
        
        # Cleanup
        self.is_exiting = True


def main():
    """Entry point."""
    chat = EnhancedChatClient()
    
    try:
        chat.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.BRIGHT_CYAN}Goodbye!{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.BRIGHT_RED}Fatal error: {e}{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
