"""
Mouse & Keyboard Automation Engine
Handles mouse movements, clicks, keyboard input, and macro recording/playback
"""

import pyautogui
import json
import time
import threading
from datetime import datetime
from pynput import mouse, keyboard

# Enable failsafe - move mouse to corner to stop
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1


class MouseKeyboardEngine:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback or (lambda msg: None)
        self.recording = False
        self.recorded_actions = []
        self.listener = None
        self.keyboard_listener = None
        self._stop_recording = False
        
    def log(self, message):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_callback(f"[{timestamp}] {message}")
    
    def get_mouse_position(self):
        """Get current mouse position"""
        x, y = pyautogui.position()
        return x, y
    
    def move_mouse(self, x, y, duration=0.5):
        """Move mouse to specified coordinates"""
        try:
            pyautogui.moveTo(x, y, duration)
            self.log(f"Mouse moved to ({x}, {y})")
            return True
        except Exception as e:
            self.log(f"Error moving mouse: {e}")
            return False
    
    def left_click(self, x=None, y=None):
        """Perform left click at specified or current position"""
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y)
            else:
                pyautogui.click()
            self.log(f"Left click at ({x or 'current'}, {y or 'current'})")
            return True
        except Exception as e:
            self.log(f"Error clicking: {e}")
            return False
    
    def right_click(self, x=None, y=None):
        """Perform right click at specified or current position"""
        try:
            if x is not None and y is not None:
                pyautogui.rightClick(x, y)
            else:
                pyautogui.rightClick()
            self.log(f"Right click at ({x or 'current'}, {y or 'current'})")
            return True
        except Exception as e:
            self.log(f"Error right clicking: {e}")
            return False
    
    def double_click(self, x=None, y=None):
        """Perform double click at specified or current position"""
        try:
            if x is not None and y is not None:
                pyautogui.doubleClick(x, y)
            else:
                pyautogui.doubleClick()
            self.log(f"Double click at ({x or 'current'}, {y or 'current'})")
            return True
        except Exception as e:
            self.log(f"Error double clicking: {e}")
            return False
    
    def drag_mouse(self, x1, y1, x2, y2, duration=1.0):
        """Drag mouse from one position to another"""
        try:
            pyautogui.moveTo(x1, y1)
            pyautogui.dragTo(x2, y2, duration)
            self.log(f"Dragged from ({x1}, {y1}) to ({x2}, {y2})")
            return True
        except Exception as e:
            self.log(f"Error dragging: {e}")
            return False
    
    def scroll(self, amount, x=None, y=None):
        """Scroll up (positive) or down (negative)"""
        try:
            if x is not None and y is not None:
                pyautogui.scroll(amount, x, y)
            else:
                pyautogui.scroll(amount)
            direction = "up" if amount > 0 else "down"
            self.log(f"Scrolled {direction} by {abs(amount)}")
            return True
        except Exception as e:
            self.log(f"Error scrolling: {e}")
            return False
    
    def type_text(self, text, interval=0.05):
        """Type text character by character"""
        try:
            pyautogui.write(text, interval=interval)
            self.log(f"Typed: {text[:50]}{'...' if len(text) > 50 else ''}")
            return True
        except Exception as e:
            self.log(f"Error typing: {e}")
            return False
    
    def press_hotkey(self, hotkey):
        """Press a hotkey combination like 'ctrl+c' or 'alt+tab'"""
        try:
            keys = hotkey.lower().replace(' ', '').split('+')
            pyautogui.hotkey(*keys)
            self.log(f"Pressed hotkey: {hotkey}")
            return True
        except Exception as e:
            self.log(f"Error pressing hotkey: {e}")
            return False
    
    def take_screenshot(self, filepath=None):
        """Take a screenshot and save it"""
        try:
            if filepath is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = f"screenshot_{timestamp}.png"
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            self.log(f"Screenshot saved to: {filepath}")
            return filepath
        except Exception as e:
            self.log(f"Error taking screenshot: {e}")
            return None
    
    # Macro Recording Functions
    def start_recording(self):
        """Start recording mouse and keyboard actions"""
        self.recorded_actions = []
        self.recording = True
        self._stop_recording = False
        self.start_time = time.time()
        
        def on_move(x, y):
            if self.recording and not self._stop_recording:
                elapsed = time.time() - self.start_time
                self.recorded_actions.append({
                    'type': 'move',
                    'x': x,
                    'y': y,
                    'time': elapsed
                })
        
        def on_click(x, y, button, pressed):
            if self.recording and not self._stop_recording and pressed:
                elapsed = time.time() - self.start_time
                action_type = 'click'
                if button == mouse.Button.left:
                    action_type = 'left_click'
                elif button == mouse.Button.right:
                    action_type = 'right_click'
                self.recorded_actions.append({
                    'type': action_type,
                    'x': x,
                    'y': y,
                    'time': elapsed
                })
        
        def on_scroll(x, y, dx, dy):
            if self.recording and not self._stop_recording:
                elapsed = time.time() - self.start_time
                self.recorded_actions.append({
                    'type': 'scroll',
                    'x': x,
                    'y': y,
                    'amount': dy,
                    'time': elapsed
                })
        
        def on_press(key):
            if self.recording and not self._stop_recording:
                elapsed = time.time() - self.start_time
                try:
                    key_name = key.char if hasattr(key, 'char') and key.char else str(key).replace('Key.', '')
                    self.recorded_actions.append({
                        'type': 'key_press',
                        'key': key_name,
                        'time': elapsed
                    })
                except AttributeError:
                    pass
        
        self.mouse_listener = mouse.Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll
        )
        self.keyboard_listener = keyboard.Listener(on_press=on_press)
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        self.log("Recording started...")
        return True
    
    def stop_recording(self):
        """Stop recording"""
        self._stop_recording = True
        self.recording = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        elapsed = time.time() - self.start_time
        self.log(f"Recording stopped. {len(self.recorded_actions)} actions recorded in {elapsed:.2f}s")
        return self.recorded_actions
    
    def play_macro(self, actions, speed=1.0, loop=False, stop_event=None):
        """Play back recorded macro actions"""
        if not actions:
            self.log("No actions to play")
            return False
        
        iteration = 0
        while True:
            if stop_event and stop_event.is_set():
                self.log("Playback stopped by user")
                break
            
            for i, action in enumerate(actions):
                if stop_event and stop_event.is_set():
                    break
                
                action_type = action.get('type')
                
                try:
                    if action_type == 'move':
                        pyautogui.moveTo(action['x'], action['y'], duration=0.1/speed)
                    elif action_type == 'left_click':
                        pyautogui.click(action['x'], action['y'])
                    elif action_type == 'right_click':
                        pyautogui.rightClick(action['x'], action['y'])
                    elif action_type == 'scroll':
                        pyautogui.scroll(int(action['amount']), action['x'], action['y'])
                    elif action_type == 'key_press':
                        pyautogui.press(action['key'])
                    
                    # Wait between actions based on timing and speed
                    if i < len(actions) - 1:
                        wait_time = (actions[i+1]['time'] - action['time']) / speed
                        if wait_time > 0:
                            time.sleep(min(wait_time, 2.0))  # Cap wait time at 2 seconds
                except Exception as e:
                    self.log(f"Error playing action {i}: {e}")
            
            iteration += 1
            if not loop:
                break
            
            self.log(f"Completed iteration {iteration}")
        
        self.log("Playback finished")
        return True
    
    def save_macro(self, filepath, actions=None):
        """Save macro to JSON file"""
        if actions is None:
            actions = self.recorded_actions
        try:
            with open(filepath, 'w') as f:
                json.dump(actions, f, indent=2)
            self.log(f"Macro saved to: {filepath}")
            return True
        except Exception as e:
            self.log(f"Error saving macro: {e}")
            return False
    
    def load_macro(self, filepath):
        """Load macro from JSON file"""
        try:
            with open(filepath, 'r') as f:
                actions = json.load(f)
            self.log(f"Macro loaded from: {filepath} ({len(actions)} actions)")
            return actions
        except Exception as e:
            self.log(f"Error loading macro: {e}")
            return None
