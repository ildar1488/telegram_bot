import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
import sqlite3 as sq3
from dotenv import load_dotenv
import os 

from app import handlers
    
connection = sq3.connect('UsersAndPointDatabese.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS UsersAndPointDatabese (
id INTEGER PRIMARY KEY,
username TEXT NOT NULL,
point INTEGER,
level INTEGER
)
''')

load_dotenv()


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    dp.include_router(handlers.router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
       asyncio.run(main())
    except KeyboardInterrupt:
        print("bot off")
    