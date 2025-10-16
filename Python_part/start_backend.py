#!/usr/bin/env python3
"""
Startup script for the unified backend
Run this to start all services in one place
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    return True

def start_backend():
    """Start the unified backend"""
    print("🚀 Starting unified backend...")
    try:
        # Change to the Python part directory (with space)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        python_part_dir = os.path.join(parent_dir, "Python part")
        
        if os.path.exists(python_part_dir):
            os.chdir(python_part_dir)
            print(f"📁 Changed to directory: {python_part_dir}")
        else:
            print(f"❌ Directory not found: {python_part_dir}")
            return
        
        # Start the unified backend
        subprocess.run([sys.executable, "unified_backend.py"])
    except KeyboardInterrupt:
        print("\n👋 Backend stopped by user")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🌐 UNIFIED WEATHER SERVICES BACKEND")
    print("=" * 60)
    print("📱 Available Services:")
    print("   • Weather Blog Generator")
    print("   • Tsunami Detection")
    print("   • Climate Podcast")
    print("   • Weather Data")
    print("   • Twitter Weather Posts")
    print("=" * 60)
    
    # Install requirements first
    if install_requirements():
        print("\n" + "=" * 60)
        start_backend()
    else:
        print("❌ Cannot start backend due to installation errors")
        sys.exit(1)