import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ChatAction, ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import httpx


import os
from dotenv import load_dotenv, find_dotenv
# Загрузка переменных окружения из .env файла
load_dotenv(find_dotenv())

# Перемещаем все переменные окружения в глобальную область видимости
bot = Bot(os.getenv("Token"))
api_key = (os.getenv("API_KEY"))

# Создание диспетчера
dp = Dispatcher()


# Определяем состояния для поиска синонимов
class SynonymStates(StatesGroup):
    waiting_for_english_word = State()
    waiting_for_german_word = State()


# Главная клавиатура
main_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="ℹ️ Информация", callback_data="info"),
     InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
    [InlineKeyboardButton(text="🇬🇧 Английские синонимы", callback_data="english_synonyms"),
     InlineKeyboardButton(text="🇩🇪 Немецкие синонимы", callback_data="german_synonyms")],
    [InlineKeyboardButton(text="💬 Техподдержка", callback_data="support")]
])

async def start_command(message: types.Message):
    text = ("<b>Привет! 👋</b>\n\n"
            "Добро пожаловать в <i>бот для поиска синонимов</i> для английских и немецких слов. 🎉✨\n\n"
            "Выбирайте нужный режим и наслаждайтесь удобным поиском синонимов! 🚀")
    await message.reply(text, reply_markup=main_keyboard, parse_mode="HTML")
    await message.answer_sticker('CAACAgIAAxkBAAENiMRn1_yQnMnMiYP2VIEziJX1O95dpQAC-RYAArtSuUmHd6j9C5buuDYE')

@dp.message(Command("start"))
async def handle_start(message: Message):
    await start_command(message)


# Функция, отвечающая за отправку сообщения
async def send_info(target):
    await target.answer(
        "💡 Это разработка студентов ИМОИиФ курса «Цифровой переводчик».\n\n"
        "🎯 Цель проекта: оптимизировать поиск синонимов английских и немецких терминов и ускорить работу переводчиков, студентов и преподавателей.\n\n"
        "🚀 Основные преимущества:\n"
        "1️⃣ Постоянная доступность ✅\n"
        "2️⃣ Легкость использования 💡\n"
        "3️⃣ Экономия времени ⏱️\n\n"
        "👨‍💻 Создатели приложения:\n"
        "• Сибиев А.Р., гр. 04.3-104\n"
        "• Косухина В.А., гр. 04.3-104\n"
        "• Татаринцева А.В., гр. 04.3-104\n"
        "• Горюнова Е.И., гр. 04.3-107\n"
        "• Ахметов А.А., гр. 04.3-106\n"
        "• Юсова Ю.М., гр. 04.3-410"
    )

# Обработчик нажатия на кнопку "Информация"
@dp.callback_query(F.data == "info")
async def info_callback(callback: CallbackQuery):
    await send_info(callback.message)
    await callback.answer()  # Закрываем уведомление о нажатии.

# Обработчик команды /info
@dp.message(Command("info"))
async def info_command(message: Message):
    await send_info(message)




# Функция для отправки сообщения с помощью /help или кнопки "Помощь"
async def send_help(target):
    await target.answer(
        "🤔 Как работает алгоритм?\n"
        "1️⃣ Вам нужно нажать на кнопку поиска, например, английских синонимов;\n"
        "2️⃣ Далее вас перенесёт в режим ожидания слова, где вы вводите, например, слово 'money';\n"
        "3️⃣ Бот получает ваше слово и отправляет запрос в API;\n"
        "4️⃣ Затем полученный результат выводится в виде: *Сильные совпадения* и *Слабые совпадения*;\n"
        "5️⃣ После вывода бот будет ожидать следующего запроса или можно будет сменить язык поиска с помощью команды /back.\n\n"
        "📝 Распишем функции команд:\n"
        "• /info – выводит информационную справку о проекте: преимущества бота, его актуальность, цель создания и информацию о создателях с контактами.\n"
        "• /help – объясняет алгоритм работы (подсказка в виде примера) и показывает все команды.\n"
        "• /searcheng – переводит в режим поиска английских синонимов.\n"
        "• /searchdeutsch – переводит в режим поиска немецких синонимов.\n"
        "• /back – возвращает к основным командам (бот продолжает ожидание);\n"
        "• /support – связь с разработчиком. 🤖"
    )

