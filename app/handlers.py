from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter, CommandObject
import random
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

last_used = {}

from app import keyboard as kb
from main import cursor, connection

from dotenv import load_dotenv
import os 

load_dotenv("ini.env")

router = Router()

# Состояния FSM
class GameState(StatesGroup):
    waiting_for_bullets = State()
    in_game = State()

class State_admin(StatesGroup):
    admin = State()

# Множители в зависимости от количества патронов
MULTIPLIERS = {
    1: 1.1,
    2: 1.3,
    3: 1.5,
    4: 1.7,
    5: 1.9,
    6: 2.5,
    7: 2.7,
    8: 2.8
}

# Хранение данных игры
user_games = {}

def new_face(id, username):
    username = username or "unknown"
    cursor.execute('SELECT 1 FROM UsersAndPointDatabese WHERE ID = ?', (id,))
    result = cursor.fetchone()
    if not result:
        cursor.execute('INSERT INTO UsersAndPointDatabese (id, username, point, level) VALUES (?, ?, ?, ?)', 
                      (id, username, 0, 0))
        connection.commit()
        
def update_point(new_point, id):
    cursor.execute('SELECT point FROM UsersAndPointDatabese WHERE id = ?', (id,))
    old_point = cursor.fetchone()
    if old_point and old_point[0] is not None:
        cursor.execute('UPDATE UsersAndPointDatabese SET point = ? WHERE id = ?', 
                      (new_point + old_point[0], id))
    else:
        cursor.execute('UPDATE UsersAndPointDatabese SET point = ? WHERE id = ?', 
                      (new_point, id))
    connection.commit()

def chek_admin_password(data, id):
    if data.get("admin") == os.getenv("ADMIN_PASSWORD"):
        cursor.execute('UPDATE UsersAndPointDatabese SET level = ? WHERE id = ?', (-1, id))
        connection.commit()
        return True
    return False

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет! 👋')
    id = message.from_user.id
    username = message.from_user.username
    new_face(id, username)
    await message.answer('Ты теперь зарегистрирован(а)! 😊 Если ты не нажимал эту команду раньше.')

@router.message(Command('info'))
async def info(message: Message):
    await message.answer('📝 Вот команды, которые ты можешь использовать:\n\n'
                         '/info - Список команд\n'
                         '/point - Посмотреть свои очки и уровень\n'
                         'p2p - Заработать очки 💎\n'
                         '/start - Зарегистрироваться\n'
                         '/rus_rou - Русская рулетка\n'
                         '/list (команда доступна только админам) - показывает список пользователей\n'
                         '/edit <айди пользователя> <новые очки> <новый уровень> - изменить показатели пользователя(доступна только админам)')

@router.message(Command('point'))
async def get_point(message: Message):
    user_id = message.from_user.id
    cursor.execute('SELECT point, level FROM UsersAndPointDatabese WHERE id = ?', (user_id,))
    my_point = cursor.fetchone()
    
    if my_point:
        await message.answer(f'💎 Ваши очки: {my_point[0]}\n🎯 Ваш уровень: {my_point[1]}')
    else:
        await message.answer('⚠️ Вы ещё не зарегистрированы!')

@router.message(F.text == 'p2p')
async def farm(message: Message):
    user_id = message.from_user.id
    now = datetime.now()

    if user_id in last_used and now - last_used[user_id] < timedelta(minutes=5):  # Кулдаун 5 минут
        await message.reply("⏳ Подождите 5 минут перед следующим использованием!")
        return

    last_used[user_id] = now
    new_point = random.randint(1, 20)
    update_point(new_point, user_id)
    await message.reply(f'🎉 Вы заработали {new_point} очков!')

@router.message(Command('admin'))
async def admin(message: Message, state: FSMContext):
    await state.set_state(State_admin.admin)
    await message.answer('🔒 Введите пароль админа')

@router.message(StateFilter(State_admin.admin))
async def admin_two(message: Message, state: FSMContext):
    await state.update_data(admin=message.text)
    data = await state.get_data()
    if not chek_admin_password(data, message.from_user.id):
        await message.answer("❌ Пароль неверный")
    else:
        await message.answer("✅ Пароль верный. Вы теперь админ 🎉")
    await state.clear()

