from telebot.types import Message, CallbackQuery
from telebot import types
import telebot.types
from flask import Flask, request
from decouple import config
import os

from bot_requests.city_selection import choice_city
from handlers import count_photo, hotel_count, menu
from users import User, users_dict
from loader import logger, bot
from check import check_user


server = Flask(__name__)


@bot.message_handler(commands=['start'])
@logger.catch
def start(message: Message) -> None:
    """
    Функция обработки команды 'старт', вызывающая функцию 'меню'
    """
    menu(message)


@bot.message_handler(content_types=["text"])
@logger.catch
def get_text(message: Message) -> None:
    """
    Функция отлавливания метода сортировки и запрос для ввода названия города,
    а так же вызывает функцию (choice_city) по поиску названия и ID города
    """
    check_user(message)
    cls_user: User = users_dict[f'{message.chat.id}']
    if message.text in ['/lowprice', '/highprice', '/bestdeal']:
        logger.debug(f'Записали метод сортировки: {message.text}')
        cls_user = users_dict[f'{message.chat.id}']
        cls_user.call_method = message.text
        bot.send_message(message.chat.id, 'Напишите название города')
        bot.register_next_step_handler(message, choice_city)
    elif message.text == '/history':
        logger.debug('Пользователь запросил историю поиска')
        for info in cls_user.history_list:
            bot.send_message(message.chat.id, info)
        menu(message)
    elif message.text == '/help':
        logger.debug('Пользователь выбрал команду help')
        bot.send_message(message.chat.id,
                         'Я бот для поиска отелей!\n'
                         'Я ищу самые дешевые и дорогие отели, а так же '
                         'отпимальные варианты по цене и расположению.\n'
                         'Для начала работы выберите команду:\n'
                         '/lowprice - поиск самых дешевых отелей.\n'
                         '/highprice - поиск самых дорогих отелей.\n'
                         '/bestdeal - поиск оптимального отеля по цене и расоложению.\n'
                         '/history - вывод вашей истории поиска.')


@bot.callback_query_handler(func=lambda call: True)
@logger.catch
def get_menu_button(call: CallbackQuery) -> None:
    """
    Функция отлавливания ID города, выбранного через нажатие кнопки
    """
    cls_user: User = users_dict[f'{call.message.chat.id}']
    if call.data.startswith('id_city'):
        cls_user.city_id = call.data[8:]
        markup = types.InlineKeyboardMarkup(row_width=2)
        button_yes = types.InlineKeyboardButton(text='Да', callback_data='Yes')
        button_no = types.InlineKeyboardButton(text='Нет', callback_data='No')
        markup.add(button_yes, button_no)
        bot.send_message(call.message.chat.id, 'Загружать фотографии?', reply_markup=markup)
    elif call.message.text == 'Загружать фотографии?':
        if call.data == 'Yes':
            cls_user.photo = True
            bot.send_message(call.message.chat.id, 'Введите количество фотографий (Не более 5)')
            bot.register_next_step_handler(call.message, count_photo)
        else:
            cls_user.photo = False
            bot.send_message(call.message.chat.id, 'Введите количество отелей (Не более 10)')
            bot.register_next_step_handler(call.message, hotel_count)


@server.route('/' + config("TOKEN"), methods=['PORT'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '!', 200


@server.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f'{config("APP_URL")}{config("TOKEN")}')
    return '!', 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
