"""
Script để chạy SuiGuard Demo
Tự động start backend server và mở frontend
"""

import subprocess
import webbrowser
import time
import os
import sys
from pathlib import Path

def check_dependencies():
    """Kiểm tra xem đã cài đặt dependencies chưa"""
    try:
        import fastapi
        import uvicorn
        print("✅ Dependencies đã được cài đặt")
        return True
    except ImportError:
        print("❌ Chưa cài đặt dependencies")
        print("Đang cài đặt...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True

def start_backend():
    """Khởi động backend server"""
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    print("🚀 Đang khởi động backend server...")
    print("📍 Backend sẽ chạy tại: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("\n" + "="*50)
    
    # Chạy uvicorn
    subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])

def main():
    """Hàm main"""
    print("="*50)
    print("🛡️  SuiGuard Demo - AI Security Assistant")
    print("="*50)
    print()
    
    # Kiểm tra dependencies
    if not check_dependencies():
        return
    
    # Đợi một chút để backend khởi động
    time.sleep(2)
    
    # Mở frontend trong browser
    frontend_path = Path(__file__).parent / "frontend" / "index.html"
    frontend_url = f"file://{frontend_path.absolute()}"
    
    print(f"🌐 Đang mở frontend: {frontend_url}")
    webbrowser.open(frontend_url)
    
    # Start backend
    start_backend()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Đã dừng server. Tạm biệt!")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")