@router.message(F.text == 'Даня лох')
async def farm(message: Message):
    try:
        await message.reply('😂 Да, да. Я полностью согласен!')
    except:
        await message.answer('😂 Да, да. Я полностью согласен!')

@router.message(Command('list'))
async def list(message: Message):
    cursor.execute('SELECT level FROM UsersAndPointDatabese WHERE id = ?', (message.from_user.id,))
    level_player = cursor.fetchone()
    if level_player and level_player[0] == -1:
        cursor.execute('SELECT * FROM UsersAndPointDatabese')
        rows = cursor.fetchall()

        if not rows:
            await message.answer("📊 База данных пуста.")
            return

        text = "📋 Список пользователей:\n\n"
        for row in rows:
            text += f"🆔 {row[0]}\n👤 Username: {row[1]}\n⭐ Очки: {row[2]}\n🎯 Уровень: {row[3]}\n\n"

        for part in [text[i:i+4000] for i in range(0, len(text), 4000)]:
            await message.answer(part)
    else:
        await message.answer("❌ Вы не админ ❌")

@router.message(Command('rus_rou'))
async def russian_rulet(message: Message, command: Command, state: FSMContext):
    play_id = message.from_user.id
    cursor.execute('SELECT point FROM UsersAndPointDatabese WHERE id = ?', (play_id,))
    point_data = cursor.fetchone()
    point = point_data[0] if point_data else 0
    
    if not command.args:
        await message.answer("❌ Укажите ставку после /rus_rou! Пример: /rus_rou 100")
        return
        
    try:
        bet = int(command.args)
        if bet <= 0 or bet > point:
            await message.answer(f"🔢 Ставка должна быть больше нуля и не больше вашего баланса ({point})! 🚫")
            return
        
        # Сохраняем ставку в состоянии
        await state.update_data(bet=bet)
        await message.answer(f"✅ Ставка принята: {bet} очков\nСколько патронов из 8 будет заряжено? (1-8)")
        await state.set_state(GameState.waiting_for_bullets)
        
    except ValueError:
        await message.answer("🤖 Ошибка! Это не похоже на число. Попробуйте ещё раз! ❌")

@router.message(GameState.waiting_for_bullets)
async def set_bullets(message: Message, state: FSMContext):
    try:
        bullets = int(message.text)
        if bullets < 1 or bullets > 8:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введите число от 1 до 8")
        return
    
    # Получаем ставку из состояния
    data = await state.get_data()
    bet = data.get('bet', 0)
    
    # Создаем игру
    chamber = [0] * 8
    bullet_positions = random.sample(range(8), bullets)
    for pos in bullet_positions:
        chamber[pos] = 1
    
    user_games[message.from_user.id] = {
        'chamber': chamber,
        'current_pos': 0,
        'bullets': bullets,
        'original_multiplier': MULTIPLIERS[bullets],
        'current_multiplier': MULTIPLIERS[bullets],
        'consecutive_shots': 0,
        'total_shots': 0,
        'game_over': False,
        'bet': bet
    }
    
    # Отправляем сообщение с клавиатурой
    await message.answer("Игра началась!", reply_markup=kb.get_game_keyboard())
    await state.set_state(GameState.in_game)