# Обработчик нажатия на кнопку "Помощь"
@dp.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery):
    await send_help(callback.message)
    await callback.answer()  # Закрываем уведомление о нажатии

# Обработчик команды /help
@dp.message(Command("help"))
async def help_command(message: Message):
    await send_help(message)




# Обработчик команды /back – для выхода из режима ожидания слова и автоматического запуска /start
@dp.message(Command("back"))
async def back_command(message: Message, state: FSMContext):
    await state.clear()  # Очищаем состояние
    await message.answer("Вы вышли из режима поиска синонимов. Возвращаюсь в главное меню...")
    await start_command(message)  # Автоматически вызываем обработчик /start



# Общая функция для запроса ввода английского слова
async def request_english_word(target, state: FSMContext):
    await target.answer("Введите английское слово для поиска синонимов:")
    await state.set_state(SynonymStates.waiting_for_english_word)

# Обработчик команды /searcheng
@dp.message(Command("searcheng"))
async def searcheng_command(message: Message, state: FSMContext):
    await request_english_word(message, state)

# Обработчик кнопки "Синонимы" - английский
@dp.callback_query(F.data == "english_synonyms")
async def english_synonyms_callback(callback: CallbackQuery, state: FSMContext):
    await request_english_word(callback.message, state)
    await callback.answer()  # Закрываем уведомление о нажатии



# Общая функция для запроса ввода немецкого слова
async def request_german_word(target, state: FSMContext):
    await target.answer("Введите немецкое слово для поиска синонимов(с заглавной буквы):")
    await state.set_state(SynonymStates.waiting_for_german_word)

# Обработчик команды /searchdeutsch
@dp.message(Command("searchdeutsch"))
async def searchgerman_command(message: Message, state: FSMContext):
    await request_german_word(message, state)

# Обработчик кнопки "Синонимы" - немецкий
@dp.callback_query(F.data == "german_synonyms")
async def german_synonyms_callback(callback: CallbackQuery, state: FSMContext):
    await request_german_word(callback.message, state)
    await callback.answer()  # Закрываем уведомление о нажатии


# Обработчик ввода английского слова (c режимом ожидания следующего)
@dp.message(SynonymStates.waiting_for_english_word)
async def process_english_word(message: Message, state: FSMContext):
    word = message.text.strip().lower()  # Преобразуем слово к нижнему регистру
    # Если пользователь отправляет команду, то данный хэндлер её не обрабатывает
    if word.startswith("/"):
        return

     # Отправляем сообщение о начале поиска
    processing_message = await message.answer("Бот принял слово и начал поиск синонимов. Пожалуйста, подождите...")

    strong_synonyms, weak_synonyms = await get_english_synonyms(word)
    if not strong_synonyms and not weak_synonyms:
        response = f"Не найдено синонимов для слова: {word}"
    else:
        response = ""
        if strong_synonyms:
            response += f"Сильные совпадения: {', '.join(strong_synonyms)}\n\n"
        if weak_synonyms:
            response += f"Слабые совпадения: {', '.join(weak_synonyms)}"
    response += "\n\nВведите новое слово для поиска синонимов или введите /back для выхода."

    # Удаляет сообщение после ответа
    try:
        await processing_message.delete()
    except Exception:
        pass
# Отправляем результаты пользователю
    await message.answer(response)
    # Оставляем состояние для продолжения поиска


# Обработчик ввода немецкого слова (с режимом ожидания следующего)
@dp.message(SynonymStates.waiting_for_german_word)
async def process_german_word(message: Message, state: FSMContext):
    # Удаляем артикль, если слово начинается с него
    raw_text = message.text.strip().lower()
    tokens = raw_text.split()
    # Набор немецких определенных и неопределенных артиклей
    articles = {"der", "die", "das", "ein", "eine", "einen", "dem", "den"}
    if tokens and tokens[0] in articles:
        word = " ".join(tokens[1:]).strip()
    else:
        word = raw_text

    if not word or word.startswith("/"):
        return
