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
conn.commit()

# Словарь для хранения состояния пользователя
user_states = {}


@bot.message_handler(commands=['start'])
def start(message):
    show_main_menu(message)


def show_main_menu(message):
    # Приветственное сообщение
    welcome_message = "Добро пожаловать в футбольное сообщество MatchMaker!\n"
    welcome_message += "Используйте кнопки ниже для выбора функций."

    # Создание кнопок
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_button = types.KeyboardButton("Добавить данные")
    update_button = types.KeyboardButton("Изменить данные")
    view_button = types.KeyboardButton("Мои данные")
    markup.add(add_button, update_button, view_button)

    bot.send_message(message.chat.id, welcome_message, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Добавить данные")
def initiate_add(message):
    user_states[message.from_user.id] = {}
    bot.reply_to(message, "Введите ваше имя:")


@bot.message_handler(func=lambda message: message.text == "Изменить данные")
def initiate_update(message):
    user_states[message.from_user.id] = {'update': True}
    view(message)  # показываем данные для изменения


@bot.message_handler(func=lambda message: message.text == "Мои данные")
def view(message):
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (message.from_user.id,))
    user_info = cursor.fetchone()

    if user_info:
        response = "Ваши данные:\n"
        response += f"Имя: {user_info[1]}\n"
        response += f"Фамилия: {user_info[2]}\n"
        response += f"Год рождения: {user_info[3]}\n"
        response += f"Город: {user_info[4]}\n"
        response += f"Номер телефона: {user_info[5]}\n"
        response += f"Уровень игры: {user_info[6]}\n"
        response += f"Ведущая нога: {user_info[7]}\n"
        response += f"Позиция: {user_info[8]}\n"
        response += f"Основной скилл: {user_info[9]}\n"
        bot.reply_to(message, response)

        if 'update' in user_states[message.from_user.id]:
            bot.reply_to(message, "Введите имя, которое хотите изменить:")
    else:
        bot.reply_to(message, "Вы еще не добавили свои данные. Используйте /add для этого.")


@bot.message_handler(func=lambda message: message.from_user.id in user_states)
def collect_data(message):
    user_id = message.from_user.id
    state = user_states[user_id]

    if 'update' in state:  # Логика для изменения данных
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


if __name__ == '__main__':
    bot.polling(none_stop=True)