@router.callback_query(GameState.in_game, F.data == "shoot")
async def shoot(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    game = user_games.get(user_id)
    
    if not game or game['game_over']:
        await callback.answer("Игра уже завершена")
        return

    if game['consecutive_shots'] >= 3:
        await callback.answer("Нельзя стрелять более 3 раз подряд без прокрутки!")
        return

    if game['chamber'][game['current_pos']] == 1:
        # 💥 Игрок проиграл — минус ставка
        game['game_over'] = True
        update_point(-game['bet'], user_id)

        await callback.message.edit_text(
            f"💥 БАМ! Вы проиграли.\n"
            f"Множитель: {game['current_multiplier']:.2f}x\n"
            f"Ставка: {game['bet']} очков\n"
            f"Всего выстрелов: {game['total_shots'] + 1}",
            reply_markup=None
        )
        del user_games[user_id]
        await state.clear()
        return

    # Игрок выжил
    game['current_pos'] = (game['current_pos'] + 1) % 8
    game['consecutive_shots'] += 1
    game['total_shots'] += 1

    # Бонус за серию выстрелов
    if game['consecutive_shots'] >= 2:
        bonus = 0.5 * game['original_multiplier'] if game['consecutive_shots'] == 2 else 0.05 * game['original_multiplier']
        game['current_multiplier'] += bonus

    await update_game_message(callback.message, game)

@router.callback_query(GameState.in_game, F.data == "spin")
async def spin(callback: CallbackQuery):
    user_id = callback.from_user.id
    game = user_games.get(user_id)
    
    if not game or game['game_over']:
        await callback.answer("Игра уже завершена")
        return
    
    # Крутим барабан - выбираем случайную позицию
    game['current_pos'] = random.randint(0, 7)
    game['consecutive_shots'] = 0
    
    await update_game_message(callback.message, game)

@router.callback_query(GameState.in_game, F.data == "stop")
async def stop_game(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    game = user_games.get(user_id)

    if not game or game['game_over']:
        await callback.answer("Игра уже завершена")
        return

    # 💰 Вычисляем и начисляем выигрыш
    win_amount = int(game['bet'] * game['current_multiplier'])
    update_point(win_amount, user_id)

    game['game_over'] = True

    await callback.message.edit_text(
        f"🏁 Игра окончена по вашему желанию.\n"
        f"💰 Вы выиграли: {win_amount} очков!\n"
        f"Множитель: {game['current_multiplier']:.2f}x\n"
        f"Ставка: {game['bet']} очков\n"
        f"Всего выстрелов: {game['total_shots']}",
        reply_markup=None
    )

    del user_games[user_id]
    await state.clear()

async def update_game_message(message: Message, game):
    bullets_left = sum(game['chamber'])
    text = (
        f"🔫 Русская рулетка\n"
        f"Патронов в барабане: {bullets_left}/8\n"
        f"Текущий множитель: {game['current_multiplier']:.2f}x\n"
        f"Ставка: {game['bet']} очков\n"
        f"Выстрелов подряд: {game['consecutive_shots']}/3\n"
        f"Всего выстрелов: {game['total_shots']}"
    )
    
    await message.edit_text(text, reply_markup=kb.get_game_keyboard())
    
@router.message(Command("edit"))
async def handle_edit_command(message: Message, command: CommandObject):
    # Проверка прав администратора (уровень -1)
    try:
        cursor.execute('SELECT level FROM UsersAndPointDatabese WHERE id = ?', (message.from_user.id,))
        user_level = cursor.fetchone()
        if not user_level or user_level[0] != -1:
            await message.answer("🚫 Ошибка: Недостаточно прав! Только админы (level=-1) могут редактировать.")
            return
    except Exception as e:
        await message.answer(f"❌ Ошибка проверки прав: {e}")
        return

    # Проверка аргументов команды
    if not command.args:
        await message.answer("❌ Укажите аргументы: /edit <ID> <новый point> <новый level>")
        return

    args = command.args.split()
    if len(args) != 3:
        await message.answer("❌ Нужно 3 аргумента: /edit <ID> <point> <level>")
        return

    # Проверка, что аргументы - числа
    try:
        user_id = int(args[0])
        new_point = int(args[1])
        new_level = int(args[2])
    except ValueError:
        await message.answer("❌ Все аргументы должны быть числами!")
        return

    # Обновление данных
    try:
        cursor.execute(
            'UPDATE UsersAndPointDatabese SET point = ?, level = ? WHERE id = ?',
            (new_point, new_level, user_id)
        )
        connection.commit()
        await message.answer(f"✅ Данные пользователя {user_id} обновлены!")
    except Exception as e:
        await message.answer(f"❌ Ошибка при обновлении: {e}")