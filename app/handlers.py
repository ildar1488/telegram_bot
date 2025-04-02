from aiogram import F, Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command, StateFilter
import random
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app import keyboard as kb
from main import cursor 
from main import connection

from dotenv import load_dotenv
import os 

load_dotenv("ini.env")


router = Router()

class State_admin(StatesGroup):
    admin = State()

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

def chek_admin_password(data, id):
    if data.get("admin") == os.getenv("ADMIN_PASSWORD"):
        cursor.execute('UPDATE UsersAndPointDatabese SET level = ? WHERE id = ?', (-1, id))
        connection.commit()
    else:
        return False
        

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет!')
    id = message.from_user.id
    username = message.from_user.username
    new_face(id, username)
    await message.answer('Ты теперь зарегестрирован(ну если ты не нажимал эту команду раньше(:)')

@router.message(Command('info'))
async def get_point(message: Message):
    await message.answer('/info-команды,\n/point-свои очки и уровень, \np2p(словом)-заработать очки    ,\n/start-зарегистрироваться')

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
    
@router.message(Command('admin'))
async def admin(message: Message, state: FSMContext):
    await state.set_state(State_admin.admin)
    await message.answer('Введите пароль админа')

@router.message(StateFilter(State_admin.admin))
async def admin_two(message: Message, state: FSMContext):
    await state.update_data(admin = message.text)
    data = await state.get_data()
    if chek_admin_password(data, message.from_user.id) == False:
        await message.answer("Пароль неверный")
    else:
        await message.answer("Пароль верный. Вы теперь админ")
    await state.clear()
    
@router.message(F.text == 'Даня лох')
async def farm(message: Message):
    await message.reply('Да, да. Я полностью согласен!')

