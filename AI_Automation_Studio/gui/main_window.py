"""
Main GUI Application for AI Automation Studio
Dark-themed modern tkinter interface with 4 tabs
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import json
from datetime import datetime
from pathlib import Path

# Import core engines
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.mouse_keyboard import MouseKeyboardEngine
from core.file_manager import FileManagerEngine
from core.capcut_automator import CapCutAutomator
from core.ai_engine import AIEngine


class AIAutomationStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ AI Automation Studio")
        self.root.geometry("1280x820")
        self.root.minsize(1000, 650)
        
        # Color theme
        self.colors = {
            'bg_dark': '#1a1a2e',
            'bg_medium': '#16213e',
            'bg_light': '#0f3460',
            'accent': '#e94560',
            'text_primary': '#ffffff',
            'text_secondary': '#a8a8b3',
            'success': '#00b894',
            'warning': '#fdcb6e',
            'danger': '#d63031'
        }
        
        # Configure root style
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Initialize engines
        self.mk_engine = MouseKeyboardEngine(log_callback=self.log_general)
        self.fm_engine = FileManagerEngine(log_callback=self.log_general)
        self.cc_engine = CapCutAutomator(log_callback=self.log_general)
        self.ai_engine = AIEngine(log_callback=self.log_general)
        
        # State variables
        self.is_recording = False
        self.recorded_actions = []
        self.playback_stop_event = threading.Event()
        self.current_directory = os.path.expanduser("~")
        self.selected_files = []
        
        # Build UI
        self._create_header()
        self._create_notebook()
        self._create_status_bar()
        
        # Start mouse position updater
        self._update_mouse_position()
        
        # Center window
        self._center_window()
    
    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_header(self):
        """Create header bar with title and clock"""
        header = tk.Frame(self.root, bg=self.colors['bg_medium'], height=60)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header, 
            text="⚡ AI Automation Studio", 
            font=("Segoe UI", 16, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium']
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Version
        version_label = tk.Label(
            header,
            text="v2.0",
            font=("Segoe UI", 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_medium']
        )
        version_label.pack(side=tk.RIGHT, padx=(10, 20), pady=15)
        
        # Clock
        self.clock_label = tk.Label(
            header,
            text="",
            font=("Consolas", 11),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium']
        )
        self.clock_label.pack(side=tk.RIGHT, padx=10, pady=15)
        self._update_clock()
    
    def _update_clock(self):
        """Update clock every second"""
        current_time = datetime.now().strftime("%H:%M:%S  %Y-%m-%d")
        self.clock_label.config(text=current_time)
        self.root.after(1000, self._update_clock)
    
    def _create_notebook(self):
        """Create tabbed notebook interface"""
        # Custom style for notebook
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure notebook style
        style.configure(
            'TNotebook',
            background=self.colors['bg_dark'],
            borderwidth=0
        )
        style.configure(
            'TNotebook.Tab',
            background=self.colors['bg_medium'],
            foreground=self.colors['text_primary'],
            padding=[20, 10],
            font=('Segoe UI', 11)
        )
        style.map(
            'TNotebook.Tab',
            background=[('selected', self.colors['bg_light'])],
            foreground=[('selected', self.colors['text_primary'])]
        )
        
        self.notebook = ttk.Notebook(self.root, style='TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self._create_mouse_keyboard_tab()
        self._create_file_manager_tab()
        self._create_capcut_tab()
        self._create_ai_commands_tab()
    
    def _create_status_bar(self):
        """Create status bar at bottom"""
        status_frame = tk.Frame(self.root, bg=self.colors['bg_medium'], height=28)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        # Status indicator
        self.status_indicator = tk.Label(
            status_frame,
            text="● Ready",
            font=("Segoe UI", 9),
            fg=self.colors['success'],
            bg=self.colors['bg_medium']
        )
        self.status_indicator.pack(side=tk.LEFT, padx=15)
        
        # Recording indicator
        self.recording_indicator = tk.Label(
            status_frame,
            text="",
            font=("Segoe UI", 9, "bold"),
            fg=self.colors['danger'],
            bg=self.colors['bg_medium']
        )
        self.recording_indicator.pack(side=tk.LEFT, padx=10)
        
        # Mouse position
        self.mouse_pos_label = tk.Label(
            status_frame,
            text="Mouse: (0, 0)",
            font=("Consolas", 9),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_medium']
        )
        self.mouse_pos_label.pack(side=tk.RIGHT, padx=15)
    
    def _update_mouse_position(self):
        """Update mouse position display every 500ms"""
        try:
            x, y = self.mk_engine.get_mouse_position()
            self.mouse_pos_label.config(text=f"Mouse: ({x}, {y})")
        except:
            pass
        self.root.after(500, self._update_mouse_position)
    
    def log_general(self, message):
        """Log to general log (thread-safe)"""
        def update():
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_text = f"[{timestamp}] {message}\n"
            
            # Try to log to all available log widgets
            for attr_name in dir(self):
                if attr_name.endswith('_log') and hasattr(getattr(self, attr_name), 'insert'):
                    log_widget = getattr(self, attr_name)
                    try:
                        log_widget.insert(tk.END, log_text)
                        log_widget.see(tk.END)
                    except:
                        pass
        try:
            self.root.after(0, update)
        except:
            pass
    
    def set_status(self, status_type, message=""):
        """Set status bar indicator"""
        colors = {
            'ready': self.colors['success'],
            'processing': self.colors['warning'],
            'error': self.colors['danger']
        }
        color = colors.get(status_type, self.colors['success'])
        text = f"● {message}" if message else f"● {status_type.capitalize()}"
        self.status_indicator.config(text=text, fg=color)
    
    # ==================== TAB 1: MOUSE & KEYBOARD ====================
    def _create_mouse_keyboard_tab(self):
        """Create Mouse & Keyboard automation tab"""
        tab = tk.Frame(self.notebook, bg=self.colors['bg_dark'])
        self.notebook.add(tab, text="🖥 Mouse & Keyboard")
        
        # Left panel (controls)
        left_panel = tk.Frame(tab, bg=self.colors['bg_dark'], width=620)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        left_panel.pack_propagate(False)
        
        # Right panel (log)
        right_panel = tk.Frame(tab, bg=self.colors['bg_dark'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === Mouse Control Section ===
        mouse_frame = tk.LabelFrame(
            left_panel, text="🖱 Mouse Control", 
            font=("Segoe UI", 12, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium'],
            padx=15, pady=15
        )
        mouse_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Coordinates row
        coord_frame = tk.Frame(mouse_frame, bg=self.colors['bg_medium'])
        coord_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(coord_frame, text="X:", fg=self.colors['text_secondary'], bg=self.colors['bg_medium']).pack(side=tk.LEFT, padx=(0, 5))
        self.mk_x_entry = tk.Entry(coord_frame, width=8, font=("Consolas", 10), bg=self.colors['bg_light'], fg=self.colors['text_primary'], insertbackground='white')
        self.mk_x_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(coord_frame, text="Y:", fg=self.colors['text_secondary'], bg=self.colors['bg_medium']).pack(side=tk.LEFT, padx=(0, 5))
        self.mk_y_entry = tk.Entry(coord_frame, width=8, font=("Consolas", 10), bg=self.colors['bg_light'], fg=self.colors['text_primary'], insertbackground='white')
        self.mk_y_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Get position button
        get_pos_btn = tk.Button(
            coord_frame, text="Get Position",
            command=self._mk_get_position,
            bg=self.colors['bg_light'], fg=self.colors['text_primary'],
            activebackground=self.colors['accent'], activeforeground='white',
            relief=tk.FLAT, padx=10, pady=3
        )
        get_pos_btn.pack(side=tk.LEFT, padx=10)
        
        # Mouse action buttons
        btn_frame = tk.Frame(mouse_frame, bg=self.colors['bg_medium'])
        btn_frame.pack(fill=tk.X)
        
        actions = [
            ("Move", self._mk_move), ("Left Click", self._mk_left_click),
            ("Right Click", self._mk_right_click), ("Double Click", self._mk_double_click)
        ]
        for text, cmd in actions:
            btn = tk.Button(
                btn_frame, text=text, command=cmd,
                bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                activebackground=self.colors['accent'], activeforeground='white',
                relief=tk.FLAT, padx=12, pady=5
            )
            btn.pack(side=tk.LEFT, padx=3)
        
        # Drag and scroll
        drag_scroll_frame = tk.Frame(mouse_frame, bg=self.colors['bg_medium'])
        drag_scroll_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(drag_scroll_frame, text="Drag (use 4 coords)", command=self._mk_drag,
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=10, pady=3).pack(side=tk.LEFT, padx=3)
        
        tk.Button(drag_scroll_frame, text="Scroll Up", command=lambda: self._mk_scroll(100),
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=10, pady=3).pack(side=tk.LEFT, padx=3)
        
        tk.Button(drag_scroll_frame, text="Scroll Down", command=lambda: self._mk_scroll(-100),
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=10, pady=3).pack(side=tk.LEFT, padx=3)
        
        tk.Button(drag_scroll_frame, text="📸 Screenshot", command=self._mk_screenshot,
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=10, pady=3).pack(side=tk.RIGHT)
        
        # === Keyboard Control Section ===
        kb_frame = tk.LabelFrame(
            left_panel, text="⌨️ Keyboard Control",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium'],
            padx=15, pady=15
        )
        kb_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Type text
        type_frame = tk.Frame(kb_frame, bg=self.colors['bg_medium'])
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mk_type_entry = tk.Entry(type_frame, font=("Consolas", 10), bg=self.colors['bg_light'], fg=self.colors['text_primary'], insertbackground='white')
        self.mk_type_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.mk_type_entry.insert(0, "Type your text here...")
        
        tk.Button(type_frame, text="Type Text", command=self._mk_type,
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=10, pady=3).pack(side=tk.LEFT)
        
        # Hotkey entry
        hotkey_frame = tk.Frame(kb_frame, bg=self.colors['bg_medium'])
        hotkey_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mk_hotkey_entry = tk.Entry(hotkey_frame, width=15, font=("Consolas", 10), bg=self.colors['bg_light'], fg=self.colors['text_primary'], insertbackground='white')
        self.mk_hotkey_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.mk_hotkey_entry.insert(0, "ctrl+c")
        
        tk.Button(hotkey_frame, text="Press Hotkey", command=self._mk_hotkey,
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=10, pady=3).pack(side=tk.LEFT)
        
        # Quick hotkeys
        quick_frame = tk.Frame(kb_frame, bg=self.colors['bg_medium'])
        quick_frame.pack(fill=tk.X)
        
        quick_keys = [
            ("Ctrl+Z", lambda: self.mk_engine.press_hotkey("ctrl+z")),
            ("Ctrl+C", lambda: self.mk_engine.press_hotkey("ctrl+c")),
            ("Ctrl+V", lambda: self.mk_engine.press_hotkey("ctrl+v")),
            ("Ctrl+A", lambda: self.mk_engine.press_hotkey("ctrl+a")),
            ("Ctrl+S", lambda: self.mk_engine.press_hotkey("ctrl+s"))
        ]
        for text, cmd in quick_keys:
            btn = tk.Button(
                quick_frame, text=text, command=cmd,
                bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                activebackground=self.colors['accent'], activeforeground='white',
                relief=tk.FLAT, padx=10, pady=3
            )
            btn.pack(side=tk.LEFT, padx=3)
        
        # === Macro Recording Section ===
        macro_frame = tk.LabelFrame(
            left_panel, text="🎬 Macro Recording",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium'],
            padx=15, pady=15
        )
        macro_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Record/Stop buttons
        record_frame = tk.Frame(macro_frame, bg=self.colors['bg_medium'])
        record_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mk_record_btn = tk.Button(
            record_frame, text="🔴 Record", command=self._mk_start_recording,
            bg=self.colors['danger'], fg='white',
            activebackground='#ff6b6b', activeforeground='white',
            relief=tk.FLAT, padx=20, pady=8, font=("Segoe UI", 10, "bold")
        )
        self.mk_record_btn.pack(side=tk.LEFT, padx=5)
        
        self.mk_stop_btn = tk.Button(
            record_frame, text="⏹ Stop", command=self._mk_stop_recording,
            bg=self.colors['bg_light'], fg=self.colors['text_primary'],
            activebackground=self.colors['accent'], activeforeground='white',
            relief=tk.FLAT, padx=20, pady=8, font=("Segoe UI", 10, "bold"),
            state=tk.DISABLED
        )
        self.mk_stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.mk_play_btn = tk.Button(
            record_frame, text="▶ Play", command=self._mk_play_macro,
            bg=self.colors['success'], fg='white',
            activebackground='#00d9a5', activeforeground='white',
            relief=tk.FLAT, padx=20, pady=8, font=("Segoe UI", 10, "bold"),
            state=tk.DISABLED
        )
        self.mk_play_btn.pack(side=tk.LEFT, padx=5)
        
        # Speed slider and loop
        speed_frame = tk.Frame(macro_frame, bg=self.colors['bg_medium'])
        speed_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(speed_frame, text="Speed:", fg=self.colors['text_secondary'], bg=self.colors['bg_medium']).pack(side=tk.LEFT, padx=(0, 5))
        self.mk_speed_var = tk.DoubleVar(value=1.0)
        speed_slider = tk.Scale(
            speed_frame, from_=0.25, to=5.0, resolution=0.25,
            orient=tk.HORIZONTAL, variable=self.mk_speed_var,
            bg=self.colors['bg_light'], fg=self.colors['text_primary'],
            troughcolor=self.colors['bg_dark'], length=200,
            highlightthickness=0
        )
        speed_slider.pack(side=tk.LEFT, padx=(0, 15))
        
        self.mk_loop_var = tk.BooleanVar(value=False)
        loop_check = tk.Checkbutton(
            speed_frame, text="Loop", variable=self.mk_loop_var,
            bg=self.colors['bg_medium'], fg=self.colors['text_primary'],
            selectcolor=self.colors['bg_light'], activebackground=self.colors['bg_medium']
        )
        loop_check.pack(side=tk.LEFT)
        
        # Save/Load buttons
        save_load_frame = tk.Frame(macro_frame, bg=self.colors['bg_medium'])
        save_load_frame.pack(fill=tk.X)
        
        tk.Button(save_load_frame, text="💾 Save Macro", command=self._mk_save_macro,
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=10, pady=3).pack(side=tk.LEFT, padx=3)
        
        tk.Button(save_load_frame, text="📂 Load Macro", command=self._mk_load_macro,
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=10, pady=3).pack(side=tk.LEFT, padx=3)
        
        # === Log Panel ===
        log_label = tk.Label(
            right_panel, text="📋 Activity Log",
            font=("Segoe UI", 11, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_dark']
        )
        log_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.mk_log = scrolledtext.ScrolledText(
            right_panel,
            font=("Consolas", 9),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_primary'],
            insertbackground='white',
            wrap=tk.WORD,
            state=tk.NORMAL
        )
        self.mk_log.pack(fill=tk.BOTH, expand=True)
        
        clear_btn = tk.Button(
            right_panel, text="Clear Log", command=lambda: self.mk_log.delete(1.0, tk.END),
            bg=self.colors['bg_light'], fg=self.colors['text_primary'],
            activebackground=self.colors['accent'], activeforeground='white',
            relief=tk.FLAT, padx=10, pady=3
        )
        clear_btn.pack(anchor=tk.E, pady=(5, 0))
    
    # Mouse & Keyboard callbacks
    def _mk_get_position(self):
        x, y = self.mk_engine.get_mouse_position()
        self.mk_x_entry.delete(0, tk.END)
        self.mk_x_entry.insert(0, str(x))
        self.mk_y_entry.delete(0, tk.END)
        self.mk_y_entry.insert(0, str(y))
    
    def _mk_move(self):
        try:
            x = int(self.mk_x_entry.get())
            y = int(self.mk_y_entry.get())
            self.mk_engine.move_mouse(x, y)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid coordinates")
    
    def _mk_left_click(self):
        try:
            x = int(self.mk_x_entry.get()) if self.mk_x_entry.get() else None
            y = int(self.mk_y_entry.get()) if self.mk_y_entry.get() else None
            self.mk_engine.left_click(x, y)
        except ValueError:
            self.mk_engine.left_click()
    
    def _mk_right_click(self):
        try:
            x = int(self.mk_x_entry.get()) if self.mk_x_entry.get() else None
            y = int(self.mk_y_entry.get()) if self.mk_y_entry.get() else None
            self.mk_engine.right_click(x, y)
        except ValueError:
            self.mk_engine.right_click()
    
    def _mk_double_click(self):
        try:
            x = int(self.mk_x_entry.get()) if self.mk_x_entry.get() else None
            y = int(self.mk_y_entry.get()) if self.mk_y_entry.get() else None
            self.mk_engine.double_click(x, y)
        except ValueError:
            self.mk_engine.double_click()
    
    def _mk_drag(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Drag Mouse")
        dialog.geometry("300x200")
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Start X:", fg=self.colors['text_secondary'], bg=self.colors['bg_dark']).pack(pady=5)
        x1_entry = tk.Entry(dialog, bg=self.colors['bg_light'], fg=self.colors['text_primary'])
        x1_entry.pack(pady=5)
        
        tk.Label(dialog, text="Start Y:", fg=self.colors['text_secondary'], bg=self.colors['bg_dark']).pack(pady=5)
        y1_entry = tk.Entry(dialog, bg=self.colors['bg_light'], fg=self.colors['text_primary'])
        y1_entry.pack(pady=5)
        
        tk.Label(dialog, text="End X:", fg=self.colors['text_secondary'], bg=self.colors['bg_dark']).pack(pady=5)
        x2_entry = tk.Entry(dialog, bg=self.colors['bg_light'], fg=self.colors['text_primary'])
        x2_entry.pack(pady=5)
        
        tk.Label(dialog, text="End Y:", fg=self.colors['text_secondary'], bg=self.colors['bg_dark']).pack(pady=5)
        y2_entry = tk.Entry(dialog, bg=self.colors['bg_light'], fg=self.colors['text_primary'])
        y2_entry.pack(pady=5)
        
        def do_drag():
            try:
                x1, y1, x2, y2 = int(x1_entry.get()), int(y1_entry.get()), int(x2_entry.get()), int(y2_entry.get())
                self.mk_engine.drag_mouse(x1, y1, x2, y2)
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid coordinates", parent=dialog)
        
        tk.Button(dialog, text="Drag", command=do_drag,
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white').pack(pady=10)
    
    def _mk_scroll(self, amount):
        try:
            x = int(self.mk_x_entry.get()) if self.mk_x_entry.get() else None
            y = int(self.mk_y_entry.get()) if self.mk_y_entry.get() else None
            self.mk_engine.scroll(amount, x, y)
        except:
            self.mk_engine.scroll(amount)
    
    def _mk_screenshot(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile=f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )
        if filepath:
            self.set_status('processing', 'Taking screenshot...')
            threading.Thread(target=lambda: self.mk_engine.take_screenshot(filepath), daemon=True).start()
    
    def _mk_type(self):
        text = self.mk_type_entry.get()
        if text and text != "Type your text here...":
            self.mk_engine.type_text(text)
    
    def _mk_hotkey(self):
        hotkey = self.mk_hotkey_entry.get()
        if hotkey:
            self.mk_engine.press_hotkey(hotkey)
    
    def _mk_start_recording(self):
        self.is_recording = True
        self.recorded_actions = []
        self.mk_engine.start_recording()
        self.recording_indicator.config(text="🔴 RECORDING")
        self.mk_record_btn.config(state=tk.DISABLED)
        self.mk_stop_btn.config(state=tk.NORMAL)
        self.mk_play_btn.config(state=tk.DISABLED)
        self.set_status('processing', 'Recording...')
    
    def _mk_stop_recording(self):
        self.recorded_actions = self.mk_engine.stop_recording()
        self.is_recording = False
        self.recording_indicator.config(text="")
        self.mk_record_btn.config(state=tk.NORMAL)
        self.mk_stop_btn.config(state=tk.DISABLED)
        if self.recorded_actions:
            self.mk_play_btn.config(state=tk.NORMAL)
        self.set_status('ready', 'Ready')
    
    def _mk_play_macro(self):
        if not self.recorded_actions:
            return
        
        self.set_status('processing', 'Playing macro...')
        self.playback_stop_event.clear()
        
        speed = self.mk_speed_var.get()
        loop = self.mk_loop_var.get()
        
        def play_thread():
            self.mk_engine.play_macro(self.recorded_actions, speed, loop, self.playback_stop_event)
            self.root.after(0, lambda: self.set_status('ready', 'Ready'))
        
        threading.Thread(target=play_thread, daemon=True).start()
    
    def _mk_save_macro(self):
        if not self.recorded_actions:
            messagebox.showinfo("Info", "No recorded actions to save")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if filepath:
            self.mk_engine.save_macro(filepath, self.recorded_actions)
    
    def _mk_load_macro(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )
        if filepath:
            self.recorded_actions = self.mk_engine.load_macro(filepath)
            if self.recorded_actions:
                self.mk_play_btn.config(state=tk.NORMAL)
                messagebox.showinfo("Loaded", f"Loaded {len(self.recorded_actions)} actions")
    
    # ==================== TAB 2: FILE MANAGER ====================
    def _create_file_manager_tab(self):
        """Create File Manager tab"""
        tab = tk.Frame(self.notebook, bg=self.colors['bg_dark'])
        self.notebook.add(tab, text="📁 File Manager")
        
        # Left panel (controls)
        left_panel = tk.Frame(tab, bg=self.colors['bg_dark'], width=620)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        left_panel.pack_propagate(False)
        
        # Right panel (log + file tree)
        right_panel = tk.Frame(tab, bg=self.colors['bg_dark'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === Directory Browser Section ===
        dir_frame = tk.LabelFrame(
            left_panel, text="📂 Directory Browser",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium'],
            padx=15, pady=15
        )
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Path entry
        path_frame = tk.Frame(dir_frame, bg=self.colors['bg_medium'])
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.fm_path_entry = tk.Entry(path_frame, font=("Consolas", 10), bg=self.colors['bg_light'], fg=self.colors['text_primary'], insertbackground='white')
        self.fm_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.fm_path_entry.insert(0, self.current_directory)
        
        tk.Button(path_frame, text="Browse", command=self._fm_browse,
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=10, pady=3).pack(side=tk.LEFT, padx=3)
        
        tk.Button(path_frame, text="🔄 Refresh", command=self._fm_refresh,
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=10, pady=3).pack(side=tk.LEFT, padx=3)
        
        # File tree
        tree_frame = tk.Frame(dir_frame, bg=self.colors['bg_medium'])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('name', 'size', 'modified', 'type')
        self.fm_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', height=8)
        self.fm_tree.heading('#0', text='Name')
        self.fm_tree.heading('name', text='Name')
        self.fm_tree.heading('size', text='Size')
        self.fm_tree.heading('modified', text='Modified')
        self.fm_tree.heading('type', text='Type')
        
        self.fm_tree.column('#0', width=200)
        self.fm_tree.column('name', width=200)
        self.fm_tree.column('size', width=80)
        self.fm_tree.column('modified', width=120)
        self.fm_tree.column('type', width=80)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.fm_tree.yview)
        self.fm_tree.configure(yscrollcommand=scrollbar.set)
        
        self.fm_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.fm_tree.bind('<<TreeviewSelect>>', self._fm_on_select)
        
        # === Batch Rename Section ===
        rename_frame = tk.LabelFrame(
            left_panel, text="✏️ Batch Rename",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium'],
            padx=15, pady=15
        )
        rename_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Mode selection
        mode_frame = tk.Frame(rename_frame, bg=self.colors['bg_medium'])
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.fm_rename_mode = tk.StringVar(value='prefix')
        modes = [
            ('Prefix', 'prefix'), ('Suffix', 'suffix'),
            ('Find/Replace', 'find_replace'), ('Sequence', 'sequence'),
            ('Lowercase', 'lowercase'), ('Uppercase', 'uppercase'),
            ('Strip Special', 'strip'), ('Date Prefix', 'date_prefix')
        ]
        for i, (text, value) in enumerate(modes):
            rb = tk.Radiobutton(mode_frame, text=text, variable=self.fm_rename_mode, value=value,
                               bg=self.colors['bg_medium'], fg=self.colors['text_primary'],
                               selectcolor=self.colors['bg_light'], activebackground=self.colors['bg_medium'])
            rb.grid(row=i//4, column=i%4, sticky=tk.W, padx=5, pady=2)
        
        # Value entry
        val_frame = tk.Frame(rename_frame, bg=self.colors['bg_medium'])
        val_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(val_frame, text="Value:", fg=self.colors['text_secondary'], bg=self.colors['bg_medium']).pack(side=tk.LEFT, padx=(0, 5))
        self.fm_rename_value = tk.Entry(val_frame, font=("Consolas", 10), bg=self.colors['bg_light'], fg=self.colors['text_primary'], insertbackground='white')
        self.fm_rename_value.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Options
        opt_frame = tk.Frame(rename_frame, bg=self.colors['bg_medium'])
        opt_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.fm_dry_run_var = tk.BooleanVar(value=True)
        dry_check = tk.Checkbutton(opt_frame, text="✓ DRY RUN (Preview first)", variable=self.fm_dry_run_var,
                                   bg=self.colors['bg_medium'], fg=self.colors['success'],
                                   selectcolor=self.colors['bg_light'], activebackground=self.colors['bg_medium'],
                                   font=("Segoe UI", 9, "bold"))
        dry_check.pack(side=tk.LEFT)
        
        # Rename buttons
        btn_frame = tk.Frame(rename_frame, bg=self.colors['bg_medium'])
        btn_frame.pack(fill=tk.X)
        
        tk.Button(btn_frame, text="Preview", command=self._fm_rename_preview,
                  bg=self.colors['warning'], fg='black',
                  activebackground='#ffeaa7', activeforeground='black',
                  relief=tk.FLAT, padx=15, pady=5).pack(side=tk.LEFT, padx=3)
        
        tk.Button(btn_frame, text="Apply Rename", command=self._fm_rename_apply,
                  bg=self.colors['success'], fg='white',
                  activebackground='#00d9a5', activeforeground='white',
                  relief=tk.FLAT, padx=15, pady=5).pack(side=tk.LEFT, padx=3)
        
        # === Organize Files Section ===
        org_frame = tk.LabelFrame(
            left_panel, text="🗂 Organize Files",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium'],
            padx=15, pady=15
        )
        org_frame.pack(fill=tk.X, pady=(0, 10))
        
        org_btns = tk.Frame(org_frame, bg=self.colors['bg_medium'])
        org_btns.pack(fill=tk.X)
        
        tk.Button(org_btns, text="By Type", command=lambda: threading.Thread(target=self._fm_organize_type, daemon=True).start(),
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=15, pady=5).pack(side=tk.LEFT, padx=3)
        
        tk.Button(org_btns, text="By Date", command=lambda: threading.Thread(target=self._fm_organize_date, daemon=True).start(),
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=15, pady=5).pack(side=tk.LEFT, padx=3)
        
        # === File Operations Section ===
        ops_frame = tk.LabelFrame(
            left_panel, text="🔧 File Operations",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium'],
            padx=15, pady=15
        )
        ops_frame.pack(fill=tk.X, pady=(0, 10))
        
        ops_grid = tk.Frame(ops_frame, bg=self.colors['bg_medium'])
        ops_grid.pack(fill=tk.X)
        
        operations = [
            ("🔍 Find Duplicates", self._fm_find_duplicates),
            ("🎬 Create Video Project", self._fm_create_project),
            ("🧹 Clean Empty Folders", self._fm_clean_empty),
            ("📋 Copy Selected", self._fm_copy_selected),
            ("📁 Move Selected", self._fm_move_selected),
            ("🗑 Delete Selected", self._fm_delete_selected),
            ("🔎 Find by Extension", self._fm_find_by_ext),
        ]
        
        for i, (text, cmd) in enumerate(operations):
            btn = tk.Button(ops_grid, text=text, command=cmd,
                           bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                           activebackground=self.colors['accent'], activeforeground='white',
                           relief=tk.FLAT, padx=10, pady=5)
            btn.grid(row=i//2, column=i%2, sticky=tk.EW, padx=3, pady=3)
            ops_grid.grid_columnconfigure(i%2, weight=1)
        
        # === Log Panel ===
        log_label = tk.Label(
            right_panel, text="📋 Activity Log",
            font=("Segoe UI", 11, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_dark']
        )
        log_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.fm_log = scrolledtext.ScrolledText(
            right_panel,
            font=("Consolas", 9),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_primary'],
            insertbackground='white',
            wrap=tk.WORD,
            state=tk.NORMAL,
            height=15
        )
        self.fm_log.pack(fill=tk.BOTH, expand=True)
        
        clear_btn = tk.Button(
            right_panel, text="Clear Log", command=lambda: self.fm_log.delete(1.0, tk.END),
            bg=self.colors['bg_light'], fg=self.colors['text_primary'],
            activebackground=self.colors['accent'], activeforeground='white',
            relief=tk.FLAT, padx=10, pady=3
        )
        clear_btn.pack(anchor=tk.E, pady=(5, 0))
    
    # File Manager callbacks
    def _fm_browse(self):
        path = filedialog.askdirectory(initialdir=self.current_directory)
        if path:
            self.current_directory = path
            self.fm_path_entry.delete(0, tk.END)
            self.fm_path_entry.insert(0, path)
            self._fm_refresh()
    
    def _fm_refresh(self):
        path = self.fm_path_entry.get()
        if not os.path.isdir(path):
            messagebox.showerror("Error", "Invalid directory path")
            return
        
        # Clear tree
        for item in self.fm_tree.get_children():
            self.fm_tree.delete(item)
        
        # Get contents
        items = self.fm_engine.get_directory_contents(path)
        
        # Add to tree
        for item in items:
            icon = "📁 " if item['is_dir'] else "📄 "
            size_str = f"{item['size'] / 1024:.1f} KB" if item['size'] > 0 else ""
            
            self.fm_tree.insert('', tk.END, iid=item['path'], 
                               text=f"{icon}{item['name']}",
                               values=(item['name'], size_str, item['modified'], item['file_type']))
    
    def _fm_on_select(self, event):
        selected = self.fm_tree.selection()
        self.selected_files = list(selected)
    
    def _fm_rename_preview(self):
        if not self.selected_files:
            messagebox.showinfo("Info", "Please select files to rename")
            return
        
        mode = self.fm_rename_mode.get()
        value = self.fm_rename_value.get()
        
        self.fm_engine.batch_rename(self.selected_files, mode, value, dry_run=True)
    
    def _fm_rename_apply(self):
        if not self.selected_files:
            messagebox.showinfo("Info", "Please select files to rename")
            return
        
        dry_run = self.fm_dry_run_var.get()
        mode = self.fm_rename_mode.get()
        value = self.fm_rename_value.get()
        
        if dry_run:
            self._fm_rename_preview()
            if not messagebox.askyesno("Confirm", "Apply these changes?"):
                return
        
        self.fm_engine.batch_rename(self.selected_files, mode, value, dry_run=False)
        self._fm_refresh()
    
    def _fm_organize_type(self):
        path = self.fm_path_entry.get()
        if messagebox.askyesno("Confirm", f"Organize files in {path} by type?"):
            self.fm_engine.organize_by_type(path, dry_run=False)
            self._fm_refresh()
    
    def _fm_organize_date(self):
        path = self.fm_path_entry.get()
        if messagebox.askyesno("Confirm", f"Organize files in {path} by date?"):
            self.fm_engine.organize_by_date(path, dry_run=False)
            self._fm_refresh()
    
    def _fm_find_duplicates(self):
        path = self.fm_path_entry.get()
        self.set_status('processing', 'Finding duplicates...')
        result = self.fm_engine.find_duplicates(path)
        if result['success'] and result['duplicates']:
            msg = f"Found {len(result['duplicates'])} groups of duplicates:\n\n"
            for i, group in enumerate(result['duplicates'][:5]):
                msg += f"Group {i+1}:\n" + "\n".join([os.path.basename(f) for f in group]) + "\n\n"
            messagebox.showinfo("Duplicates Found", msg)
        else:
            messagebox.showinfo("No Duplicates", "No duplicate files found")
        self.set_status('ready')
    
    def _fm_create_project(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Video Project")
        dialog.geometry("400x150")
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        
        tk.Label(dialog, text="Project Name:", fg=self.colors['text_primary'], bg=self.colors['bg_dark']).pack(pady=10)
        name_entry = tk.Entry(dialog, font=("Consolas", 11), bg=self.colors['bg_light'], fg=self.colors['text_primary'])
        name_entry.pack(pady=5, padx=20, fill=tk.X)
        
        def create():
            name = name_entry.get().strip()
            if name:
                base_path = self.fm_path_entry.get()
                result = self.fm_engine.create_video_project(base_path, name)
                if result['success']:
                    messagebox.showinfo("Success", f"Project created at:\n{result['path']}")
                    self._fm_refresh()
                dialog.destroy()
        
        tk.Button(dialog, text="Create Project", command=create,
                  bg=self.colors['success'], fg='white',
                  activebackground='#00d9a5').pack(pady=15)
    
    def _fm_clean_empty(self):
        path = self.fm_path_entry.get()
        if messagebox.askyesno("Confirm", "Delete all empty folders?"):
            self.fm_engine.clean_empty_folders(path)
            self._fm_refresh()
    
    def _fm_copy_selected(self):
        if not self.selected_files:
            messagebox.showinfo("Info", "Please select files")
            return
        dest = filedialog.askdirectory()
        if dest:
            self.fm_engine.copy_files(self.selected_files, dest)
    
    def _fm_move_selected(self):
        if not self.selected_files:
            messagebox.showinfo("Info", "Please select files")
            return
        dest = filedialog.askdirectory()
        if dest:
            self.fm_engine.move_files(self.selected_files, dest)
            self._fm_refresh()
    
    def _fm_delete_selected(self):
        if not self.selected_files:
            messagebox.showinfo("Info", "Please select files")
            return
        if messagebox.askyesno("Confirm Delete", f"Delete {len(self.selected_files)} items?\nThis cannot be undone!", icon='warning'):
            self.fm_engine.delete_files(self.selected_files)
            self._fm_refresh()
    
    def _fm_find_by_ext(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Find by Extension")
        dialog.geometry("350x120")
        dialog.configure(bg=self.colors['bg_dark'])
        
        tk.Label(dialog, text="Extensions (comma-separated):", fg=self.colors['text_primary'], bg=self.colors['bg_dark']).pack(pady=5)
        ext_entry = tk.Entry(dialog, font=("Consolas", 11), bg=self.colors['bg_light'], fg=self.colors['text_primary'])
        ext_entry.pack(pady=5, padx=20, fill=tk.X)
        ext_entry.insert(0, "mp4, mp3, png")
        
        def find():
            exts = ext_entry.get()
            path = self.fm_path_entry.get()
            result = self.fm_engine.find_by_extension(path, exts)
            if result['success']:
                msg = f"Found {len(result['files'])} files:\n\n" + "\n".join(result['files'][:20])
                if len(result['files']) > 20:
                    msg += f"\n...and {len(result['files']) - 20} more"
                messagebox.showinfo("Search Results", msg)
            dialog.destroy()
        
        tk.Button(dialog, text="Find", command=find,
                  bg=self.colors['bg_light'], fg=self.colors['text_primary']).pack(pady=10)
    
    # ==================== TAB 3: CAPCUT EDITOR ====================
    def _create_capcut_tab(self):
        """Create CapCut Editor automation tab"""
        tab = tk.Frame(self.notebook, bg=self.colors['bg_dark'])
        self.notebook.add(tab, text="🎬 CapCut Editor")
        
        # Left panel (controls)
        left_panel = tk.Frame(tab, bg=self.colors['bg_dark'], width=620)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        left_panel.pack_propagate(False)
        
        # Right panel (log)
        right_panel = tk.Frame(tab, bg=self.colors['bg_dark'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === CapCut Control Section ===
        cc_frame = tk.LabelFrame(
            left_panel, text="🎬 CapCut Control",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium'],
            padx=15, pady=15
        )
        cc_frame.pack(fill=tk.X, pady=(0, 10))
        
        ctrl_frame = tk.Frame(cc_frame, bg=self.colors['bg_medium'])
        ctrl_frame.pack(fill=tk.X)
        
        tk.Button(ctrl_frame, text="🔍 Find CapCut", command=self._cc_find,
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=12, pady=5).pack(side=tk.LEFT, padx=3)
        
        tk.Button(ctrl_frame, text="🚀 Launch", command=self._cc_launch,
                  bg=self.colors['success'], fg='white',
                  activebackground='#00d9a5', activeforeground='white',
                  relief=tk.FLAT, padx=12, pady=5).pack(side=tk.LEFT, padx=3)
        
        tk.Button(ctrl_frame, text="⏹ Stop All", command=self._cc_stop,
                  bg=self.colors['danger'], fg='white',
                  activebackground='#ff6b6b', activeforeground='white',
                  relief=tk.FLAT, padx=12, pady=5).pack(side=tk.LEFT, padx=3)
        
        self.cc_status_label = tk.Label(cc_frame, text="Status: Not checked", 
                                        fg=self.colors['text_secondary'], bg=self.colors['bg_medium'])
        self.cc_status_label.pack(anchor=tk.W, pady=(10, 0))
        
        # === Quick Editing Tools ===
        edit_frame = tk.LabelFrame(
            left_panel, text="✂️ Quick Editing",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium'],
            padx=15, pady=15
        )
        edit_frame.pack(fill=tk.X, pady=(0, 10))
        
        edit_grid = tk.Frame(edit_frame, bg=self.colors['bg_medium'])
        edit_grid.pack(fill=tk.X)
        
        edits = [
            ("Split (Ctrl+B)", lambda: self.cc_engine.split_clip()),
            ("Delete (Del)", lambda: self.cc_engine.delete_selected()),
            ("Undo (Ctrl+Z)", lambda: self.cc_engine.undo()),
            ("Redo (Ctrl+Y)", lambda: self.cc_engine.redo()),
            ("Play/Pause", lambda: self.cc_engine.play_pause()),
            ("Select All", lambda: self.cc_engine.select_all()),
            ("Copy", lambda: self.cc_engine.copy()),
            ("Paste", lambda: self.cc_engine.paste()),
            ("Zoom In", lambda: self.cc_engine.zoom_in_timeline()),
            ("Zoom Out", lambda: self.cc_engine.zoom_out_timeline()),
        ]
        
        for i, (text, cmd) in enumerate(edits):
            btn = tk.Button(edit_grid, text=text, command=cmd,
                           bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                           activebackground=self.colors['accent'], activeforeground='white',
                           relief=tk.FLAT, padx=8, pady=4)
            btn.grid(row=i//5, column=i%5, sticky=tk.EW, padx=2, pady=2)
            edit_grid.grid_columnconfigure(i%5, weight=1)
        
        # === Text & Overlay ===
        text_frame = tk.LabelFrame(
            left_panel, text="📝 Text & Overlay",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium'],
            padx=15, pady=15
        )
        text_frame.pack(fill=tk.X, pady=(0, 10))
        
        txt_entry_frame = tk.Frame(text_frame, bg=self.colors['bg_medium'])
        txt_entry_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.cc_text_entry = tk.Entry(txt_entry_frame, font=("Consolas", 10), bg=self.colors['bg_light'], fg=self.colors['text_primary'], insertbackground='white')
        self.cc_text_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.cc_text_entry.insert(0, "Enter text to add...")
        
        tk.Button(txt_entry_frame, text="Add Text", command=self._cc_add_text,
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=12, pady=5).pack(side=tk.LEFT)
        
        # === Effects & Animation ===
        fx_frame = tk.LabelFrame(
            left_panel, text="✨ Effects & Animation",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium'],
            padx=15, pady=15
        )
        fx_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Speed control
        speed_f = tk.Frame(fx_frame, bg=self.colors['bg_medium'])
        speed_f.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(speed_f, text="Speed:", fg=self.colors['text_secondary'], bg=self.colors['bg_medium']).pack(side=tk.LEFT, padx=(0, 5))
        self.cc_speed_entry = tk.Entry(speed_f, width=8, font=("Consolas", 10), bg=self.colors['bg_light'], fg=self.colors['text_primary'])
        self.cc_speed_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.cc_speed_entry.insert(0, "1.0")
        
        tk.Button(speed_f, text="Set Speed", command=self._cc_set_speed,
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=10, pady=3).pack(side=tk.LEFT)
        
        # Mask selection
        mask_f = tk.Frame(fx_frame, bg=self.colors['bg_medium'])
        mask_f.pack(fill=tk.X, pady=(0, 10))
        
        self.cc_mask_var = tk.StringVar(value='rectangle')
        tk.Label(mask_f, text="Mask:", fg=self.colors['text_secondary'], bg=self.colors['bg_medium']).pack(side=tk.LEFT, padx=(0, 5))
        for mask_type in ['rectangle', 'ellipse', 'linear', 'mirror']:
            rb = tk.Radiobutton(mask_f, text=mask_type.capitalize(), variable=self.cc_mask_var, value=mask_type,
                               bg=self.colors['bg_medium'], fg=self.colors['text_primary'],
                               selectcolor=self.colors['bg_light'])
            rb.pack(side=tk.LEFT, padx=5)
        
        tk.Button(mask_f, text="Apply Mask", command=self._cc_apply_mask,
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=10, pady=3).pack(side=tk.RIGHT)
        
        # Effect buttons
        fx_btns = tk.Frame(fx_frame, bg=self.colors['bg_medium'])
        fx_btns.pack(fill=tk.X)
        
        tk.Button(fx_btns, text="Add Transition", command=lambda: self.cc_engine.add_transition(),
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=10, pady=5).pack(side=tk.LEFT, padx=3)
        
        tk.Button(fx_btns, text="Add Keyframe", command=lambda: self.cc_engine.add_keyframe(),
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=10, pady=5).pack(side=tk.LEFT, padx=3)
        
        # === Import & Export ===
        io_frame = tk.LabelFrame(
            left_panel, text="📥 Import / Export",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium'],
            padx=15, pady=15
        )
        io_frame.pack(fill=tk.X, pady=(0, 10))
        
        io_btns = tk.Frame(io_frame, bg=self.colors['bg_medium'])
        io_btns.pack(fill=tk.X)
        
        tk.Button(io_btns, text="📥 Import Media", command=self._cc_import,
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=12, pady=5).pack(side=tk.LEFT, padx=3)
        
        tk.Button(io_btns, text="📤 Export Video", command=self._cc_export,
                  bg=self.colors['warning'], fg='black',
                  activebackground='#ffeaa7', activeforeground='black',
                  relief=tk.FLAT, padx=12, pady=5).pack(side=tk.LEFT, padx=3)
        
        # === Preset Workflows ===
        workflow_frame = tk.LabelFrame(
            left_panel, text="⚡ Preset Workflows",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium'],
            padx=15, pady=15
        )
        workflow_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.cc_workflow_listbox = tk.Listbox(workflow_frame, font=("Consolas", 9), 
                                              bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                                              selectbackground=self.colors['accent'], height=5)
        self.cc_workflow_listbox.pack(fill=tk.X, pady=(0, 10))
        
        presets = ["Basic Text Overlay", "Split and Trim", "Add Zoom Keyframe", "Export 1080p"]
        for preset in presets:
            self.cc_workflow_listbox.insert(tk.END, preset)
        
        wf_btns = tk.Frame(workflow_frame, bg=self.colors['bg_medium'])
        wf_btns.pack(fill=tk.X)
        
        tk.Button(wf_btns, text="▶ Run Selected", command=self._cc_run_workflow,
                  bg=self.colors['success'], fg='white',
                  activebackground='#00d9a5', activeforeground='white',
                  relief=tk.FLAT, padx=12, pady=5).pack(side=tk.LEFT, padx=3)
        
        tk.Button(wf_btns, text="📂 Load Custom", command=self._cc_load_workflow,
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=12, pady=5).pack(side=tk.LEFT, padx=3)
        
        # === Log Panel ===
        log_label = tk.Label(
            right_panel, text="📋 Activity Log",
            font=("Segoe UI", 11, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_dark']
        )
        log_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.cc_log = scrolledtext.ScrolledText(
            right_panel,
            font=("Consolas", 9),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_primary'],
            insertbackground='white',
            wrap=tk.WORD,
            state=tk.NORMAL
        )
        self.cc_log.pack(fill=tk.BOTH, expand=True)
        
        clear_btn = tk.Button(
            right_panel, text="Clear Log", command=lambda: self.cc_log.delete(1.0, tk.END),
            bg=self.colors['bg_light'], fg=self.colors['text_primary'],
            activebackground=self.colors['accent'], activeforeground='white',
            relief=tk.FLAT, padx=10, pady=3
        )
        clear_btn.pack(anchor=tk.E, pady=(5, 0))
    
    # CapCut callbacks
    def _cc_find(self):
        is_running = self.cc_engine.find_capcut()
        status = "Running" if is_running else "Not running"
        color = self.colors['success'] if is_running else self.colors['text_secondary']
        self.cc_status_label.config(text=f"Status: {status}", fg=color)
    
    def _cc_launch(self):
        self.set_status('processing', 'Launching CapCut...')
        threading.Thread(target=lambda: (self.cc_engine.launch_capcut(), self.set_status('ready')), daemon=True).start()
    
    def _cc_stop(self):
        self.cc_engine.stop_all()
        self.set_status('ready', 'Stopped')
    
    def _cc_add_text(self):
        text = self.cc_text_entry.get()
        if text and text != "Enter text to add...":
            threading.Thread(target=lambda: self.cc_engine.add_text(text), daemon=True).start()
    
    def _cc_set_speed(self):
        try:
            speed = float(self.cc_speed_entry.get())
            threading.Thread(target=lambda: self.cc_engine.set_speed(speed), daemon=True).start()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid speed value")
    
    def _cc_apply_mask(self):
        mask_type = self.cc_mask_var.get()
        threading.Thread(target=lambda: self.cc_engine.apply_mask(mask_type), daemon=True).start()
    
    def _cc_import(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Media files", "*.mp4 *.avi *.mov *.mkv *.mp3 *.wav *.png *.jpg"), ("All files", "*.*")]
        )
        if filepath:
            threading.Thread(target=lambda: self.cc_engine.import_media(filepath), daemon=True).start()
    
    def _cc_export(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        if filepath:
            threading.Thread(target=lambda: self.cc_engine.export_video(filepath), daemon=True).start()
    
    def _cc_run_workflow(self):
        selection = self.cc_workflow_listbox.curselection()
        if selection:
            preset = self.cc_workflow_listbox.get(selection[0])
            threading.Thread(target=lambda: self.cc_engine.run_preset_workflow(preset), daemon=True).start()
    
    def _cc_load_workflow(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filepath:
            steps = self.cc_engine.load_workflow(filepath)
            if steps:
                threading.Thread(target=lambda: self.cc_engine.execute_custom_workflow(steps), daemon=True).start()
    
    # ==================== TAB 4: AI COMMANDS ====================
    def _create_ai_commands_tab(self):
        """Create AI Command Center tab"""
        tab = tk.Frame(self.notebook, bg=self.colors['bg_dark'])
        self.notebook.add(tab, text="🤖 AI Commands")
        
        # Left panel (controls)
        left_panel = tk.Frame(tab, bg=self.colors['bg_dark'], width=620)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        left_panel.pack_propagate(False)
        
        # Right panel (results)
        right_panel = tk.Frame(tab, bg=self.colors['bg_dark'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === Command Input Section ===
        cmd_frame = tk.LabelFrame(
            left_panel, text="💬 Natural Language Command",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium'],
            padx=15, pady=15
        )
        cmd_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Large text input
        self.ai_cmd_text = scrolledtext.ScrolledText(
            cmd_frame,
            font=("Consolas", 11),
            bg=self.colors['bg_light'],
            fg=self.colors['text_primary'],
            insertbackground='white',
            wrap=tk.WORD,
            height=4
        )
        self.ai_cmd_text.pack(fill=tk.X, pady=(0, 15))
        self.ai_cmd_text.insert("1.0", "Add text 'Welcome to my channel' to my CapCut video, then export it")
        
        # Action buttons
        btn_frame = tk.Frame(cmd_frame, bg=self.colors['bg_medium'])
        btn_frame.pack(fill=tk.X)
        
        tk.Button(btn_frame, text="▶ Execute Command", command=self._ai_execute,
                  bg=self.colors['success'], fg='white',
                  activebackground='#00d9a5', activeforeground='white',
                  relief=tk.FLAT, padx=15, pady=8, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=3)
        
        tk.Button(btn_frame, text="🔍 Parse Only", command=self._ai_parse,
                  bg=self.colors['warning'], fg='black',
                  activebackground='#ffeaa7', activeforeground='black',
                  relief=tk.FLAT, padx=15, pady=8).pack(side=tk.LEFT, padx=3)
        
        tk.Button(btn_frame, text="⚡ Quick Execute", command=self._ai_quick_execute,
                  bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                  activebackground=self.colors['accent'], activeforeground='white',
                  relief=tk.FLAT, padx=15, pady=8).pack(side=tk.LEFT, padx=3)
        
        # === Quick Commands Listbox ===
        quick_frame = tk.LabelFrame(
            left_panel, text="⚡ Quick Commands (Double-click)",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium'],
            padx=15, pady=15
        )
        quick_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.ai_quick_list = tk.Listbox(quick_frame, font=("Consolas", 9),
                                        bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                                        selectbackground=self.colors['accent'], height=8)
        self.ai_quick_list.pack(fill=tk.X, pady=(0, 10))
        
        quick_cmds = [
            "Split clip at playhead in CapCut",
            "Add text 'Subscribe!' to video",
            "Change playback speed to 2x",
            "Export video at 1080p",
            "Create video project 'My_Vlog'",
            "Organize downloads folder by type",
            "Take a screenshot",
            "Move mouse to 500 300 and click",
            "Type 'Hello World' and press enter",
        ]
        for cmd in quick_cmds:
            self.ai_quick_list.insert(tk.END, cmd)
        
        self.ai_quick_list.bind('<Double-Button-1>', self._ai_on_quick_select)
        
        # === Help Button ===
        help_btn = tk.Button(
            left_panel, text="❓ Show Help / Available Commands",
            command=self._ai_show_help,
            bg=self.colors['bg_light'], fg=self.colors['text_primary'],
            activebackground=self.colors['accent'], activeforeground='white',
            relief=tk.FLAT, padx=15, pady=8
        )
        help_btn.pack(fill=tk.X, pady=(0, 10))
        
        # === Result Display ===
        result_label = tk.Label(
            right_panel, text="📊 Command Interpretation & Results",
            font=("Segoe UI", 11, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_dark']
        )
        result_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.ai_result = scrolledtext.ScrolledText(
            right_panel,
            font=("Consolas", 9),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_primary'],
            insertbackground='white',
            wrap=tk.WORD,
            state=tk.NORMAL
        )
        self.ai_result.pack(fill=tk.BOTH, expand=True)
        
        clear_btn = tk.Button(
            right_panel, text="Clear", command=lambda: self.ai_result.delete(1.0, tk.END),
            bg=self.colors['bg_light'], fg=self.colors['text_primary'],
            activebackground=self.colors['accent'], activeforeground='white',
            relief=tk.FLAT, padx=10, pady=3
        )
        clear_btn.pack(anchor=tk.E, pady=(5, 0))
    
    # AI Command callbacks
    def _ai_on_quick_select(self, event):
        selection = self.ai_quick_list.curselection()
        if selection:
            cmd = self.ai_quick_list.get(selection[0])
            self.ai_cmd_text.delete("1.0", tk.END)
            self.ai_cmd_text.insert("1.0", cmd)
    
    def _ai_execute(self):
        command = self.ai_cmd_text.get("1.0", tk.END).strip()
        if not command:
            messagebox.showinfo("Info", "Please enter a command")
            return
        
        self.set_status('processing', 'Processing with AI...')
        self.ai_result.delete("1.0", tk.END)
        self.ai_result.insert("1.0", "🔄 Processing command...\n\n")
        
        def process():
            try:
                result = self.ai_engine.process_command(command)
                self.root.after(0, lambda: self._ai_display_result(result, execute=True))
            except Exception as e:
                self.root.after(0, lambda: self.ai_result.insert(tk.END, f"❌ Error: {e}\n"))
            finally:
                self.root.after(0, lambda: self.set_status('ready'))
        
        threading.Thread(target=process, daemon=True).start()
    
    def _ai_parse(self):
        command = self.ai_cmd_text.get("1.0", tk.END).strip()
        if not command:
            messagebox.showinfo("Info", "Please enter a command")
            return
        
        self.ai_result.delete("1.0", tk.END)
        self.ai_result.insert("1.0", "🔍 Parsing command (no execution)...\n\n")
        
        result = self.ai_engine.process_command(command)
        self._ai_display_result(result, execute=False)
    
    def _ai_quick_execute(self):
        command = self.ai_cmd_text.get("1.0", tk.END).strip()
        if not command:
            messagebox.showinfo("Info", "Please enter a command")
            return
        
        self.set_status('processing', 'Quick executing...')
        self.ai_result.delete("1.0", tk.END)
        
        # Use rule-based parsing only (faster)
        result = self.ai_engine._process_rule_based(command)
        self._ai_display_result(result, execute=True)
        self.set_status('ready')
    
    def _ai_display_result(self, result, execute=False):
        """Display parsed result and optionally execute"""
        r = self.ai_result
        
        r.insert(tk.END, "=" * 50 + "\n")
        r.insert(tk.END, f"📋 INTERPRETATION\n")
        r.insert(tk.END, "=" * 50 + "\n")
        r.insert(tk.END, f"{result.get('interpretation', 'No interpretation')}\n\n")
        
        # Actions
        actions = result.get('actions', [])
        if actions:
            r.insert(tk.END, f"\n🖱️ MOUSE/KEYBOARD ACTIONS ({len(actions)})\n")
            r.insert(tk.END, "-" * 40 + "\n")
            for action in actions:
                atype = action.get('type', 'unknown')
                details = action.get('details', {})
                r.insert(tk.END, f"  • {atype}: {details}\n")
                
                if execute:
                    self._ai_execute_action(action)
        
        # CapCut steps
        capcut = result.get('capcut_steps', [])
        if capcut:
            r.insert(tk.END, f"\n🎬 CAPCUT STEPS ({len(capcut)})\n")
            r.insert(tk.END, "-" * 40 + "\n")
            for step in capcut:
                stype = step.get('type', 'unknown')
                details = step.get('details', {})
                r.insert(tk.END, f"  • {stype}: {details}\n")
                
                if execute:
                    self._ai_execute_capcut_step(step)
        
        # File operations
        file_ops = result.get('file_operations', [])
        if file_ops:
            r.insert(tk.END, f"\n📁 FILE OPERATIONS ({len(file_ops)})\n")
            r.insert(tk.END, "-" * 40 + "\n")
            for op in file_ops:
                otype = op.get('type', 'unknown')
                details = op.get('details', {})
                r.insert(tk.END, f"  • {otype}: {details}\n")
                
                if execute:
                    self._ai_execute_file_op(op)
        
        # Tips
        tips = result.get('tips', [])
        if tips:
            r.insert(tk.END, f"\n💡 TIPS\n")
            r.insert(tk.END, "-" * 40 + "\n")
            for tip in tips:
                r.insert(tk.END, f"  ⚠ {tip}\n")
        
        r.insert(tk.END, "\n" + "=" * 50 + "\n")
        if execute:
            r.insert(tk.END, "✅ Execution completed!\n")
        else:
            r.insert(tk.END, "ℹ️ Parse only mode - no actions executed\n")
    
    def _ai_execute_action(self, action):
        """Execute a mouse/keyboard action"""
        try:
            atype = action.get('type')
            details = action.get('details', {})
            
            if atype == 'mouse_move':
                x, y = details.get('x', 0), details.get('y', 0)
                self.mk_engine.move_mouse(x, y)
            elif atype == 'mouse_click':
                x, y = details.get('x'), details.get('y')
                button = details.get('button', 'left')
                if button == 'right':
                    self.mk_engine.right_click(x, y)
                else:
                    self.mk_engine.left_click(x, y)
            elif atype == 'key_type':
                text = details.get('text', '')
                self.mk_engine.type_text(text)
            elif atype == 'key_press':
                key = details.get('key', '')
                self.mk_engine.press_hotkey(key)
            elif atype == 'screenshot':
                self.mk_engine.take_screenshot()
            elif atype == 'wait':
                import time
                time.sleep(details.get('seconds', 1))
        except Exception as e:
            self.log_general(f"Action execution error: {e}")
    
    def _ai_execute_capcut_step(self, step):
        """Execute a CapCut step"""
        try:
            stype = step.get('type')
            details = step.get('details', {})
            
            if stype == 'split':
                self.cc_engine.split_clip()
            elif stype == 'text':
                content = details.get('content', 'Text')
                self.cc_engine.add_text(content)
            elif stype == 'delete':
                self.cc_engine.delete_selected()
            elif stype == 'speed':
                value = details.get('value', 1)
                self.cc_engine.set_speed(value)
            elif stype == 'export':
                self.cc_engine.export_video()
            elif stype == 'play':
                self.cc_engine.play_pause()
            elif stype == 'undo':
                self.cc_engine.undo()
        except Exception as e:
            self.log_general(f"CapCut step error: {e}")
    
    def _ai_execute_file_op(self, op):
        """Execute a file operation"""
        try:
            otype = op.get('type')
            details = op.get('details', {})
            
            if otype == 'organize':
                method = details.get('method', 'type')
                path = os.path.expanduser("~")
                if method == 'type':
                    self.fm_engine.organize_by_type(path, dry_run=False)
                else:
                    self.fm_engine.organize_by_date(path, dry_run=False)
            elif otype == 'create_project':
                name = details.get('name', 'MyProject')
                path = os.path.expanduser("~")
                self.fm_engine.create_video_project(path, name)
            elif otype == 'find':
                exts = details.get('extensions', [])
                path = os.path.expanduser("~")
                self.fm_engine.find_by_extension(path, ','.join(exts))
        except Exception as e:
            self.log_general(f"File op error: {e}")
    
    def _ai_show_help(self):
        """Show help dialog with available commands"""
        help_text = """
