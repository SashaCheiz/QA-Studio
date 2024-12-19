import telebot
import sqlite3
from telebot import types

# Инициализация бота
TOKEN = "7214008513:AAERsyJh26BMx7YGTVdvgBlrWSBO08npbqc"
bot = telebot.TeleBot(TOKEN)

# Подключаемся к базе данных SQLite (создается, если не существует)
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    surname TEXT,
    year_of_birth INTEGER,
    city TEXT,
    phone_number TEXT,
    level TEXT,
    leading_leg TEXT,
    position TEXT,
    skill TEXT
)
''')

# Создание таблицы для тренировок
cursor.execute('''
CREATE TABLE IF NOT EXISTS trainings (
    training_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT,
    price REAL,
    max_players INTEGER,
    participants TEXT
)
''')
conn.commit()

# Словарь для хранения состояния пользователя
user_states = {}

@bot.message_handler(commands=['start'])
def start(message):
    show_main_menu(message)

def show_main_menu(message):
    welcome_message = "Добро пожаловать в футбольное сообщество MatchMaker!\n"
    welcome_message += "Используйте кнопки ниже для выбора функций."

    # Создание кнопок
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_button = types.KeyboardButton("Добавить данные")
    update_button = types.KeyboardButton("Изменить данные")
    view_button = types.KeyboardButton("Мои данные")
    training_button = types.KeyboardButton("Создать тренировку")
    markup.add(add_button, update_button, view_button, training_button)

    bot.send_message(message.chat.id, welcome_message, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Создать тренировку")
def initiate_training(message):
    user_states[message.from_user.id] = {'stage': 'location'}
    bot.reply_to(message, "Введите локацию для тренировки:")

@bot.message_handler(func=lambda message: message.from_user.id in user_states)
def collect_data(message):
    user_id = message.from_user.id
    state = user_states[user_id]

    if 'stage' in state:  # Логика для создания тренировки
        if state['stage'] == 'location':
            state['location'] = message.text
            state['stage'] = 'price'
            bot.reply_to(message, "Введите цену за посещение тренировки:")
        elif state['stage'] == 'price':
            state['price'] = message.text
            state['stage'] = 'max_players'
            bot.reply_to(message, "Введите количество игроков:")
        elif state['stage'] == 'max_players':
            state['max_players'] = message.text
            state['stage'] = 'participants'
            state['participants'] = []  # Инициализация списка участников
            bot.reply_to(message, "Введите участников (через запятую):")
        elif state['stage'] == 'participants':
            state['participants'] = message.text.split(',')
            create_training(state)
            del user_states[user_id]  # Очистка состояния пользователя

    elif 'update' in state:  # Логика для изменения данных
        if 'name' in state:
            cursor.execute('UPDATE users SET surname = ? WHERE user_id = ?', (message.text, user_id))
            conn.commit()
            del state['surname']
            bot.reply_to(message, "Введите год рождения, который хотите изменить:")
        elif 'surname' not in state:
            state['surname'] = message.text
            bot.reply_to(message, "Введите год рождения:")
        elif 'year_of_birth' not in state:
            cursor.execute('UPDATE users SET year_of_birth = ? WHERE user_id = ?', (message.text, user_id))
            conn.commit()
            del state['year_of_birth']
            bot.reply_to(message, "Введите новый город:")
        elif 'city' not in state:
            cursor.execute('UPDATE users SET city = ? WHERE user_id = ?', (message.text, user_id))
            conn.commit()
            del state['city']
            bot.reply_to(message, "Введите новый номер телефона:")
        elif 'phone_number' not in state:
            cursor.execute('UPDATE users SET phone_number = ? WHERE user_id = ?', (message.text, user_id))
            conn.commit()
            del state['phone_number']
            bot.reply_to(message, "Введите новый уровень игры:")
        elif 'level' not in state:
            cursor.execute('UPDATE users SET level = ? WHERE user_id = ?', (message.text, user_id))
            conn.commit()
            del state['level']
            bot.reply_to(message, "Введите новую ведущую ногу:")
        elif 'leading_leg' not in state:
            cursor.execute('UPDATE users SET leading_leg = ? WHERE user_id = ?', (message.text, user_id))
            conn.commit()
            del state['leading_leg']
            bot.reply_to(message, "Введите новую позицию на поле:")
        elif 'position' not in state:
            cursor.execute('UPDATE users SET position = ? WHERE user_id = ?', (message.text, user_id))
            conn.commit()
            del state['position']
            bot.reply_to(message, "Введите новый основной скилл:")
        elif 'skill' not in state:
            cursor.execute('UPDATE users SET skill = ? WHERE user_id = ?', (message.text, user_id))
            conn.commit()
            bot.reply_to(message, "Ваши данные успешно обновлены!")
            del user_states[user_id]
    else:  # Логика для добавления данных
        if 'name' not in state:
            state['name'] = message.text
            bot.reply_to(message, "Введите вашу фамилию:")
        elif 'surname' not in state:
            state['surname'] = message.text
            bot.reply_to(message, "Введите год рождения:")
        elif 'year_of_birth' not in state:
            state['year_of_birth'] = message.text
            bot.reply_to(message, "Введите город:")
        elif 'city' not in state:
            state['city'] = message.text
            bot.reply_to(message, "Введите номер телефона:")
        elif 'phone_number' not in state:
            state['phone_number'] = message.text
            bot.reply_to(message, "Введите уровень игры:")
        elif 'level' not in state:
            state['level'] = message.text
            bot.reply_to(message, "Введите ведущую ногу:")
        elif 'leading_leg' not in state:
            state['leading_leg'] = message.text
            bot.reply_to(message, "Введите позицию на поле:")
        elif 'position' not in state:
            state['position'] = message.text
            bot.reply_to(message, "Введите основной скилл:")
        elif 'skill' not in state:
            state['skill'] = message.text

            # Сохранение данных в базе данных
            cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, name, surname, year_of_birth, city, phone_number, level, leading_leg, position, skill)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (user_id, state['name'], state['surname'], state['year_of_birth'], state['city'],
                            state['phone_number'],
                            state['level'], state['leading_leg'], state['position'], state['skill']))

            conn.commit()
            bot.reply_to(message, "Ваши данные успешно добавлены!")

            # Очистка состояния пользователя
            del user_states[user_id]

def create_training(state):
    cursor.execute('''
    INSERT INTO trainings (location, price, max_players, participants)
    VALUES (?, ?, ?, ?)''',
    (state['location'], state['price'], state['max_players'], ', '.join(state['participants'])))
    conn.commit()
    bot.reply_to(bot.get_chat(state['user_id']), "Тренировка успешно создана!")

if __name__ == '__main__':
    bot.polling(none_stop=True)
