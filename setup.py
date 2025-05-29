import os
import sys
import subprocess
import secrets
from pathlib import Path

def create_virtual_env():
    """Create a virtual environment if it doesn't exist."""
    if not os.path.exists('venv'):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'])
        print("Virtual environment created successfully!")
    else:
        print("Virtual environment already exists.")

def install_requirements():
    """Install requirements from requirements.txt."""
    if os.name == 'nt':  # Windows
        pip_path = os.path.join('venv', 'Scripts', 'pip')
    else:  # Linux/Mac
        pip_path = os.path.join('venv', 'bin', 'pip')
    
    print("Installing requirements...")
    subprocess.run([pip_path, 'install', '-r', 'requirements.txt'])

def create_env_file():
    """Create .env file with default settings."""
    if not os.path.exists('.env'):
        print("Creating .env file...")
        env_content = f"""# Django Settings
DEBUG=True
SECRET_KEY={secrets.token_urlsafe(50)}
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DATABASE_URL=postgres://postgres:postgres@localhost:5432/inventory_db

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Timezone and Locale
TIME_ZONE=UTC
LANGUAGE_CODE=en-us

# Static and Media Files
STATIC_URL=/static/
MEDIA_URL=/media/

# Security Settings
CSRF_TRUSTED_ORIGINS=http://localhost:8000
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        print(".env file created successfully!")
    else:
        print(".env file already exists.")

def main():
    """Main setup function."""
    print("Starting setup process...")
    
    # Create virtual environment
    create_virtual_env()
    
    # Install requirements
    install_requirements()
    
    # Create .env file
    create_env_file()
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    if os.name == 'nt':  # Windows
        print("   .\\venv\\Scripts\\activate")
    else:  # Linux/Mac
        print("   source venv/bin/activate")
    print("2. Configure your database settings in .env")
    print("3. Run migrations: python manage.py migrate")
    print("4. Create a superuser: python manage.py createsuperuser")
    print("5. Start the development server: python manage.py runserver")

if __name__ == '__main__':
    main() 