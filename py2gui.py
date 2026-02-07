"""
Py2GUI - Enhanced Python Terminal-style GUI
Fixed version: Fixed potential errors and issues
"""
import tkinter as tk
from tkinter import scrolledtext, simpledialog, Menu, Frame, Entry, Button, StringVar, font
import queue
import threading
import traceback
import re
import json
import os
import sys
from typing import Callable, Any, Optional, List, Tuple, Dict, Set
import warnings


class Py2GUI:
    def __init__(self, title: str = "Py2GUI", width: int = 80, height: int = 20, config_file: str = "config.json"):
        """Initialize Py2GUI instance"""
        self.root = tk.Tk()
        self.root.title(title)
        self.root.resizable(True, True)
        self.width = width
        self.height = height
        self.running = True
        self.config_file = config_file
        
        # Load configuration
        self.config = self._load_config()
        
        # Extended ANSI color configuration
        self.ansi_colors = {
            # Basic colors
            '30': '#000000',        # Black
            '31': '#ff0000',        # Red
            '32': '#00ff00',        # Green
            '33': '#ffff00',        # Yellow
            '34': '#0000ff',        # Blue
            '35': '#ff00ff',        # Magenta
            '36': '#00ffff',        # Cyan
            '37': '#ffffff',        # White
            
            # Bright colors
            '90': '#808080',        # Gray
            '91': '#ff8080',        # Bright red
            '92': '#80ff80',        # Bright green
            '93': '#ffff80',        # Bright yellow
            '94': '#8080ff',        # Bright blue
            '95': '#ff80ff',        # Bright magenta
            '96': '#80ffff',        # Bright cyan
            '97': '#ffffff',        # Bright white
            
            # Background colors
            '40': '#1a1a1a',        # Black background
            '41': '#ff0000',        # Red background
            '42': '#00ff00',        # Green background
            '43': '#ffff00',        # Yellow background
            '44': '#0000ff',        # Blue background
            '45': '#ff00ff',        # Magenta background
            '46': '#00ffff',        # Cyan background
            '47': '#ffffff',        # White background
            
            # Extended 256 colors
            '38;5;0': '#000000',    # Black
            '38;5;1': '#800000',    # Dark red
            '38;5;2': '#008000',    # Dark green
            '38;5;3': '#808000',    # Dark yellow
            '38;5;4': '#000080',    # Dark blue
            '38;5;5': '#800080',    # Dark magenta
            '38;5;6': '#008080',    # Dark cyan
            '38;5;7': '#c0c0c0',    # Light gray
            '38;5;8': '#808080',    # Dark gray
            '38;5;9': '#ff0000',    # Red
            '38;5;10': '#00ff00',   # Green
            '38;5;11': '#ffff00',   # Yellow
            '38;5;12': '#0000ff',   # Blue
            '38;5;13': '#ff00ff',   # Magenta
            '38;5;14': '#00ffff',   # Cyan
            '38;5;15': '#ffffff',   # White
            
            # Extended background colors
            '48;5;0': '#000000',    # Black background
            '48;5;1': '#800000',    # Dark red background
            '48;5;2': '#008000',    # Dark green background
            '48;5;3': '#808000',    # Dark yellow background
            '48;5;4': '#000080',    # Dark blue background
            '48;5;5': '#800080',    # Dark magenta background
            '48;5;6': '#008080',    # Dark cyan background
            '48;5;7': '#c0c0c0',    # Light gray background
            
            # True Color support
            '38;2;0;0;0': '#000000',    # Black
            '38;2;255;0;0': '#ff0000',  # Red
            '38;2;0;255;0': '#00ff00',  # Green
            '38;2;0;0;255': '#0000ff',  # Blue
        }
        
        # Color name to hex mapping
        self.color_name_to_hex = {
            'black': '#000000',
            'red': '#ff0000',
            'green': '#00ff00',
            'yellow': '#ffff00',
            'blue': '#0000ff',
            'magenta': '#ff00ff',
            'cyan': '#00ffff',
            'white': '#ffffff',
            'gray': '#808080',
            'bright red': '#ff8080',
            'bright green': '#80ff80',
            'bright yellow': '#ffff80',
            'bright blue': '#8080ff',
            'bright magenta': '#ff80ff',
            'bright cyan': '#80ffff',
            'bright white': '#ffffff',
            'orange': '#ff8000',
            'purple': '#8000ff',
            'pink': '#ff80ff',
            'brown': '#804000',
            'dark gray': '#404040',
            'light gray': '#c0c0c0',
        }
        
        # Available fonts
        try:
            self.available_fonts = font.families()
        except Exception:
            self.available_fonts = ["Courier", "Consolas", "Monaco", "Menlo"]
            warnings.warn(f"Could not load font families, using fallback fonts: {self.available_fonts}")
        
        # Current text style state
        self.current_style = {
            'font': ('Courier', 10, 'normal'),
            'foreground': 'white',
            'background': 'black',
            'underline': False,
            'strikethrough': False
        }
        
        # Defined text tags
        self.tag_names: Set[str] = set()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        
        # Main frame
        self.main_frame = Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Output area
        self.text_area = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            width=width,
            height=height,
            font=("Courier", 10),
            bg="black",
            fg="white",
            insertbackground="white"
        )
        self.text_area.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.text_area.config(state=tk.DISABLED)
        
        # Configure default tag
        self.text_area.tag_configure("default", 
            font=("Courier", 10, "normal"),
            foreground="white",
            background="black"
        )
        
        # Configure color tags
        for code, color_hex in self.ansi_colors.items():
            # Skip disabled colors
            if 'disabled_colors' in self.config and code in self.config['disabled_colors']:
                continue
                
            tag_name = f"ansi_{code}"
            if (code.startswith('3') and ';' not in code) or code.startswith('38'):
                # Foreground color
                self.text_area.tag_configure(tag_name, foreground=color_hex)
            elif code.startswith('4') or code.startswith('48'):
                # Background color
                self.text_area.tag_configure(tag_name, background=color_hex)
            self.tag_names.add(tag_name)
        
        # Configure style tags
        self.text_area.tag_configure("bold", font=("Courier", 10, "bold"))
        self.text_area.tag_configure("italic", font=("Courier", 10, "italic"))
        self.text_area.tag_configure("underline", underline=True)
        self.text_area.tag_configure("strikethrough", overstrike=True)
        self.text_area.tag_configure("reverse", foreground="black", background="white")
        
        # Add style tags to tag set
        for tag in ["bold", "italic", "underline", "strikethrough", "reverse"]:
            self.tag_names.add(tag)
        
        # Terminal style input area frame
        self.input_frame = Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Input label
        self.input_label = tk.Label(self.input_frame, text=">> ", font=("Courier", 10), fg="white", bg="black")
        self.input_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Terminal style input field
        self.input_var = StringVar()
        self.input_entry = Entry(
            self.input_frame,
            textvariable=self.input_var,
            font=("Courier", 10),
            bg="black",
            fg="white",
            insertbackground="white"
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Send button
        self.send_button = Button(
            self.input_frame,
            text="Send",
            command=self._on_send_input,
            font=("Courier", 9)
        )
        self.send_button.pack(side=tk.LEFT)
        
        # Input queues
        self.input_queue = queue.Queue()
        self.type_in_queue = queue.Queue()
        
        # Bind Enter key
        self.input_entry.bind('<Return>', self._on_enter_pressed)
        
        # Create menus
        self._setup_menus()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        default_config = {
            "disabled_menus": [],
            "disabled_views": [],
            "disabled_colors": [],
            "show_clear_button": True,
            "show_demo_button": True
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with default config
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
        except (json.JSONDecodeError, IOError, OSError) as e:
            self._safe_print(f"Error loading config file: {e}")
        except Exception as e:
            self._safe_print(f"Unexpected error loading config: {e}")
        
        return default_config
    
    def _safe_print(self, message: str) -> None:
        """Safely print message (for initialization and error handling)"""
        try:
            print(message, file=sys.stderr)
        except Exception:
            pass  # Ignore print errors
    
    def _setup_menus(self) -> None:
        """Set up menu system"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        if 'disabled_menus' not in self.config or 'File' not in self.config['disabled_menus']:
            file_menu = Menu(menubar, tearoff=0)
            menubar.add_cascade(label="File", menu=file_menu)
            file_menu.add_command(label="Exit", command=self.exit)
        
        # Edit menu
        if 'disabled_menus' not in self.config or 'Edit' not in self.config['disabled_menus']:
            edit_menu = Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Edit", menu=edit_menu)
            edit_menu.add_command(label="Copy", command=self.copy_text)
            edit_menu.add_command(label="Select All", command=self.select_all)
        
        # View menu
        if 'disabled_menus' not in self.config or 'View' not in self.config['disabled_menus']:
            view_menu = Menu(menubar, tearoff=0)
            menubar.add_cascade(label="View", menu=view_menu)
            
            if 'disabled_views' not in self.config or 'Focus Input' not in self.config['disabled_views']:
                view_menu.add_command(label="Focus Input", command=self.focus_input)
            
            if 'disabled_views' not in self.config or 'Clear Output' not in self.config['disabled_views']:
                view_menu.add_command(label="Clear Output", command=self.clear)
            
            if 'disabled_views' not in self.config or 'Demo ANSI Colors' not in self.config['disabled_views']:
                view_menu.add_command(label="Demo ANSI Colors", command=self._demo_colors)
        
        # Colors menu
        if 'disabled_menus' not in self.config or 'Colors' not in self.config['disabled_menus']:
            colors_menu = Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Colors", menu=colors_menu)
            colors_menu.add_command(label="Default Theme", command=lambda: self.set_theme("default"))
            colors_menu.add_command(label="Dark Theme", command=lambda: self.set_theme("dark"))
            colors_menu.add_command(label="Light Theme", command=lambda: self.set_theme("light"))
            colors_menu.add_command(label="Green on Black", command=lambda: self.set_theme("matrix"))
    
    def _parse_ansi_codes(self, text: str) -> List[Tuple[str, List[str]]]:
        """Parse ANSI escape sequences in text"""
        # ANSI escape sequence regex pattern
        ansi_pattern = re.compile(r'(\x1b\[[\d;]*m)')
        
        parts = []
        last_end = 0
        current_codes: List[str] = []
        
        for match in ansi_pattern.finditer(text):
            # Add normal text
            if match.start() > last_end:
                normal_text = text[last_end:match.start()]
                if normal_text:
                    parts.append((normal_text, current_codes.copy()))
            
            # Parse ANSI code
            ansi_code = match.group(0)
            code_str = ansi_code[2:-1]  # Remove \x1b[ and m
            
            if code_str == '':
                # Reset all attributes
                current_codes = ['0']
            else:
                codes = code_str.split(';')
                for code in codes:
                    if code == '0':
                        # Reset
                        current_codes = ['0']
                    elif code in ['1', '3', '4', '7', '9']:
                        # Style codes
                        if code not in current_codes:
                            if code == '1' and '22' in current_codes:
                                current_codes.remove('22')
                            current_codes.append(code)
                    elif code in ['22', '23', '24', '27', '29']:
                        # Reset specific styles
                        reset_map = {'22': '1', '23': '3', '24': '4', '27': '7', '29': '9'}
                        if reset_map[code] in current_codes:
                            current_codes.remove(reset_map[code])
                    elif code in self.ansi_colors or code.startswith('38;') or code.startswith('48;'):
                        # Color codes
                        if 'disabled_colors' in self.config and code in self.config['disabled_colors']:
                            continue
                            
                        # Remove same type color codes
                        if code in ['30', '31', '32', '33', '34', '35', '36', '37',
                                   '90', '91', '92', '93', '94', '95', '96', '97']:
                            # Remove other basic foreground colors
                            for c in list(current_codes):
                                if c in ['30', '31', '32', '33', '34', '35', '36', '37',
                                        '90', '91', '92', '93', '94', '95', '96', '97']:
                                    current_codes.remove(c)
                        elif code in ['40', '41', '42', '43', '44', '45', '46', '47']:
                            # Remove other basic background colors
                            for c in list(current_codes):
                                if c in ['40', '41', '42', '43', '44', '45', '46', '47']:
                                    current_codes.remove(c)
                        elif code.startswith('38;'):
                            # Remove other foreground colors
                            for c in list(current_codes):
                                if c.startswith('38;'):
                                    current_codes.remove(c)
                        elif code.startswith('48;'):
                            # Remove other background colors
                            for c in list(current_codes):
                                if c.startswith('48;'):
                                    current_codes.remove(c)
                        current_codes.append(code)
        
        # Add remaining text
        if last_end < len(text):
            remaining_text = text[last_end:]
            if remaining_text:
                parts.append((remaining_text, current_codes.copy()))
        
        return parts
    
    def _get_tags_for_codes(self, codes: List[str]) -> List[str]:
        """Get corresponding tag list based on ANSI codes"""
        tags = []
        
        for code in codes:
            if code == '0':
                # Reset all styles
                tags = ['default']
                break
            elif code in ['1', '3', '4', '7', '9']:
                # Style tags
                style_map = {'1': 'bold', '3': 'italic', '4': 'underline', 
                            '7': 'reverse', '9': 'strikethrough'}
                if code in style_map:
                    tags.append(style_map[code])
            elif code in self.ansi_colors or code.startswith('38;') or code.startswith('48;'):
                # Skip disabled colors
                if 'disabled_colors' in self.config and code in self.config['disabled_colors']:
                    continue
                # Color tags
                tag_name = f"ansi_{code}"
                if tag_name in self.tag_names:
                    tags.append(tag_name)
        
        return tags if tags else ['default']
    
    def _process_escape_sequences(self, text: str) -> str:
        """Process escape sequences like \n, \t, etc."""
        # Replace common escape sequences
        replacements = {
            '\\n': '\n',
            '\\t': '\t',
            '\\r': '\r',
            '\\b': '\b',
            '\\f': '\f',
            '\\v': '\v',
            '\\\\': '\\',
            '\\"': '"',
            "\\'": "'"
        }
        
        for esc_seq, char in replacements.items():
            text = text.replace(esc_seq, char)
        
        return text
    
    def display_paragraph(self, text: str, parse_ansi: bool = True, font_family: Optional[str] = None, 
                         font_size: Optional[int] = None, font_style: Optional[str] = None) -> None:
        """Thread-safe display paragraph (no auto newline)"""
        def _update():
            try:
                self.text_area.config(state=tk.NORMAL)
                
                # Process escape sequences
                text_processed = self._process_escape_sequences(text)
                
                # Check custom font settings
                font_tags = []
                if font_family or font_size or font_style:
                    # Create unique tag for font combination
                    font_family_val = font_family or "Courier"
                    font_size_val = font_size or 10
                    font_style_val = font_style or "normal"
                    font_key = f"font_{font_family_val}_{font_size_val}_{font_style_val}"
                    
                    if font_key not in self.tag_names:
                        self.text_area.tag_configure(font_key, 
                                                     font=(font_family_val, font_size_val, font_style_val))
                        self.tag_names.add(font_key)
                    font_tags.append(font_key)
                
                if parse_ansi and ('\x1b[' in text_processed or '\033[' in text_processed):
                    # Parse and apply ANSI colors
                    parts = self._parse_ansi_codes(text_processed)
                    
                    for part_text, codes in parts:
                        tags = self._get_tags_for_codes(codes)
                        
                        # Add font tags (if specified)
                        if font_tags:
                            tags = font_tags + tags
                        
                        # Insert text and apply tags
                        self.text_area.insert(tk.END, part_text, tuple(tags))
                else:
                    # Normal text
                    tags = ['default']
                    if font_tags:
                        tags = font_tags
                    self.text_area.insert(tk.END, text_processed, tuple(tags))
                
                self.text_area.config(state=tk.DISABLED)
                self.text_area.see(tk.END)
            except tk.TclError as e:
                if self.running:
                    self._safe_print(f"Tkinter error in display_paragraph: {e}")
            except Exception as e:
                if self.running:
                    self._safe_print(f"Error in display_paragraph: {e}")
        
        if self.running:
            self.root.after(0, _update)
    
    def display(self, text: str, parse_ansi: bool = True, font_family: Optional[str] = None, 
               font_size: Optional[int] = None, font_style: Optional[str] = None) -> None:
        """Thread-safe display text (auto newline)"""
        def _update():
            try:
                self.text_area.config(state=tk.NORMAL)
                
                # Check custom font settings
                font_tags = []
                if font_family or font_size or font_style:
                    # Create unique tag for font combination
                    font_family_val = font_family or "Courier"
                    font_size_val = font_size or 10
                    font_style_val = font_style or "normal"
                    font_key = f"font_{font_family_val}_{font_size_val}_{font_style_val}"
                    
                    if font_key not in self.tag_names:
                        self.text_area.tag_configure(font_key, 
                                                     font=(font_family_val, font_size_val, font_style_val))
                        self.tag_names.add(font_key)
                    font_tags.append(font_key)
                
                if parse_ansi and ('\x1b[' in str(text) or '\033[' in str(text)):
                    # Parse and apply ANSI colors
                    parts = self._parse_ansi_codes(str(text))
                    
                    for part_text, codes in parts:
                        tags = self._get_tags_for_codes(codes)
                        
                        # Add font tags (if specified)
                        if font_tags:
                            tags = font_tags + tags
                        
                        # Insert text and apply tags
                        self.text_area.insert(tk.END, part_text, tuple(tags))
                    
                    # Add newline
                    if font_tags:
                        self.text_area.insert(tk.END, "\n", tuple(font_tags))
                    else:
                        self.text_area.insert(tk.END, "\n", 'default')
                else:
                    # Normal text
                    tags = ['default']
                    if font_tags:
                        tags = font_tags
                    self.text_area.insert(tk.END, str(text) + "\n", tuple(tags))
                
                self.text_area.config(state=tk.DISABLED)
                self.text_area.see(tk.END)
            except tk.TclError as e:
                if self.running:
                    self._safe_print(f"Tkinter error in display: {e}")
            except Exception as e:
                if self.running:
                    self._safe_print(f"Error in display: {e}")
        
        if self.running:
            self.root.after(0, _update)
    
    def display_colored(self, text: str, fg_color: Optional[str] = None, bg_color: Optional[str] = None, 
                       bold: bool = False, underline: bool = False, italic: bool = False,
                       strikethrough: bool = False, reverse: bool = False,
                       font_family: Optional[str] = None, font_size: Optional[int] = None, 
                       font_style: Optional[str] = None) -> None:
        """Directly display colored text"""
        def _update():
            try:
                self.text_area.config(state=tk.NORMAL)
                
                tags = ['default']
                
                # Process foreground color
                if fg_color is not None and fg_color != "":
                    fg_color_lower = fg_color.lower()
                    if fg_color_lower in self.color_name_to_hex:
                        color_value = self.color_name_to_hex[fg_color_lower]
                        custom_fg_tag = f"custom_fg_{color_value}"
                        tags.append(custom_fg_tag)
                        if custom_fg_tag not in self.tag_names:
                            self.text_area.tag_configure(custom_fg_tag, foreground=color_value)
                            self.tag_names.add(custom_fg_tag)
                    elif fg_color.isdigit():
                        # ANSI code
                        if ('disabled_colors' not in self.config or 
                            fg_color not in self.config.get('disabled_colors', [])):
                            if fg_color in self.ansi_colors:
                                tags.append(f"ansi_{fg_color}")
                    elif fg_color.startswith('#') and len(fg_color) in [4, 5, 7, 9]:
                        # Hex color
                        color_value = fg_color
                        custom_fg_tag = f"custom_fg_{color_value}"
                        tags.append(custom_fg_tag)
                        if custom_fg_tag not in self.tag_names:
                            self.text_area.tag_configure(custom_fg_tag, foreground=color_value)
                            self.tag_names.add(custom_fg_tag)
                    elif ';' in fg_color and fg_color.startswith('38;'):
                        # Extended ANSI color codes
                        if fg_color in self.ansi_colors:
                            tags.append(f"ansi_{fg_color}")
                    else:
                        # Try named color
                        try:
                            if fg_color.strip():
                                self.text_area.tag_configure(f"custom_fg_{fg_color}", foreground=fg_color)
                                tags.append(f"custom_fg_{fg_color}")
                                self.tag_names.add(f"custom_fg_{fg_color}")
                        except tk.TclError:
                            pass
                
                # Process background color
                if bg_color is not None and bg_color != "":
                    bg_color_lower = bg_color.lower()
                    if bg_color_lower in self.color_name_to_hex:
                        color_value = self.color_name_to_hex[bg_color_lower]
                        custom_bg_tag = f"custom_bg_{color_value}"
                        tags.append(custom_bg_tag)
                        if custom_bg_tag not in self.tag_names:
                            self.text_area.tag_configure(custom_bg_tag, background=color_value)
                            self.tag_names.add(custom_bg_tag)
                    elif bg_color.isdigit():
                        # ANSI code
                        if ('disabled_colors' not in self.config or 
                            bg_color not in self.config.get('disabled_colors', [])):
                            if bg_color in self.ansi_colors:
                                tags.append(f"ansi_{bg_color}")
                    elif bg_color.startswith('#') and len(bg_color) in [4, 5, 7, 9]:
                        # Hex color
                        color_value = bg_color
                        custom_bg_tag = f"custom_bg_{color_value}"
                        tags.append(custom_bg_tag)
                        if custom_bg_tag not in self.tag_names:
                            self.text_area.tag_configure(custom_bg_tag, background=color_value)
                            self.tag_names.add(custom_bg_tag)
                    elif ';' in bg_color and bg_color.startswith('48;'):
                        # Extended ANSI color codes
                        if bg_color in self.ansi_colors:
                            tags.append(f"ansi_{bg_color}")
                    else:
                        # Try named color
                        try:
                            if bg_color.strip():
                                self.text_area.tag_configure(f"custom_bg_{bg_color}", background=bg_color)
                                tags.append(f"custom_bg_{bg_color}")
                                self.tag_names.add(f"custom_bg_{bg_color}")
                        except tk.TclError:
                            pass
                
                # Process font
                if font_family or font_size or font_style:
                    font_family_val = font_family or "Courier"
                    font_size_val = font_size or 10
                    font_style_val = font_style or "normal"
                    font_key = f"font_{font_family_val}_{font_size_val}_{font_style_val}"
                    
                    if font_key not in self.tag_names:
                        self.text_area.tag_configure(font_key, 
                                                     font=(font_family_val, font_size_val, font_style_val))
                        self.tag_names.add(font_key)
                    tags.append(font_key)
                
                # Process styles
                if bold:
                    tags.append('bold')
                if underline:
                    tags.append('underline')
                if italic:
                    tags.append('italic')
                if strikethrough:
                    tags.append('strikethrough')
                if reverse:
                    tags.append('reverse')
                
                self.text_area.insert(tk.END, str(text) + "\n", tuple(tags))
                self.text_area.config(state=tk.DISABLED)
                self.text_area.see(tk.END)
            except tk.TclError as e:
                if self.running:
                    self._safe_print(f"Tkinter error in display_colored: {e}")
            except Exception as e:
                if self.running:
                    self._safe_print(f"Error in display_colored: {e}")
        
        if self.running:
            self.root.after(0, _update)
    
    def _demo_colors(self) -> None:
        """Display ANSI color demo"""
        demo_texts = [
            ("\x1b[1mANSI Color Demo\x1b[0m\n", False),
            ("\x1b[1;37mBasic Colors:\x1b[0m\n", True),
            ("  \x1b[30mBlack\x1b[0m  \x1b[31mRed\x1b[0m  \x1b[32mGreen\x1b[0m  \x1b[33mYellow\x1b[0m\n", True),
            ("  \x1b[34mBlue\x1b[0m  \x1b[35mMagenta\x1b[0m  \x1b[36mCyan\x1b[0m  \x1b[37mWhite\x1b[0m\n", True),
            ("\n\x1b[1;37mBright Colors:\x1b[0m\n", True),
            ("  \x1b[90mGray\x1b[0m  \x1b[91mBright Red\x1b[0m  \x1b[92mBright Green\x1b[0m\n", True),
            ("  \x1b[93mBright Yellow\x1b[0m  \x1b[94mBright Blue\x1b[0m  \x1b[95mBright Magenta\x1b[0m\n", True),
            ("\n\x1b[1;37mBackground Colors:\x1b[0m\n", True),
            ("  \x1b[40;37mBlack BG\x1b[0m  \x1b[41mRed BG\x1b[0m  \x1b[42mGreen BG\x1b[0m\n", True),
            ("  \x1b[43mYellow BG\x1b[0m  \x1b[44mBlue BG\x1b[0m  \x1b[45mMagenta BG\x1b[0m\n", True),
            ("\n\x1b[1;37mExtended Colors:\x1b[0m\n", True),
            ("  \x1b[38;5;1mDark Red\x1b[0m  \x1b[38;5;9mRed\x1b[0m  \x1b[38;5;10mGreen\x1b[0m  \x1b[38;5;12mBlue\x1b[0m\n", True),
            ("  \x1b[48;5;1mDark Red BG\x1b[0m  \x1b[48;5;9mRed BG\x1b[0m\n", True),
            ("\n\x1b[1;37mTrue Colors (RGB):\x1b[0m\n", True),
            ("  \x1b[38;2;255;0;0mRed\x1b[0m  \x1b[38;2;0;255;0mGreen\x1b[0m  \x1b[38;2;0;0;255mBlue\x1b[0m\n", True),
            ("\n\x1b[1;37mText Styles:\x1b[0m\n", True),
            ("  \x1b[1mBold\x1b[0m  \x1b[3mItalic\x1b[0m  \x1b[4mUnderline\x1b[0m  \x1b[9mStrikethrough\x1b[0m\n", True),
            ("\n\x1b[1;37mCombined Styles:\x1b[0m\n", True),
            ("  \x1b[1;31mBold Red\x1b[0m  \x1b[1;4;32mBold Underlined Green\x1b[0m\n", True),
            ("  \x1b[1;33;44mBold Yellow on Blue\x1b[0m  \x1b[1;37;41mBold White on Red\x1b[0m\n", True),
        ]
        
        for text, parse_ansi in demo_texts:
            self.display(text, parse_ansi)
    
    def set_theme(self, theme_name: str) -> None:
        """Set theme"""
        def _set_theme():
            try:
                if theme_name == "dark":
                    self.text_area.config(bg="black", fg="white", insertbackground="white")
                    self.text_area.tag_configure("default", foreground="white", background="black")
                elif theme_name == "light":
                    self.text_area.config(bg="white", fg="black", insertbackground="black")
                    self.text_area.tag_configure("default", foreground="black", background="white")
                elif theme_name == "matrix":
                    self.text_area.config(bg="black", fg="#00ff00", insertbackground="#00ff00")
                    self.text_area.tag_configure("default", foreground="#00ff00", background="black")
                else:  # Default theme
                    self.text_area.config(bg="black", fg="white", insertbackground="white")
                    self.text_area.tag_configure("default", foreground="white", background="black")
                
                self.text_area.see(tk.END)
            except tk.TclError as e:
                if self.running:
                    self._safe_print(f"Tkinter error setting theme: {e}")
        
        if self.running:
            self.root.after(0, _set_theme)
    
    def user_write(self, prompt: str = "Input:") -> Optional[str]:
        """Thread-safe input dialog (opens in new window)"""
        if not self.running:
            return None
        
        def _ask():
            try:
                result = simpledialog.askstring("Input", prompt, parent=self.root)
                self.input_queue.put(result)
            except tk.TclError:
                self.input_queue.put(None)
            except Exception as e:
                self._safe_print(f"Error in user_write dialog: {e}")
                self.input_queue.put(None)
        
        self.root.after(0, _ask)
        
        # Wait for input, but check if still running
        while self.running:
            try:
                return self.input_queue.get(timeout=0.1)
            except queue.Empty:
                continue
        return None
    
    def user_type_in(self, prompt: str = ">> ") -> Optional[str]:
        """Thread-safe terminal-style input (embedded in main window)"""
        if not self.running:
            return None
            
        def _prepare_input():
            try:
                # Update prompt in label
                self.input_label.config(text=prompt)
                
                # Clear previous input
                self.input_var.set("")
                
                # Focus input field
                self.input_entry.focus_set()
                
                # Enable input field
                self.input_entry.config(state=tk.NORMAL)
            except tk.TclError as e:
                if self.running:
                    self._safe_print(f"Tkinter error preparing input: {e}")
        
        # Clear old values from queue
        while not self.type_in_queue.empty():
            try:
                self.type_in_queue.get_nowait()
            except queue.Empty:
                break
        
        # Prepare input field
        try:
            self.root.after(0, _prepare_input)
        except tk.TclError as e:
            if self.running:
                self._safe_print(f"Tkinter error scheduling input preparation: {e}")
            return None
        
        # Block and wait for user input
        while self.running:
            try:
                return self.type_in_queue.get(timeout=0.1)
            except queue.Empty:
                continue
        return None
    
    def _on_enter_pressed(self, event: Optional[tk.Event] = None) -> str:
        """Handle Enter key press in input field"""
        self._on_send_input()
        return "break"  # Prevent default behavior
    
    def _on_send_input(self) -> None:
        """Send input from terminal-style input field"""
        try:
            user_input = self.input_var.get().strip()
            
            if user_input:
                # Put input in queue
                self.type_in_queue.put(user_input)
                
                # Display user input in output area
                self.text_area.config(state=tk.NORMAL)
                self.text_area.insert(tk.END, f"{self.input_label.cget('text')}{user_input}\n", 'default')
                self.text_area.config(state=tk.DISABLED)
                self.text_area.see(tk.END)
                
                # Clear input field
                self.input_var.set("")
        except tk.TclError as e:
            if self.running:
                self._safe_print(f"Tkinter error sending input: {e}")
        except Exception as e:
            if self.running:
                self._safe_print(f"Error sending input: {e}")
    
    def _clear_input(self) -> None:
        """Clear terminal-style input field"""
        try:
            self.input_var.set("")
            self.input_entry.focus_set()
        except tk.TclError as e:
            if self.running:
                self._safe_print(f"Tkinter error clearing input: {e}")
    
    def focus_input(self) -> None:
        """Set focus to terminal-style input field"""
        try:
            self.input_entry.focus_set()
        except tk.TclError as e:
            if self.running:
                self._safe_print(f"Tkinter error focusing input: {e}")
    
    def clear(self) -> None:
        """Clear output area"""
        try:
            self.text_area.config(state=tk.NORMAL)
            self.text_area.delete(1.0, tk.END)
            self.text_area.config(state=tk.DISABLED)
        except tk.TclError as e:
            if self.running:
                self._safe_print(f"Tkinter error clearing text: {e}")
    
    def copy_text(self) -> None:
        """Copy selected text"""
        try:
            selected = self.text_area.selection_get()
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
        except tk.TclError:
            pass  # No text selected
        except Exception as e:
            if self.running:
                self._safe_print(f"Error copying text: {e}")
    
    def select_all(self) -> None:
        """Select all text"""
        try:
            self.text_area.config(state=tk.NORMAL)
            self.text_area.tag_add(tk.SEL, "1.0", tk.END)
            self.text_area.config(state=tk.DISABLED)
            self.text_area.mark_set(tk.INSERT, "1.0")
            self.text_area.see(tk.INSERT)
        except tk.TclError as e:
            if self.running:
                self._safe_print(f"Tkinter error selecting all: {e}")
    
    def exit(self) -> None:
        """Exit GUI"""
        self.running = False
        try:
            self.root.quit()
            self.root.destroy()
        except tk.TclError:
            pass  # Already destroyed
        except Exception as e:
            self._safe_print(f"Error exiting GUI: {e}")
    
    def run(self, func: Optional[Callable] = None, *args, **kwargs) -> Any:
        """
        Run GUI and optional worker function
        Tkinter operations stay in main thread; logic runs in another thread
        """
        result_queue = queue.Queue()
        
        if func:
            def worker():
                try:
                    result = func(*args, **kwargs)
                    result_queue.put(result)
                except Exception as e:
                    self.display(f"Error: {e}\n{traceback.format_exc()}")
                    result_queue.put(e)
            thread = threading.Thread(target=worker, daemon=True)
            thread.start()
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.exit()
        except Exception as e:
            self._safe_print(f"Error in mainloop: {e}")
            self.exit()
        
        if func:
            # Wait for function to complete, but make it interruptible
            while self.running:
                try:
                    return result_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
        return None


# Global instance and helper functions
_gui_instance = None

def _get_instance() -> Py2GUI:
    """Get or create global instance"""
    global _gui_instance
    if _gui_instance is None or not _gui_instance.running:
        _gui_instance = Py2GUI()
    return _gui_instance

def display(text: str, parse_ansi: bool = True, font_family: Optional[str] = None, 
            font_size: Optional[int] = None, font_style: Optional[str] = None) -> None:
    """Display text (auto newline)"""
    _get_instance().display(text, parse_ansi, font_family, font_size, font_style)

def display_colored(text: str, fg_color: Optional[str] = None, bg_color: Optional[str] = None, 
                   bold: bool = False, underline: bool = False, italic: bool = False,
                   strikethrough: bool = False, reverse: bool = False,
                   font_family: Optional[str] = None, font_size: Optional[int] = None, 
                   font_style: Optional[str] = None) -> None:
    """Directly display colored text"""
    _get_instance().display_colored(text, fg_color, bg_color, bold, underline, 
                                   italic, strikethrough, reverse, font_family, 
                                   font_size, font_style)

def display_paragraph(text: str, parse_ansi: bool = True, font_family: Optional[str] = None, 
                     font_size: Optional[int] = None, font_style: Optional[str] = None) -> None:
    """Display paragraph (no auto newline)"""
    _get_instance().display_paragraph(text, parse_ansi, font_family, font_size, font_style)

def user_write(prompt: str = "Input:") -> Optional[str]:
    """User input (dialog)"""
    return _get_instance().user_write(prompt)

def user_type_in(prompt: str = ">> ") -> Optional[str]:
    """User input (terminal-style)"""
    return _get_instance().user_type_in(prompt)

def clear() -> None:
    """Clear output"""
    _get_instance().clear()

def copy_text() -> None:
    """Copy text"""
    _get_instance().copy_text()

def select_all() -> None:
    """Select all"""
    _get_instance().select_all()

def exit_gui() -> None:
    """Exit GUI"""
    _get_instance().exit()

def run(func: Optional[Callable] = None, *args, **kwargs) -> Any:
    """Run GUI"""
    return _get_instance().run(func, *args, **kwargs)

def focus_input() -> None:
    """Focus on input field"""
    _get_instance().focus_input()

def set_theme(theme_name: str) -> None:
    """Set theme"""
    _get_instance().set_theme(theme_name)