@echo off
chcp 65001 >nul
cd %CD%
set BOT_TOKEN=8175265574:AAGrmnUmCzBYdshTd44r99ShDzR5EzdBqOE

echo ✅ Запуск Telegram-бота...
python main.py

if %errorlevel% equ 0 (
    echo 🟢 Бот вышел в онлайн.
) else (
    echo ❌ Произошла ошибка при запуске бота.
)

pause
