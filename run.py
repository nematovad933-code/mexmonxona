import os
import sys
import time
import threading
import webbrowser
from app import app
from database import init_db
from seed_data import seed_initial_data

def open_browser():
    time.sleep(1.2)
    url = "http://localhost:5000"
    print(f"\n[+] Brauzer ochilmoqda: {url}")
    webbrowser.open(url)

if __name__ == '__main__':
    print("=" * 60)
    print("      MEHMONXONA BOSHQARUV VA RO'YXATGA OLISH TIZIMI")
    print("=" * 60)
    
    # 1. Bazani tekshirish va ishga tushirish
    init_db()
    seed_initial_data()
    
    # 2. Brauzerni avtomatik ochish oqimi
    threading.Thread(target=open_browser, daemon=True).start()
    
    # 3. Serverni ishga tushirish (Waitress orqali)
    port = 5000
    print(f"[*] Server manzili: http://localhost:{port}")
    print("[*] To'xtatish uchun terminalda Ctrl + C tugmalarini bosing.\n")
    
    try:
        from waitress import serve
        serve(app, host='127.0.0.1', port=port, threads=6)
    except ImportError:
        app.run(host='127.0.0.1', port=port, debug=False)

