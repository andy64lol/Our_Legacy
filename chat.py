#!/usr/bin/env python3
"""
Chat CLI for Our Legacy
Chat-like interface with clean message display and input separation.
"""

import os
import sys
import time
import json
import threading
import requests
import readline
import signal
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

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
CREATE_USER_URL = "https://our-legacy.vercel.app/api/create_user"
GLOBAL_CHAT_URL = "https://raw.githubusercontent.com/andy64lol/globalchat/refs/heads/main/global_chat.toml"
USERS_URL = "https://raw.githubusercontent.com/andy64lol/globalchat/refs/heads/main/users.json"
ALIAS_FILE = "data/saves/username.txt"
COOLDOWN_SECONDS = 20
AUTO_REFRESH_SECONDS = 10
BAN_CHECK_SECONDS = 90  # Check ban status every 90 seconds
MAX_MESSAGE_LENGTH = 300
MESSAGES_PER_PAGE = 10
MAX_FETCH_MESSAGES = 10  # Only fetch last 10 messages for performance

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
        self.last_message_count = 0  # Track displayed messages for incremental updates
        self.message_queue = []  # Queue for async message updates
        self.fetch_lock = threading.Lock()  # Lock for thread-safe fetching
        self.users_list: List[Dict] = []  # Cached users list
        self.is_banned = False  # Ban status
        self.last_ban_check = 0  # Last ban check time
        
        # Set up terminal resize handler (Unix/Linux only)
        try:
            signal.signal(signal.SIGWINCH, self._handle_resize)
        except (AttributeError, ValueError):
            # Windows doesn't have SIGWINCH, ignore
            pass
        
        # Load or create alias
        self.check_alias()
    
    def _handle_resize(self, signum, frame):
        """Handle terminal resize event."""
        self.terminal_width = get_terminal_width()
    
    def fetch_users(self) -> List[Dict]:
        """Fetch users list from repository."""
        try:
            response = requests.get(USERS_URL, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.users_list = data
                    return data
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}Error fetching users: {e}{Colors.RESET}")
        return []
    
    def check_alias_exists(self, alias: str) -> bool:
        """Check if alias already exists in users.json."""
        # Use the API endpoint for more reliable checking
        try:
            response = requests.get(
                f"{CREATE_USER_URL}?alias={quote(alias)}",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('exists', False)
        except Exception as e:
            print(f"{Colors.BRIGHT_YELLOW}Warning: Could not check alias availability online, falling back to local check{Colors.RESET}")
        
        # Fallback to local check
        users = self.fetch_users()
        for user in users:
            if isinstance(user, dict) and user.get('alias', '').lower() == alias.lower():
                return True
        return False
    
    def is_user_banned(self, alias: str) -> bool:
        """Check if user is banned."""
        users = self.fetch_users()
        for user in users:
            if isinstance(user, dict) and user.get('alias', '').lower() == alias.lower():
                return user.get('blacklisted', False)
        return False
    
    def check_alias(self):
        """Check if alias exists, if not create one."""
        if os.path.exists(ALIAS_FILE):
            try:
                with open(ALIAS_FILE, 'r') as f:
                    self.alias = f.read().strip()
                # Check if banned on startup
                if self.is_user_banned(self.alias):
                    print(f"{Colors.BRIGHT_RED}You are banned from the chat.{Colors.RESET}")
                    sys.exit(1)
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
        
        # Quick connection indicator (0.1s for responsiveness)
        print(f"{Colors.DIM}...{Colors.RESET}", flush=True)
        time.sleep(0.1)
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
                print(f"{Colors.BRIGHT_RED}Alias cannot be empty.{Colors.RESET}")
                continue
            
            if len(alias) > 20:
                print(f"{Colors.BRIGHT_RED}Alias too long (max 20 characters).{Colors.RESET}")
                continue
            
            if not all(c.isalnum() or c in '_- ' for c in alias):
                print(f"{Colors.BRIGHT_RED}Only letters, numbers, spaces, underscores, and hyphens.{Colors.RESET}")
                continue
            
            # Check if alias already exists
            if self.check_alias_exists(alias):
                print(f"{Colors.BRIGHT_RED}Username '{alias}' is already taken. Please choose another.{Colors.RESET}")
                continue
            
            # Show confirmation
            print(f"\n{Colors.BRIGHT_GREEN}You chose: {Colors.BRIGHT_CYAN}{alias}{Colors.RESET}")
            print(f"\n{Colors.DIM}Confirm this alias? (y/n): {Colors.RESET}", end='')
            
            confirm = input().lower().strip()
            
            if confirm == 'y':
                self.alias = alias
                self.save_alias()
                break
            else:
                print(f"{Colors.YELLOW}Let's try again.{Colors.RESET}")
                continue
    
    def register_user_online(self, alias: str) -> bool:
        """Register new user to GitHub repository via API."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                payload = {
                    "alias": alias,
                    "metadata": {
                        "permissions": "user"
                    }
                }
                
                response = requests.post(
                    CREATE_USER_URL,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )
                
                if response.status_code == 201:
                    return True
                elif response.status_code == 409:
                    # User already exists - this is actually fine for recovery
                    print(f"{Colors.BRIGHT_YELLOW}Note: Username already registered online{Colors.RESET}")
                    return True
                else:
                    error_msg = f"HTTP {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('error', error_msg)
                    except:
                        pass
                    print(f"{Colors.BRIGHT_YELLOW}Registration attempt {attempt + 1} failed: {error_msg}{Colors.RESET}")
                    
            except Exception as e:
                print(f"{Colors.BRIGHT_YELLOW}Registration attempt {attempt + 1} error: {e}{Colors.RESET}")
            
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait before retry
        
        return False

    def save_alias(self):
        """Save alias to file with enhanced confirmation and online registration."""
        try:
            if self.alias is None:
                return
            
            # First, register online (enforce username uniqueness)
            print(f"\n{Colors.DIM}Registering username online...{Colors.RESET}")
            online_success = self.register_user_online(self.alias)
            
            if not online_success:
                print(f"{Colors.BRIGHT_RED}Failed to register username online. Please try again later.{Colors.RESET}")
                # Don't exit - allow local-only mode for offline usage
                print(f"{Colors.BRIGHT_YELLOW}Continuing in local-only mode...{Colors.RESET}")
                time.sleep(1)
            
            os.makedirs(os.path.dirname(ALIAS_FILE), exist_ok=True)
            
            with open(ALIAS_FILE, 'w') as f:
                f.write(self.alias)
            
            # Set read-only permissions
            try:
                os.chmod(ALIAS_FILE, 0o444)
            except Exception:
                pass  # Permissions may not work on all systems
            
            # Try to make immutable (Linux only)
            try:
                if os.name != 'nt':  # chattr is Linux-specific
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
            if online_success:
                print_centered_text("Your identity is now secured and registered.", width, Colors.DIM)
            else:
                print_centered_text("Your identity is saved locally (offline mode).", width, Colors.BRIGHT_YELLOW)
            print(f"\n")
            print_centered_text("Entering chat...", width, Colors.DIM)
            
            # Minimal delay for user to read (0.1s)
            time.sleep(0.1)
            
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
    
    def parse_toml_messages(self, text: str) -> List[Dict]:
        """Parse TOML format messages to list of dicts."""
        messages = []
        blocks = text.split('[[messages]]')
        
        for block in blocks[1:]:  # Skip first empty element
            msg = {}
            lines = block.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Match key = "value" pattern
                match = __import__('re').match(r'^(\w+)\s*=\s*"([^"]*)"', line)
                if match:
                    msg[match.group(1)] = match.group(2)
            
            if msg.get('content') and msg.get('author'):
                messages.append(msg)
        
        return messages
    
    def fetch_messages(self) -> bool:
        """Fetch messages from global chat - optimized for incremental updates."""
        with self.fetch_lock:
            try:
                response = requests.get(GLOBAL_CHAT_URL, timeout=10)
                
                if response.status_code == 200:
                    text = response.text
                    all_messages = self.parse_toml_messages(text)
                    
                    # Only take last N messages for performance
                    if len(all_messages) > MAX_FETCH_MESSAGES:
                        all_messages = all_messages[-MAX_FETCH_MESSAGES:]
                    
                    # Normalize messages
                    normalized = []
                    for msg in all_messages:
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
                    
                    # Atomic update: check, update state, and queue in one operation
                    old_count = len(self.messages)
                    has_changes = normalized != self.messages
                    
                    if has_changes:
                        self.messages = normalized
                        self.last_refresh_time = time.time()
                        # Queue new messages for display
                        new_count = len(normalized)
                        if new_count > old_count:
                            # Only queue truly new messages
                            self.message_queue.extend(normalized[old_count:])
                        elif new_count < old_count:
                            # Messages were deleted/archived, clear queue and refresh all
                            self.message_queue = []
                    
                    return has_changes
                    
                return False
                
            except Exception as e:
                return False
    
    def display_new_messages(self):
        """Display only new messages from queue (incremental update)."""
        if not self.message_queue:
            return
        
        width = self.terminal_width
        
        while self.message_queue:
            msg = self.message_queue.pop(0)
            
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
                name_color = Colors.CHAT_NAME_SELF
                prefix = f"{Colors.DIM}[{time_str}]{Colors.RESET} {name_color}{author}{Colors.RESET}: "
            elif author == 'System' or author == 'Unknown':
                name_color = Colors.CHAT_NAME_SYSTEM
                prefix = f"{Colors.DIM}[{time_str}]{Colors.RESET} {name_color}*** {author}{Colors.RESET}: "
            else:
                name_color = Colors.CHAT_NAME_OTHER
                prefix = f"{Colors.DIM}[{time_str}]{Colors.RESET} {name_color}{author}{Colors.RESET}: "
            
            print(f"{prefix}{Colors.BRIGHT_WHITE}{content}{Colors.RESET}")
            print_chat_divider(width, Colors.DIM)
    
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
    
    def display_messages(self, show_header: bool = True, incremental: bool = False):
        """Display messages in a chat-like format with clean separation.
        
        Args:
            show_header: Whether to show header and clear screen
            incremental: If True, only display new messages from queue
        """
        # Handle incremental updates (no clear, just append)
        if incremental and not show_header:
            self.display_new_messages()
            return
        
        # Full refresh - only clear when explicitly requested for header mode
        # This reduces flickering significantly
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
            self.last_message_count = 0
            return
        
        # Always show last page (most recent messages)
        total_messages = len(self.messages)
        total_pages = max((total_messages + MESSAGES_PER_PAGE - 1) // MESSAGES_PER_PAGE, 1)
        self.current_page = min(self.current_page, total_pages - 1)  # Ensure valid page
        self.current_page = max(0, self.current_page)  # Ensure non-negative
        
        start_idx = self.current_page * MESSAGES_PER_PAGE
        end_idx = min(start_idx + MESSAGES_PER_PAGE, total_messages)
        
        # Ensure valid indices
        start_idx = max(0, min(start_idx, total_messages - 1)) if total_messages > 0 else 0
        end_idx = max(start_idx, min(end_idx, total_messages))
        
        # Display messages
        displayed_count = 0
        for idx in range(start_idx, end_idx):
            if idx >= len(self.messages):
                break
                
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
                prefix = f"{Colors.DIM}[{time_str}]{Colors.RESET} {name_color}{author}{Colors.RESET}: "
            elif author == 'System' or author == 'Unknown':
                # System message
                name_color = Colors.CHAT_NAME_SYSTEM
                prefix = f"{Colors.DIM}[{time_str}]{Colors.RESET} {name_color}*** {author}{Colors.RESET}: "
            else:
                # Other user's message
                name_color = Colors.CHAT_NAME_OTHER
                prefix = f"{Colors.DIM}[{time_str}]{Colors.RESET} {name_color}{author}{Colors.RESET}: "
            
            # Display message in list-like format
            print(f"{prefix}{Colors.BRIGHT_WHITE}{content}{Colors.RESET}")
            displayed_count += 1
            
            # Message separator (keeping the requested =================)
            if idx < end_idx - 1 and displayed_count < MESSAGES_PER_PAGE:
                print_chat_divider(width, Colors.DIM)
        
        # Update last message count
        self.last_message_count = total_messages
    
    def display_input_area(self):
        """Display the compact input area."""
        width = self.terminal_width
        
        # Print compact input area
        print()
        print_chat_divider(width, Colors.CHAT_STATUS)
    
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
    
    def ban_check_thread(self):
        """Background thread for checking ban status every 90 seconds."""
        while not self.is_exiting:
            current_time = time.time()
            if current_time - self.last_ban_check >= BAN_CHECK_SECONDS:
                try:
                    if self.alias and self.is_user_banned(self.alias):
                        self.is_banned = True
                        print(f"\n{Colors.BRIGHT_RED}You have been banned from the chat. Exiting...{Colors.RESET}")
                        self.is_exiting = True
                        break
                    self.last_ban_check = current_time
                except:
                    pass
            time.sleep(5)  # Check every 5 seconds if it's time to check ban
    
    def auto_refresh_thread(self):
        """Background thread for auto-refreshing messages - non-blocking."""
        while not self.is_exiting:
            if self.auto_refresh:
                current_time = time.time()
                if current_time - self.last_refresh_time >= AUTO_REFRESH_SECONDS:
                    try:
                        if self.fetch_messages():
                            # Queue new messages for display (don't block input)
                            # Main loop will display them on next iteration
                            pass
                    except:
                        pass
            # Shorter sleep for more responsive updates
            time.sleep(0.5)
    
    def run(self):
        """Main chat loop with enhanced initialization - optimized."""
        # Start with connection check
        if not self.check_connection():
            print(f"{Colors.BRIGHT_RED}Warning: Cannot connect to server. Some features may be limited.{Colors.RESET}")
            time.sleep(1)
        
        # Display initial messages
        self.fetch_messages()
        
        # Start background threads
        auto_refresh_thread = threading.Thread(target=self.auto_refresh_thread, daemon=True)
        ban_check_thread = threading.Thread(target=self.ban_check_thread, daemon=True)
        auto_refresh_thread.start()
        ban_check_thread.start()
        
        # Main loop
        while not self.is_exiting:
            try:
                # Display messages and input area
                self.display_messages(show_header=True)
                self.display_input_area()
                
                # Display prompt
                cooldown = self.get_cooldown_status()
                if cooldown > 0:
                    prompt = f"{Colors.BRIGHT_YELLOW}(Wait {cooldown}s) Enter message or /help: {Colors.RESET}"
                else:
                    prompt = f"{Colors.BRIGHT_GREEN}Enter message or /help: {Colors.RESET}"
                
                print(f"{prompt}", end='')
                sys.stdout.flush()
                
                # Get user input
                try:
                    user_input = input().strip()
                except EOFError:
                    # Handle Ctrl+D
                    print(f"\n{Colors.BRIGHT_CYAN}Goodbye!{Colors.RESET}")
                    break
                
                if not user_input:
                    # Just refresh display
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    cmd = user_input.lower().strip()
                    
                    if cmd == '/r' or cmd == '/refresh':
                        print(f"{Colors.DIM}Refreshing messages...{Colors.RESET}")
                        if self.fetch_messages():
                            self.display_messages(show_header=True)
                            self.display_input_area()
                        else:
                            print(f"{Colors.BRIGHT_YELLOW}No new messages{Colors.RESET}")
                        continue
                    
                    elif cmd == '/next' or cmd == '/n':
                        total_pages = max((len(self.messages) + MESSAGES_PER_PAGE - 1) // MESSAGES_PER_PAGE, 1)
                        if self.current_page < total_pages - 1:
                            self.current_page += 1
                        else:
                            print(f"{Colors.BRIGHT_YELLOW}Already at last page{Colors.RESET}")
                            time.sleep(0.5)
                        self.display_messages(show_header=True)
                        self.display_input_area()
                        continue
                    
                    elif cmd == '/prev' or cmd == '/p':
                        if self.current_page > 0:
                            self.current_page -= 1
                        else:
                            print(f"{Colors.BRIGHT_YELLOW}Already at first page{Colors.RESET}")
                            time.sleep(0.5)
                        self.display_messages(show_header=True)
                        self.display_input_area()
                        continue
                    
                    elif cmd == '/auto':
                        self.auto_refresh = not self.auto_refresh
                        status = "ON" if self.auto_refresh else "OFF"
                        color = Colors.BRIGHT_CYAN if self.auto_refresh else Colors.BRIGHT_YELLOW
                        print(f"{color}Auto-refresh: {status}{Colors.RESET}")
                        time.sleep(0.5)
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
                        time.sleep(1)
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
                        time.sleep(1)
                        continue
                
                # Send message
                if self.send_message(user_input):
                    # Auto-refresh after sending
                    time.sleep(0.5)  # Wait for server to update
                    self.fetch_messages()
                    # Display updated messages
                    self.display_messages(show_header=True)
                    self.display_input_area()
                else:
                    # Wait a moment for user to read error message
                    time.sleep(1)
                
            except KeyboardInterrupt:
                print(f"\n{Colors.BRIGHT_CYAN}Goodbye!{Colors.RESET}")
                self.is_exiting = True
                break
            except Exception as e:
                print(f"\n{Colors.BRIGHT_RED}Unexpected error: {e}{Colors.RESET}")
                time.sleep(1)
                continue
        
        # Cleanup
        self.is_exiting = True
        time.sleep(0.5)  # Give threads time to exit


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
