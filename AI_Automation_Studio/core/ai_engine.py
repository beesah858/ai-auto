"""
AI-Powered Natural Language Command Processor
Processes user commands and converts them to automation actions
"""

import json
import re
from datetime import datetime


class AIEngine:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback or (lambda msg: None)
        self.sdk_available = False
        
        # Try to import the AI SDK
        try:
            from z_ai_web_dev_sdk import ChatCompletionsClient
            self.client = ChatCompletionsClient()
            self.sdk_available = True
            self.log("AI SDK loaded successfully")
        except ImportError:
            self.log("AI SDK not available, using rule-based parsing")
    
    def log(self, message):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_callback(f"[{timestamp}] {message}")
    
    def process_command(self, command):
        """
        Process a natural language command and return structured actions
        Returns a dict with: interpretation, actions[], capcut_steps[], file_operations[], tips
        """
        if self.sdk_available:
            return self._process_with_ai(command)
        else:
            return self._process_rule_based(command)
    
    def _process_with_ai(self, command):
        """Process command using AI SDK"""
        try:
            system_prompt = """You are an automation assistant. Analyze the user's command and return a JSON response with this exact structure:
{
    "interpretation": "Brief explanation of what the user wants",
    "actions": [{"type": "mouse_move"|"mouse_click"|"key_type"|"key_press"|"screenshot"|"wait", "details": {...}}],
    "capcut_steps": [{"type": "split"|"text"|"delete"|"speed"|"export"|"play"|"undo", "details": {...}}],
    "file_operations": [{"type": "organize"|"rename"|"create_project"|"find", "details": {...}}],
    "tips": ["Helpful tips for the user"]
}

Action types and their details:
- mouse_move: {"x": number, "y": number}
- mouse_click: {"x": number, "y": number, "button": "left"|"right"}
- key_type: {"text": "string"}
- key_press: {"key": "enter"|"ctrl+c"|"ctrl+v" etc}
- screenshot: {"filepath": "optional path"}
- wait: {"seconds": number}

CapCut step types:
- split: {}
- text: {"content": "text to add"}
- delete: {}
- speed: {"value": number}
- export: {"resolution": "1080p"|"4k" etc}
- play: {}
- undo: {}

File operation types:
- organize: {"method": "type"|"date", "path": "directory path"}
- rename: {"mode": "prefix"|"suffix" etc, "value": "value", "files": [...]}
- create_project: {"name": "project name", "path": "base path"}
- find: {"extensions": ["mp4", "png" etc], "path": "search path"}

Respond ONLY with valid JSON, no other text."""

            response = self.client.chat.completions.create(
                model="z-ai-web-dev",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Command: {command}\n\nReturn JSON response:"}
                ],
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response (in case there's extra text)
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(result_text)
            
            self.log("AI processed command successfully")
            return result
            
        except Exception as e:
            self.log(f"AI processing error: {e}")
            # Fallback to rule-based
            return self._process_rule_based(command)
    
    def _process_rule_based(self, command):
        """Process command using rule-based parsing (fallback)"""
        cmd_lower = command.lower()
        
        result = {
            "interpretation": self._generate_interpretation(cmd_lower),
            "actions": [],
            "capcut_steps": [],
            "file_operations": [],
            "tips": []
        }
        
        # Mouse movement commands
        move_match = re.search(r'move\s+(?:mouse\s+)?to\s+(\d+)\s*[,\s]\s*(\d+)', cmd_lower)
        if move_match:
            x, y = int(move_match.group(1)), int(move_match.group(2))
            result["actions"].append({"type": "mouse_move", "details": {"x": x, "y": y}})
        
        # Click commands
        click_match = re.search(r'click\s+(?:at\s+)?(?:x[=:\s]*(\d+)[,\s]*)?\s*(?:y[=:\s]*(\d+))?', cmd_lower)
        if click_match or 'click' in cmd_lower:
            x = click_match.group(1) if click_match and click_match.group(1) else None
            y = click_match.group(2) if click_match and click_match.group(2) else None
            button = "right" if "right" in cmd_lower else "left"
            result["actions"].append({
                "type": "mouse_click", 
                "details": {"x": int(x) if x else None, "y": int(y) if y else None, "button": button}
            })
        
        # Type commands
        type_match = re.search(r"type\s+['\"](.+?)['\"]", cmd_lower)
        if type_match:
            result["actions"].append({"type": "key_type", "details": {"text": type_match.group(1)}})
        
        # Key press commands
        if 'press enter' in cmd_lower:
            result["actions"].append({"type": "key_press", "details": {"key": "enter"}})
        if 'press esc' in cmd_lower or 'escape' in cmd_lower:
            result["actions"].append({"type": "key_press", "details": {"key": "esc"}})
        
        # Screenshot command
        if 'screenshot' in cmd_lower or 'take snapshot' in cmd_lower:
            result["actions"].append({"type": "screenshot", "details": {}})
        
        # Wait command
        wait_match = re.search(r'wait\s+(\d+(?:\.\d+)?)\s*(?:second|sec|s)', cmd_lower)
        if wait_match:
            result["actions"].append({"type": "wait", "details": {"seconds": float(wait_match.group(1))}})
        
        # CapCut commands
        if 'split' in cmd_lower and ('clip' in cmd_lower or 'video' in cmd_lower or 'capcut' in cmd_lower):
            result["capcut_steps"].append({"type": "split", "details": {}})
        
        # Add text to CapCut
        text_match = re.search(r'add\s+text\s+[\'"](.+?)[\'"]', cmd_lower)
        if text_match or ('add text' in cmd_lower and 'capcut' in cmd_lower):
            content = text_match.group(1) if text_match else "New Text"
            result["capcut_steps"].append({"type": "text", "details": {"content": content}})
        
        # Speed change
        speed_match = re.search(r'(?:speed|playback)\s+(?:to\s+)?(\d+(?:\.\d+)?)\s*x', cmd_lower)
        if speed_match:
            result["capcut_steps"].append({"type": "speed", "details": {"value": float(speed_match.group(1))}})
        
        # Export video
        if 'export' in cmd_lower and ('video' in cmd_lower or 'capcut' in cmd_lower):
            resolution = "1080p"
            if '4k' in cmd_lower:
                resolution = "4k"
            elif '720p' in cmd_lower:
                resolution = "720p"
            result["capcut_steps"].append({"type": "export", "details": {"resolution": resolution}})
        
        # Play/Pause
        if 'play' in cmd_lower or 'pause' in cmd_lower:
            if 'capcut' in cmd_lower or 'video' in cmd_lower:
                result["capcut_steps"].append({"type": "play", "details": {}})
        
        # Undo
        if 'undo' in cmd_lower:
            result["capcut_steps"].append({"type": "undo", "details": {}})
        
        # File operations
        if 'organize' in cmd_lower and ('file' in cmd_lower or 'folder' in cmd_lower):
            method = "type" if "type" in cmd_lower else "date"
            result["file_operations"].append({"type": "organize", "details": {"method": method}})
        
        # Create video project
        project_match = re.search(r'create\s+(?:video\s+)?project\s+[\'"]?(.+?)[\'"]?', cmd_lower)
        if project_match or 'create project' in cmd_lower:
            name = project_match.group(1) if project_match else "MyProject"
            result["file_operations"].append({"type": "create_project", "details": {"name": name}})
        
        # Find files by extension
        find_match = re.search(r'find\s+(?:files?\s+)?(?:with\s+)?(?:extension|ext)[\s:]+(.+?)(?:\.|$|\s)', cmd_lower)
        if find_match:
            exts = [e.strip() for e in find_match.group(1).replace(',', ' ').split()]
            result["file_operations"].append({"type": "find", "details": {"extensions": exts}})
        
        # Generate tips based on detected actions
        if result["capcut_steps"]:
            result["tips"].append("Make sure CapCut is open and active before running these commands")
        if result["actions"]:
            result["tips"].append("Move your mouse to the corner of the screen to emergency stop automation")
        if result["file_operations"]:
            result["tips"].append("Consider enabling DRY RUN mode before applying file operations")
        
        self.log(f"Rule-based parsing detected {len(result['actions'])} actions, {len(result['capcut_steps'])} CapCut steps")
        return result
    
    def _generate_interpretation(self, cmd_lower):
        """Generate a human-readable interpretation of the command"""
        interpretations = []
        
        if 'mouse' in cmd_lower or 'click' in cmd_lower:
            interpretations.append("Mouse control action")
        if 'type' in cmd_lower or 'keyboard' in cmd_lower:
            interpretations.append("Keyboard input action")
        if 'capcut' in cmd_lower or 'video' in cmd_lower:
            interpretations.append("CapCut video editing")
        if 'text' in cmd_lower:
            interpretations.append("Text overlay operation")
        if 'export' in cmd_lower:
            interpretations.append("Export operation")
        if 'organize' in cmd_lower or 'file' in cmd_lower:
            interpretations.append("File management operation")
        if 'screenshot' in cmd_lower:
            interpretations.append("Screenshot capture")
        if 'project' in cmd_lower:
            interpretations.append("Project creation")
        
        if interpretations:
            return "Detected: " + ", ".join(interpretations)
        else:
            return "General automation command - analyzing intent"
