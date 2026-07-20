#!/usr/bin/env python3
"""
FastAPI Quick Start Script
Run this to set up and start the Mareeswari AI FastAPI server
"""

import os
import sys
import subprocess
import shutil

def print_section(title):
    print("\n" + "="*50)
    print(f"  {title}")
    print("="*50 + "\n")

def check_python():
    """Check Python version"""
    print_section("🐍 Checking Python Installation")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    print(f"✓ Python {sys.version}")
    return True

def install_dependencies():
    """Install required packages"""
    print_section("📦 Installing Dependencies")
    
    try:
        print("Installing packages from requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def setup_env():
    """Setup environment file"""
    print_section("⚙️  Setting Up Environment")
    
    if os.path.exists(".env"):
        print("✓ .env file already exists")
    elif os.path.exists(".env.example"):
        print("Creating .env from template...")
        shutil.copy(".env.example", ".env")
        print("✓ .env created")
        print("⚠️  Remember to add your OPENAI_API_KEY to .env")
    else:
        print("⚠️  .env.example not found")
    
    return True

def start_server():
    """Start the FastAPI server"""
    print_section("🚀 Starting FastAPI Server")
    
    print("📖 API Documentation:")
    print("   - Interactive: http://localhost:8000/docs")
    print("   - Alternative: http://localhost:8000/redoc")
    print("\n🔗 API Base URL: http://localhost:8000")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        import uvicorn
        from app import app
        
        print("Starting server on http://0.0.0.0:8000...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except ImportError:
        print("❌ FastAPI not installed. Run pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def main():
    """Main setup and start function"""
    print("\n🎯 Mareeswari AI - FastAPI Setup & Start")
    
    # Run setup steps
    if not check_python():
        sys.exit(1)
    
    if not install_dependencies():
        sys.exit(1)
    
    if not setup_env():
        sys.exit(1)
    
    if not start_server():
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
        sys.exit(0)
