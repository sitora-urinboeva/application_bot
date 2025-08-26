import asyncio
from aiogram import Bot,Dispatcher, types
from aiogram.filters import Command
import psycopg2

TOKEN="8198606556:AAGyoNinc9uHefa-x1YRhL-PuFIrw_zhztI"
channel_username = " @forstudy_u"

bot=Bot(token=TOKEN)
dp = Dispatcher()

user_data ={}

conn= psycopg2.connect(host='localhost',dbname='postgres',user='postgres',password='postgre',port='5432')
cursor=conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS zayavka ( 
                id SERIAL PRIMARY KEY, 
                user_id VARCHAR,
                name VARCHAR,
                phone VARCHAR, 
                age VARCHAR)''')
conn.commit()

@dp.message()
async def process(message: types.Message):
    user_id = message.from_user.id
    if message.text == 'Zayavka qoldirish':
        await start(message)
    elif user_id not in user_data:
        await start(message)
    elif 'name' not in user_data[user_id]:
        await ask_phone(message)
    elif 'phone' not in user_data[user_id]:
        await ask_age(message)
    elif 'age' not in user_data[user_id]:
        await total_info(message)

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id=message.from_user.id
    user_data[user_id] = {}

    await message.answer(f"Assalomu alekum\nIltimos ismingizni kiriting:")

async def ask_phone(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]['name'] = message.text
    button = [
        [types.KeyboardButton(text="Raqamni yuborish", request_contact=True)]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True, one_time_keyboard=True)
    await message.answer(f"Iltimos telefon raqamingizni jo'nating +998...\nYoki 'Raqamni yuborish knopkasini bosing'",
                         reply_markup=keyboard)

async def ask_age (message: types.Message):
    user_id=message.from_user.id
    if message.contact:
        phone=message.contact.phone_number
    else:
        phone=message.text
    user_data[user_id]['phone']=phone
    await message.answer(f"Iltimos yoshingizni kiriting:")

async def total_info(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]['age'] = message.text
    total_text = (f"Ismingiz: {user_data[user_id]['name']}\n" 
                  f"Telefon raqamingiz: {user_data[user_id]['phone']}\n" 
                  f"Yoshingiz: {user_data[user_id]['age']}")

    cursor.execute("""INSERT INTO zayavka (user_id, name, phone, age) VALUES ( %s, %s, %s, %s) """,
        (str(user_id), user_data[user_id]['name'], user_data[user_id]['phone'], user_data[user_id]['age']))
    conn.commit()

    button = [
        [types.KeyboardButton(text="Zayavka qoldirish")]
        ]

    keyboard = types.ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True, one_time_keyboard=True)
    await message.answer(f"Zayavka qabul qilindi!\n"
                         f"{total_text}", reply_markup=keyboard)
    await bot.send_message(channel_username, total_text)
    del user_data[user_id]


async def main():
    await dp.start_polling(bot)

print('The bot is running...')
asyncio.run(main())

conn.close()
