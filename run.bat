@echo off
chcp 65001 >nul
cd %CD%
set BOT_TOKEN=Bot(os.getenv("Token"))

echo ✅ Запуск Telegram-бота...
python main.py

if %errorlevel% equ 0 (
    echo 🟢 Бот вышел в онлайн.
) else (
    echo ❌ Произошла ошибка при запуске бота.
)

pause
