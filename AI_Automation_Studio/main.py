#!/usr/bin/env python3
"""
AI Automation Studio - Main Entry Point
A powerful desktop GUI application for automation tasks.

Features:
- Mouse & Keyboard Automation with macro recording
- File Manager with batch operations
- CapCut Video Editor Automation
- AI-Powered Natural Language Commands

Run this file to start the application.
"""

import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import main

if __name__ == "__main__":
    print("=" * 60)
    print("⚡  AI AUTOMATION STUDIO v2.0")
    print("=" * 60)
    print("\nStarting application...")
    print("\nFeatures:")
    print("  🖥  Mouse & Keyboard Automation")
    print("  📁 File Manager with Batch Operations")
    print("  🎬 CapCut Video Editor Automation")
    print("  🤖 AI-Powered Natural Language Commands")
    print("\nNote: Move mouse to screen corner to emergency stop automation")
    print("=" * 60 + "\n")
    
    main()
