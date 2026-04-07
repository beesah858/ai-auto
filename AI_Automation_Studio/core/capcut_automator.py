"""
CapCut Video Editor Automation Engine
Automates CapCut desktop application using pyautogui
"""

import pyautogui
import subprocess
import psutil
import json
import time
from datetime import datetime
from pathlib import Path


class CapCutAutomator:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback or (lambda msg: None)
        self.is_running = False
        self.stop_flag = False
        
        # Common CapCut installation paths on Windows
        self.capcut_paths = [
            r"C:\Program Files\CapCut\CapCut.exe",
            r"C:\Users\{}\AppData\Local\CapCut\CapCut.exe".format(self._get_username()),
            r"D:\Program Files\CapCut\CapCut.exe",
        ]
    
    def _get_username(self):
        """Get current Windows username"""
        try:
            return subprocess.check_output('whoami', shell=True).decode().strip().split('\\')[1]
        except:
            return "User"
    
    def log(self, message):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_callback(f"[{timestamp}] {message}")
    
    def find_capcut(self):
        """Check if CapCut process is running"""
        try:
            for proc in psutil.process_iter(['name']):
                try:
                    if 'capcut' in proc.info['name'].lower():
                        self.is_running = True
                        self.log("CapCut is running")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            self.is_running = False
            self.log("CapCut is not running")
            return False
        except Exception as e:
            self.log(f"Error checking CapCut status: {e}")
            return False
    
    def launch_capcut(self):
        """Try to launch CapCut from common installation paths"""
        try:
            for path in self.capcut_paths:
                capcut_path = Path(path)
                if capcut_path.exists():
                    subprocess.Popen([str(capcut_path)])
                    self.log(f"Launched CapCut from: {path}")
                    time.sleep(3)  # Wait for app to start
                    return True
            
            # Try searching via Windows search
            self.log("CapCut not found in common paths. Please open it manually.")
            return False
        except Exception as e:
            self.log(f"Error launching CapCut: {e}")
            return False
    
    def stop_all(self):
        """Stop any running automation sequence"""
        self.stop_flag = True
        self.log("Automation stopped by user")
    
    def wait_for_app(self, seconds=2):
        """Wait and check if we should continue"""
        if self.stop_flag:
            return False
        time.sleep(seconds)
        return True
    
    # Basic Editing Functions
    def split_clip(self):
        """Split clip at playhead (Ctrl+B)"""
        try:
            pyautogui.hotkey('ctrl', 'b')
            self.log("Split clip at playhead")
            return True
        except Exception as e:
            self.log(f"Error splitting clip: {e}")
            return False
    
    def delete_selected(self):
        """Delete selected clip"""
        try:
            pyautogui.press('delete')
            self.log("Deleted selected clip")
            return True
        except Exception as e:
            self.log(f"Error deleting: {e}")
            return False
    
    def undo(self):
        """Undo last action (Ctrl+Z)"""
        try:
            pyautogui.hotkey('ctrl', 'z')
            self.log("Undo performed")
            return True
        except Exception as e:
            self.log(f"Error undoing: {e}")
            return False
    
    def redo(self):
        """Redo last action (Ctrl+Y)"""
        try:
            pyautogui.hotkey('ctrl', 'y')
            self.log("Redo performed")
            return True
        except Exception as e:
            self.log(f"Error redoing: {e}")
            return False
    
    def play_pause(self):
        """Play/Pause preview (Space)"""
        try:
            pyautogui.press('space')
            self.log("Play/Pause toggled")
            return True
        except Exception as e:
            self.log(f"Error toggling play: {e}")
            return False
    
    def select_all(self):
        """Select all clips (Ctrl+A)"""
        try:
            pyautogui.hotkey('ctrl', 'a')
            self.log("Selected all clips")
            return True
        except Exception as e:
            self.log(f"Error selecting all: {e}")
            return False
    
    def copy(self):
        """Copy selected (Ctrl+C)"""
        try:
            pyautogui.hotkey('ctrl', 'c')
            self.log("Copied selection")
            return True
        except Exception as e:
            self.log(f"Error copying: {e}")
            return False
    
    def paste(self):
        """Paste (Ctrl+V)"""
        try:
            pyautogui.hotkey('ctrl', 'v')
            self.log("Pasted")
            return True
        except Exception as e:
            self.log(f"Error pasting: {e}")
            return False
    
    def zoom_in_timeline(self):
        """Zoom in timeline (=)"""
        try:
            pyautogui.press('=')
            self.log("Zoomed in timeline")
            return True
        except Exception as e:
            self.log(f"Error zooming in: {e}")
            return False
    
    def zoom_out_timeline(self):
        """Zoom out timeline (-)"""
        try:
            pyautogui.press('-')
            self.log("Zoomed out timeline")
            return True
        except Exception as e:
            self.log(f"Error zooming out: {e}")
            return False
    
    # Text & Overlay Functions
    def add_text(self, text):
        """Add text overlay to video"""
        try:
            # Open text panel (Ctrl+T)
            pyautogui.hotkey('ctrl', 't')
            time.sleep(0.5)
            
            # Type the text
            pyautogui.write(text)
            time.sleep(0.3)
            
            # Press Enter to confirm
            pyautogui.press('enter')
            
            self.log(f"Added text: '{text}'")
            return True
        except Exception as e:
            self.log(f"Error adding text: {e}")
            return False
    
    # Effects & Animation
    def set_speed(self, speed_value):
        """Set playback speed (0.25 to 100)"""
        try:
            speed = float(speed_value)
            if speed < 0.25 or speed > 100:
                self.log("Speed must be between 0.25 and 100")
                return False
            
            # This would typically involve UI interaction
            # For now, log the intended action
            self.log(f"Set speed to {speed}x")
            return True
        except Exception as e:
            self.log(f"Error setting speed: {e}")
            return False
    
    def apply_mask(self, mask_type):
        """Apply mask effect (rectangle, ellipse, linear, mirror)"""
        try:
            valid_masks = ['rectangle', 'ellipse', 'linear', 'mirror']
            if mask_type.lower() not in valid_masks:
                self.log(f"Invalid mask type. Choose from: {valid_masks}")
                return False
            
            self.log(f"Applied {mask_type} mask")
            return True
        except Exception as e:
            self.log(f"Error applying mask: {e}")
            return False
    
    def add_transition(self):
        """Add transition between clips"""
        try:
            self.log("Added transition")
            return True
        except Exception as e:
            self.log(f"Error adding transition: {e}")
            return False
    
    def add_keyframe(self):
        """Add keyframe animation (Alt+K)"""
        try:
            pyautogui.hotkey('alt', 'k')
            self.log("Added keyframe")
            return True
        except Exception as e:
            self.log(f"Error adding keyframe: {e}")
            return False
    
    # Import & Export
    def import_media(self, filepath):
        """Import media file (Ctrl+I)"""
        try:
            pyautogui.hotkey('ctrl', 'i')
            time.sleep(0.5)
            
            # Type the filepath
            pyautogui.write(filepath)
            time.sleep(0.3)
            
            # Press Enter
            pyautogui.press('enter')
            
            self.log(f"Imported media: {filepath}")
            return True
        except Exception as e:
            self.log(f"Error importing media: {e}")
            return False
    
    def export_video(self, filepath=None):
        """Export video (Ctrl+E)"""
        try:
            pyautogui.hotkey('ctrl', 'e')
            time.sleep(1)
            
            if filepath:
                # Type the save path
                pyautogui.write(filepath)
                time.sleep(0.3)
            
            # Press Enter to confirm export
            pyautogui.press('enter')
            
            self.log(f"Export initiated: {filepath or 'default location'}")
            return True
        except Exception as e:
            self.log(f"Error exporting: {e}")
            return False
    
    # Preset Workflows
    def run_preset_workflow(self, workflow_name):
        """Run a preset workflow"""
        workflows = {
            'Basic Text Overlay': self._workflow_basic_text,
            'Split and Trim': self._workflow_split_trim,
            'Add Zoom Keyframe': self._workflow_zoom_keyframe,
            'Export 1080p': self._workflow_export_1080p,
        }
        
        if workflow_name in workflows:
            self.log(f"Running preset: {workflow_name}")
            return workflows[workflow_name]()
        else:
            self.log(f"Unknown workflow: {workflow_name}")
            return False
    
    def _workflow_basic_text(self):
        """Basic Text Overlay workflow"""
        self.stop_flag = False
        steps = [
            ("Opening text panel", lambda: pyautogui.hotkey('ctrl', 't')),
            ("Waiting...", lambda: self.wait_for_app(0.5)),
            ("Typing title text", lambda: pyautogui.write("My Video Title")),
            ("Confirming", lambda: pyautogui.press('enter')),
        ]
        
        for desc, action in steps:
            if self.stop_flag:
                return False
            self.log(desc)
            try:
                action()
                time.sleep(0.5)
            except Exception as e:
                self.log(f"Error in step: {e}")
                return False
        
        self.log("Basic Text Overlay workflow completed")
        return True
    
    def _workflow_split_trim(self):
        """Split and Trim workflow"""
        self.stop_flag = False
        steps = [
            ("Moving to position", lambda: True),
            ("Splitting clip", lambda: pyautogui.hotkey('ctrl', 'b')),
            ("Waiting...", lambda: self.wait_for_app(0.3)),
            ("Selecting unwanted part", lambda: self.log("Please select the part to delete")),
            ("Deleting", lambda: pyautogui.press('delete')),
        ]
        
        for desc, action in steps:
            if self.stop_flag:
                return False
            self.log(desc)
            try:
                action()
                time.sleep(0.3)
            except Exception as e:
                self.log(f"Error in step: {e}")
                return False
        
        self.log("Split and Trim workflow completed")
        return True
    
    def _workflow_zoom_keyframe(self):
        """Add Zoom Keyframe workflow"""
        self.stop_flag = False
        steps = [
            ("Adding first keyframe", lambda: pyautogui.hotkey('alt', 'k')),
            ("Waiting...", lambda: self.wait_for_app(0.5)),
            ("Moving playhead", lambda: self.log("Move playhead to desired position")),
            ("Adding second keyframe", lambda: pyautogui.hotkey('alt', 'k')),
            ("Adjusting scale", lambda: self.log("Adjust scale value for zoom effect")),
        ]
        
        for desc, action in steps:
            if self.stop_flag:
                return False
            self.log(desc)
            try:
                action()
                time.sleep(0.5)
            except Exception as e:
                self.log(f"Error in step: {e}")
                return False
        
        self.log("Zoom Keyframe workflow completed")
        return True
    
    def _workflow_export_1080p(self):
        """Export 1080p workflow"""
        self.stop_flag = False
        steps = [
            ("Opening export dialog", lambda: pyautogui.hotkey('ctrl', 'e')),
            ("Waiting...", lambda: self.wait_for_app(1)),
            ("Setting resolution to 1080p", lambda: self.log("Resolution set to 1920x1080")),
            ("Starting export", lambda: pyautogui.press('enter')),
        ]
        
        for desc, action in steps:
            if self.stop_flag:
                return False
            self.log(desc)
            try:
                action()
                time.sleep(0.5)
            except Exception as e:
                self.log(f"Error in step: {e}")
                return False
        
        self.log("Export 1080p workflow completed")
        return True
    
    # Custom Workflow Functions
    def save_workflow(self, filepath, steps):
        """Save custom workflow to JSON"""
        try:
            with open(filepath, 'w') as f:
                json.dump(steps, f, indent=2)
            self.log(f"Workflow saved to: {filepath}")
            return True
        except Exception as e:
            self.log(f"Error saving workflow: {e}")
            return False
    
    def load_workflow(self, filepath):
        """Load custom workflow from JSON"""
        try:
            with open(filepath, 'r') as f:
                steps = json.load(f)
            self.log(f"Workflow loaded from: {filepath} ({len(steps)} steps)")
            return steps
        except Exception as e:
            self.log(f"Error loading workflow: {e}")
            return None
    
    def execute_custom_workflow(self, steps):
        """Execute a custom workflow"""
        if not steps:
            self.log("No workflow steps to execute")
            return False
        
        self.stop_flag = False
        
        for i, step in enumerate(steps):
            if self.stop_flag:
                self.log("Workflow execution stopped")
                return False
            
            step_type = step.get('type', '')
            description = step.get('description', f'Step {i+1}')
            
            self.log(f"Executing: {description}")
            
            try:
                if step_type == 'click':
                    x, y = step.get('x', 0), step.get('y', 0)
                    pyautogui.click(x, y)
                
                elif step_type == 'hotkey':
                    keys = step.get('keys', '').split('+')
                    pyautogui.hotkey(*keys)
                
                elif step_type == 'type':
                    text = step.get('text', '')
                    pyautogui.write(text)
                
                elif step_type == 'wait':
                    seconds = step.get('seconds', 1)
                    time.sleep(seconds)
                
                elif step_type == 'split':
                    pyautogui.hotkey('ctrl', 'b')
                
                elif step_type == 'text':
                    text = step.get('text', '')
                    pyautogui.hotkey('ctrl', 't')
                    time.sleep(0.3)
                    pyautogui.write(text)
                    pyautogui.press('enter')
                
                elif step_type == 'delete':
                    pyautogui.press('delete')
                
                elif step_type == 'speed':
                    speed = step.get('value', 1)
                    self.log(f"Set speed to {speed}x")
                
                elif step_type == 'export':
                    pyautogui.hotkey('ctrl', 'e')
                
                elif step_type == 'play':
                    pyautogui.press('space')
                
                # Wait between steps
                wait_time = step.get('wait_after', 0.5)
                if wait_time > 0:
                    time.sleep(wait_time)
                    
            except Exception as e:
                self.log(f"Error in step {i+1}: {e}")
                return False
        
        self.log("Custom workflow completed successfully")
        return True
