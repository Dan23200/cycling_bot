import sqlite3
from telebot import types
from utils import calculate_transmission
import telebot
# from database_bot import data
import sqlite3

bot = telebot.TeleBot("**********************************")

lists_with_buttons = ['Передача в дюймах 🚴', 'Отзыв о боте 🤖‍', 'Создатель бота🧑‍💻']


@bot.message_handler(commands=['start'])
def user_greeting(message):
    connect = sqlite3.connect('bot.db')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS reviews(
        users_id INTEGER
    )""")
    connect.commit()

    #Проверка на повторение ID
    people_id = message.chat.id
    cursor.execute(f"SELECT users_id FROM reviews WHERE users_id = {people_id}")
    data = cursor.fetchone()
    if data is None:
        user_id = [message.chat.id]
        cursor.execute("INSERT INTO reviews VALUES(?);", user_id)
        connect.commit()
    else:
        bot.send_message(message.chat.id, '{0.first_name}, рад тебя видеть вновь 😁'.format(message.from_user))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton(lists_with_buttons[0])
    item2 = types.KeyboardButton(lists_with_buttons[1])
    item3 = types.KeyboardButton(lists_with_buttons[2])

    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, 'Привет, {0.first_name}!'.format(message.from_user), reply_markup=markup)
    print('Кнопки работают')


@bot.message_handler(commands=['delete'])
def delete(message):
    connect = sqlite3.connect('bot.db')
    cursor = connect.cursor()
    people_id = message.chat.id
    cursor.execute(f"DELETE FROM reviews WHERE users_id = {people_id}")
    bot.send_message(message.chat.id, 'Вы успешно удалены из базы, возвращаетесь')


@bot.message_handler(content_types=['text'])
def front_chainring(message):
    if message.text == lists_with_buttons[0]:
        print('Расчёт передней шестерён')
        bot.send_message(message.chat.id, '{0.first_name}!, Скажи пожалуйста, сколько зубцов на передней шестерне? ⚙️'.format(message.from_user))
        bot.register_next_step_handler(message, bask_chainring)
    elif message.text == lists_with_buttons[2]:
        print('Создатель бота')
        bot.send_message(message.chat.id, 'Created by Danylo Kyrychenko 👨🏻')
    elif message.text == lists_with_buttons[1]:
        bot.send_message(message.chat.id, 'Напишите свой комментарий 🫣')
        bot.register_next_step_handler(message, feedback_register)


def feedback_register(message):
    connect = sqlite3.connect('bot.db')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS feed(
        users_feedback TEXT
    )""")
    connect.commit()

    cursor.execute(f"SELECT users_feedback FROM feed")
    answers = cursor.fetchone()
    if answers:
        feedback = message.text
        cursor.execute("INSERT INTO feed VALUES(?);", (feedback,))
        connect.commit()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        bot.send_message(message.chat.id, 'Спасибо большое! Комментарий успешно сохранён 👍\nЕсли вы хотите удалить свои данные из бота нажмите на /delete', reply_markup=markup)
        print('Сохранён')
    else:
        bot.send_message(message.chat.id, 'Tакой коментарий уже существует 👎')
    connect.commit()


def bask_chainring(message):
    global x
    x = message.text
    try:
        x = float(x)
    except ValueError:
        x = 0
    if x:
        bot.send_message(message.from_user.id, 'Скажи пожалуйста, количество зубцов на задней шестерне ⚙️')
        bot.register_next_step_handler(message, formula_solution)
    else:
        bot.send_message(message.from_user.id, 'Введи пожалуйста корректное значение - это должно быть целое число, не равное 0 😡')
        bot.register_next_step_handler(message, front_chainring)


def formula_solution(message):
    global y
    y = message.text
    result = calculate_transmission(front=float(x), back=float(y))
    try:
        y = float(y)
    except ValueError:
        y = 0
    if y:
        bot.send_message(message.from_user.id, "%.2f" % result)
    else:
        bot.send_message(message.from_user.id, 'Введите пожалуйста корректное значение – это должно быть целое число, не равна 0 😡')
        bot.register_next_step_handler(message, front_chainring)


bot.polling(none_stop=True)
