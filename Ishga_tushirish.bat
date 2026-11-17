@echo off
chcp 65001 > nul
title Mehmonxona Boshqaruv Tizimi
color 0B

echo ==============================================================
echo       MEHMONXONA MEHMONLARINI RO'YXATGA OLISH TIZIMI
echo ==============================================================
echo.
echo Dastur ishga tushirilmoqda, iltimos kuting...
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [XATOLIK] Python kompyuteringizda topilmadi!
    echo Iltimos, Python 3 ni o'rnating yoki PATH ga qo'shing.
    pause
    exit /b
)

python -m pip install -q -r requirements.txt

echo [OK] Tizim tayyor. Brauzer avtomatik ochiladi...
echo.
python run.py

pause