# Отправляем сообщение о начале поиска
    processing_message = await message.answer("Бот принял слово и начал поиск синонимов. Пожалуйста, подождите...")

    strong_synonyms, weak_synonyms = await get_german_synonyms(word)
    if not strong_synonyms and not weak_synonyms:
        response = f"Не найдено синонимов для слова: {word}\n Попробуйте ввести слово с заглавной буквы или сущ. с артиклем"
    else:
        response = ""
        if strong_synonyms:
            response += f"Сильные совпадения: {', '.join(strong_synonyms)}\n\n"
        if weak_synonyms:
            response += f"Слабые совпадения: {', '.join(weak_synonyms)}"
    response += "\n\nВведите новое слово для поиска синонимов или введите /back для выхода."

    # Удаляет сообщение после ответа
    try:
        await processing_message.delete()
    except Exception:
        pass

    # Отправляем результаты пользователю
    await message.answer(response)
    # Оставляем состояние для продолжения поиска

# Функция для получения синонимов через Thesaurus API
async def get_english_synonyms(word: str):
    url = "https://api.apiverve.com/v1/thesaurus"
    headers = {"x-api-key": api_key}
    params = {"word": word}
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            response = await client.get(url, headers=headers, params=params)
            data = response.json()
            if data.get("status") == "ok":
                synonyms = data.get("data", {}).get("similarWords", [])
            else:
                synonyms = []
    except httpx.ConnectTimeout:
        synonyms = []
    half = len(synonyms) // 2
    if half == 0:
        return (synonyms, [])
    return (synonyms[:half], synonyms[half:])


# Функция для получения немецких синонимов через OpenThesaurus API
async def get_german_synonyms(word: str):
    url = f"https://www.openthesaurus.de/synonyme/search?q={word}&format=application/json"
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            response = await client.get(url)
            data = response.json()
            synonyms = []
            # OpenThesaurus возвращает наборы синонимов в ключе "synsets"
            for synset in data.get("synsets", []):
                # Можно попытаться разделить набор на сильные и слабые совпадения, например, по позиции
                terms = [term["term"] for term in synset.get("terms", [])]
                synonyms.extend(terms)
            # Удаляем дубликаты и само исходное слово (если оно присутствует)
            synonyms = list(set(synonyms))
            if word in synonyms:
                synonyms.remove(word)
    except httpx.ConnectTimeout:
        synonyms = []
    # Для симуляции разделения на сильные и слабые совпадения делим список пополам
    half = len(synonyms) // 2
    if half == 0:
        return (synonyms, [])
    return (synonyms[:half], synonyms[half:])


# Функция для отправки сообщения с помощью /support или кнопки "Тех. поддержка"
async def send_support(target):
    support_message = (
        "💬 Если вы хотите связаться с разработчиками или оставить отзыв о приложении, "
        "пишите в телеграм-аккаунт (id: @ayazsib) или отправьте письмо на почту 📧 sibievayaz6@gmail.com"
    )
    await target.answer(support_message)

# Обработчик команды /support
@dp.message(Command("support"))
async def support_command(message: Message):
    await send_support(message)

# Обработчик нажатия кнопки "Тех. поддержка"
@dp.callback_query(F.data == "support")
async def support_callback(callback: CallbackQuery):
    await send_support(callback.message)
    await callback.answer()  # Закрываем уведомление о нажатии

# Отслеживает любое фото
@dp.message(F.photo)
async def handle_photo(message: Message):
    await message.reply("Спасибо за фото! Но я пока не умею обрабатывать изображения. /start")


# Обработчик для всех остальных сообщений (если команда /start не введена)
@dp.message()
async def start(message: types.Message):
    await message.reply("Привет! Напиши команду /start")


# Функция для запуска бота
async def main():
    print("Бот запущен. Ожидание сообщений...") # Выводим сообщение в консоль
    await bot.delete_webhook(drop_pending_updates=True)  # Удаляем старые обновления
    await dp.start_polling(bot)  # Передаём `bot` при запуске поллинга

# Запуск
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"ERROR: {e}") # Выводим ошибку в консоль