╔═══════════════════════════════════════════════════╗
║     🤖 AI AUTOMATION STUDIO - HELP GUIDE          ║
╚═══════════════════════════════════════════════════╝

🖱️ MOUSE COMMANDS:
  • "move mouse to X Y" - Move to coordinates
  • "click at X Y" - Click at position
  • "right click" - Right click
  • "double click" - Double click

⌨️ KEYBOARD COMMANDS:
  • "type 'text'" - Type text
  • "press enter" - Press Enter key
  • "press ctrl+c" - Press hotkey

🎬 CAPCUT COMMANDS:
  • "split clip" - Split at playhead
  • "add text 'hello'" - Add text overlay
  • "speed to 2x" - Set playback speed
  • "export video" - Export video
  • "export 4k" - Export at 4K
  • "undo" - Undo last action

📁 FILE COMMANDS:
  • "organize files by type" - Sort into folders
  • "organize by date" - Sort by date
  • "create project 'MyVlog'" - Create video project
  • "find mp4 files" - Search for files

📸 OTHER:
  • "take screenshot" - Capture screen
  • "wait 2 seconds" - Pause

💡 TIPS:
  • Double-click quick commands to fill input
  • Use "Parse Only" to preview actions
  • Move mouse to corner to emergency stop
  • Works without AI SDK (rule-based fallback)
"""
        messagebox.showinfo("AI Automation Studio - Help", help_text)


# ==================== MAIN ENTRY POINT ====================
def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = AIAutomationStudio(root)
    root.mainloop()


if __name__ == "__main__":
    main()
