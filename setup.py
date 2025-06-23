#!/usr/bin/env python3
"""
Quick Setup Script for Digital Bulletin Board
This script helps you get your application up and running quickly.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3.8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def check_directories():
    """Check and create necessary directories"""
    print("\n📁 Checking directories...")
    
    directories = [
        "encrypted_data",
        "super_secret_stuff",
        "static/data",
        "static/images",
        "templates"
    ]
    
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"✅ {directory} exists")
        else:
            path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created {directory}")

def check_files():
    """Check if essential files exist"""
    print("\n📄 Checking essential files...")
    
    essential_files = [
        "main.py",
        "encrypted_db.py",
        "requirements.txt",
        "super_secret_stuff/supersecret.json"
    ]
    
    missing_files = []
    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def test_database():
    """Test the encrypted database system"""
    print("\n🔐 Testing encrypted database...")
    try:
        from encrypted_db import EncryptedDatabase
        db = EncryptedDatabase()
        stats = db.get_database_stats()
        print("✅ Encrypted database initialized successfully")
        print(f"📊 Database tables: {list(stats.keys())}")
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    print("=== Digital Bulletin Board Setup ===")
    print("🚀 Setting up your encrypted bulletin board application...\n")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check essential files
    if not check_files():
        print("\n❌ Setup cannot continue due to missing files")
        sys.exit(1)
    
    # Create directories
    check_directories()
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Test database
    if not test_database():
        sys.exit(1)
    
    print("\n" + "="*50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run the application: python main.py")
    print("2. Open your browser: http://localhost:8000")
    print("3. Manage database: python db_manager.py")
    print("\n📚 Documentation:")
    print("- Read DATABASE_MIGRATION_README.md for detailed information")
    print("- Check the .gitignore file to understand what files are protected")
    print("\n🔒 Security reminders:")
    print("- Keep your super_secret_stuff/ directory secure")
    print("- Backup your encryption keys regularly")
    print("- Never commit sensitive files to version control")
    print("="*50)

if __name__ == "__main__":
    main()
