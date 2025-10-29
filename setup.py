#!/usr/bin/env python3
"""
Setup script for Fantasy Football Trade Analyzer
Validates environment and dependencies before starting the application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_node_version():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js version: {result.stdout.strip()}")
            return True
        else:
            print("❌ Error: Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Error: Node.js not installed")
        print("Please install Node.js from https://nodejs.org/")
        return False

def check_required_files():
    """Check if required model and data files exist"""
    required_files = [
        "models/fp_model_final.keras",
        "data/nfl_seasonal_preprocessed.csv"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_exist = False
    
    return all_exist

def setup_backend():
    """Set up the backend environment"""
    print("\n🔧 Setting up backend...")
    
    backend_dir = Path("backend")
    venv_dir = backend_dir / "venv"
    
    # Create virtual environment if it doesn't exist
    if not venv_dir.exists():
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)])
    
    # Determine the correct pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = venv_dir / "Scripts" / "pip"
    else:  # Unix-like (macOS, Linux)
        pip_path = venv_dir / "bin" / "pip"
    
    # Install requirements
    print("📥 Installing backend dependencies...")
    requirements_file = backend_dir / "requirements.txt"
    subprocess.run([str(pip_path), "install", "-r", str(requirements_file)])
    
    print("✅ Backend setup complete")

def setup_frontend():
    """Set up the frontend environment"""
    print("\n🔧 Setting up frontend...")
    
    frontend_dir = Path("fantasy-trade-app")
    
    # Install npm dependencies
    print("📥 Installing frontend dependencies...")
    subprocess.run(["npm", "install"], cwd=frontend_dir)
    
    print("✅ Frontend setup complete")

def main():
    """Main setup function"""
    print("🚀 Fantasy Football Trade Analyzer - Setup")
    print("=" * 50)
    
    # Check system requirements
    print("\n📋 Checking system requirements...")
    
    if not check_python_version():
        return False
    
    if not check_node_version():
        return False
    
    # Check required files
    print("\n📁 Checking required files...")
    if not check_required_files():
        print("\n❌ Setup failed: Missing required files")
        print("\nPlease ensure you have:")
        print("1. Your trained model: models/fp_model_final.keras")
        print("2. Your preprocessed data: data/nfl_seasonal_preprocessed.csv")
        return False
    
    # Set up environments
    try:
        setup_backend()
        setup_frontend()
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Setup failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False
    
    # Success message
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📖 Next steps:")
    print("1. Start the backend: ./start_backend.sh")
    print("2. Start the frontend: ./start_frontend.sh")
    print("3. Open http://localhost:3000 in your browser")
    print("\n💡 Tips:")
    print("- Get your ESPN cookies from Developer Tools")
    print("- API docs available at http://localhost:8000/docs")
    print("- Check logs if you encounter issues")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
