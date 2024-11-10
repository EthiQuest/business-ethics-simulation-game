#!/usr/bin/env python3
import subprocess
import sys
import os
import venv
from pathlib import Path

def main():
    """Set up development environment"""
    
    # Get root directory
    root_dir = Path(__file__).parent.parent
    venv_dir = root_dir / "venv"
    
    print("🚀 Setting up EthiQuest development environment...")
    
    # Create virtual environment
    print("\n📦 Creating virtual environment...")
    venv.create(venv_dir, with_pip=True)
    
    # Determine platform-specific activate script
    if sys.platform == "win32":
        activate_script = venv_dir / "Scripts" / "activate.bat"
        python_path = venv_dir / "Scripts" / "python.exe"
    else:
        activate_script = venv_dir / "bin" / "activate"
        python_path = venv_dir / "bin" / "python"

    # Upgrade pip
    print("\n🔄 Upgrading pip...")
    subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"])
    
    # Install dependencies
    print("\n📚 Installing dependencies...")
    subprocess.run([
        str(python_path),
        "-m",
        "pip",
        "install",
        "-r",
        str(root_dir / "requirements.txt")
    ])
    
    # Create .env file if it doesn't exist
    env_file = root_dir / ".env"
    if not env_file.exists():
        print("\n🔧 Creating .env file...")
        env_example = root_dir / ".env.example"
        if env_example.exists():
            env_example.rename(env_file)
        else:
            # Create basic .env file
            with open(env_file, "w") as f:
                f.write("""# Environment Configuration
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql+asyncpg://ethiquest:ethiquest@localhost:5432/ethiquest

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Service
AI_PROVIDER=anthropic
AI_API_KEY=your-api-key-here

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
""")
    
    print("\n✨ Development environment setup complete!")
    print("\nTo activate the virtual environment:")
    if sys.platform == "win32":
        print(f"    {activate_script}")
    else:
        print(f"    source {activate_script}")
    
    print("\nNext steps:")
    print("1. Edit .env with your configuration")
    print("2. Start the development server: uvicorn app.main:app --reload")
    print("3. Visit http://localhost:8000/docs for API documentation")

if __name__ == "__main__":
    main()