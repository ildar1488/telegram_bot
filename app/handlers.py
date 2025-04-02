from aiogram import F, Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
import random

from app import keyboard as kb
from main import cursor 
from main import connection

router = Router()

def new_face(id, username):
    cursor.execute('SELECT 1 FROM UsersAndPointDatabese WHERE ID = ?', (id,))
    result = cursor.fetchone()
    connection.commit()
    if not result:
        cursor.execute('INSERT INTO UsersAndPointDatabese (id, username, point, level) VALUES (?, ?, ?, ?)', (id, username, 0, 0))
        connection.commit()
        
        
def update_point(new_point, id):
        cursor.execute('SELECT point FROM UsersAndPointDatabese WHERE id = ?', (id,))
        old_point = cursor.fetchone()
        connection.commit()
        cursor.execute('UPDATE UsersAndPointDatabese SET point = ? WHERE id = ?', (new_point + old_point[0], id))
        connection.commit()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет!')
    id = message.from_user.id
    username = message.from_user.username
    new_face(id, username)
    await message.answer('Ты теперь зарегестрирован(ну если ты не нажимал эту команду раньше(:)')

@router.message(Command('info'))
async def get_point(message: Message):
    await message.answer('/info-команды,\n/point-свои очки и уровень, \np2p(словом)-заработать очки,\n/start-зарегистрироваться')

@router.message(Command('point'))
async def get_point(message: Message):
    user_id = message.from_user.id
    cursor.execute('SELECT point, level FROM UsersAndPointDatabese WHERE id = ?', (user_id,))
    my_point = cursor.fetchone()
    
    if my_point:  # Проверяем, что запись найдена
        await message.answer(f'Ваши очки: {my_point[0]}. Ваш уровень: {my_point[1]}')
    else:
        await message.answer('Вы ещё не зарегистрированы!')
        

        
@router.message(F.text == 'p2p')
async def farm(message: Message):
    if not message.from_user:
        return
    new_point = random.randint(1,20)
    update_point(new_point, message.from_user.id)
    await message.reply(f'Вы заработали:{new_point}')
    
    

