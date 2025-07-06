import logging
import openai
import os
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = os.getenv("API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
openai.api_key = OPENAI_API_KEY

user_sessions = {}
FREE_LIMIT = 3

menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(KeyboardButton("📄 Написати реферат"), KeyboardButton("🌐 Перекласти"))
menu.add(KeyboardButton("🧪 Відповісти на тест"))

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = 0
    await message.reply("Привіт! Я StudentAI. Обери дію нижче:", reply_markup=menu)

@dp.message_handler(lambda message: message.text in ["📄 Написати реферат", "🌐 Перекласти", "🧪 Відповісти на тест"])
async def handle_menu(message: types.Message):
    user_id = message.from_user.id
    if user_sessions[user_id] >= FREE_LIMIT:
        await message.reply("❌ Вичерпано ліміт безкоштовних запитів. Оформіть підписку для продовження.")
        return

    if message.text == "📄 Написати реферат":
        await message.reply("Введіть тему реферату:")
        dp.register_message_handler(handle_essay, state=None)
    elif message.text == "🌐 Перекласти":
        await message.reply("Введіть текст для перекладу:")
        dp.register_message_handler(handle_translate, state=None)
    elif message.text == "🧪 Відповісти на тест":
        await message.reply("Введіть тестове запитання:")
        dp.register_message_handler(handle_test_answer, state=None)

async def handle_essay(message: types.Message):
    user_id = message.from_user.id
    topic = message.text
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Напиши короткий реферат на тему: {topic}"}]
    )
    user_sessions[user_id] += 1
    await message.reply(response.choices[0].message['content'])

async def handle_translate(message: types.Message):
    user_id = message.from_user.id
    text = message.text
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Переклади український текст англійською: {text}"}]
    )
    user_sessions[user_id] += 1
    await message.reply(response.choices[0].message['content'])

async def handle_test_answer(message: types.Message):
    user_id = message.from_user.id
    question = message.text
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Дай правильну відповідь на тестове питання: {question}"}]
    )
    user_sessions[user_id] += 1
    await message.reply(response.choices[0].message['content'])

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)