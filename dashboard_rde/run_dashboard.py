"""
Dashboard Runner Script
Installs required packages and starts the RSI, DMA & EMA Dashboard
"""

import subprocess
import sys
import os
from pathlib import Path

def install_packages():
    """Install required packages"""
    packages = ['flask', 'flask-cors', 'requests', 'numpy', 'tabulate']
    
    print("🔧 Installing required packages...")
    for package in packages:
        try:
            print(f"   Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package], 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
            print(f"   ✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"   ❌ Failed to install {package}")
            return False
    
    print("✅ All packages installed successfully!")
    return True

def start_dashboard():
    """Start the dashboard server"""
    current_dir = Path(__file__).parent
    app_file = current_dir / 'app.py'
    
    if not app_file.exists():
        print("❌ app.py not found!")
        return False
    
    print("\n🚀 Starting Dashboard Server...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("\n" + "="*60)
    
    try:
        # Change to the dashboard directory
        os.chdir(current_dir)
        
        # Start the Flask app
        subprocess.call([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting dashboard: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("📊 RSI, DMA & EMA Dashboard Setup")
    print("="*50)
    
    # Install packages
    if not install_packages():
        print("\n❌ Package installation failed. Please install manually:")
        print("   pip install flask flask-cors requests numpy tabulate")
        sys.exit(1)
    
    # Start dashboard
    if not start_dashboard():
        print("\n❌ Failed to start dashboard")
        sys.exit(1)

if __name__ == "__main__":
    main()