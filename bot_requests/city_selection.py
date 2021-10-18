from telebot.types import Message
from decouple import config
from telebot import types
import requests
import json
import time
import re

from requests.exceptions import ReadTimeout, ConnectTimeout, ConnectionError
from loader import logger, get_headers, bot
from check import check_choice_city
from users import User, users_dict


@logger.catch
def choice_city(message: Message) -> None:
    """
    Функция запроса к API для поиска названия города
    """
    cls_user: User = users_dict[f'{message.chat.id}']
    cls_user.city_name = message.text
    logger.debug('Записали название города от пользователя')
    if check_choice_city(message):
        cls_user.locale = 'ru_RU' if re.match(r'[А-Яа-яЁё]+', cls_user.city_name) else 'en_US'
        query = {"query": cls_user.city_name, "locale": cls_user.locale}
        headers = get_headers()
        try:
            response = requests.request("GET", url=config('URL_SEARCH'), headers=headers, params=query, timeout=15)
            logger.debug(f'Сделали запрос на получение списка названий городов, статус ответа:{response.status_code}')
            if response.status_code == 200:
                bot.send_message(message.chat.id, 'Ищу варианты названия города')
                list_cities(message, response)
            else:
                logger.debug('Проблема запроса на получение списка названий городов')
                raise ConnectionError
        except (ReadTimeout, ConnectTimeout, ConnectionError) as e:
            bot.send_message(message.chat.id, 'Превышено время ответа сервера. Повторяю попытку через 3 секунды.')
            time.sleep(3)
            choice_city(message)
            logger.exception(f'Ошибка {e}')
    else:
        bot.send_message(message.chat.id, 'Название города должно состоять только из букв, повтороите пожалуйста.')
        bot.register_next_step_handler(message, choice_city)


@logger.catch
def list_cities(message: Message, response: json) -> None:
    """
    Функция для создания списка названий возможных городов и
    вызова функции create_keyboard для созддания списка кнопок с названиями и ID городов
    """
    cls_user: User = users_dict[f'{message.chat.id}']
    data = json.loads(response.text)
    logger.debug('Создаем список городов')
    list_city = [(city['destinationId'], re.sub(r'<.*>', message.text.capitalize(),
                 city['caption']), cls_user.call_method)
                 for city in data['suggestions'][0]['entities'] if city['type'] == 'CITY']
    if len(list_city) > 0:
        create_keyboard(message, list_city)
    else:
        logger.debug('Город не найден')
        bot.send_message(cls_user.chat_id, 'Такой город не найден, попробуйте ввести другой вариант.')
        bot.register_next_step_handler(message, choice_city)


@logger.catch
def create_keyboard(message: Message, city_list: list) -> None:
    """
    Создание клавиатуры ввиде списка названия городов и передачи ID выбранного города через callback
    """
    cities_markup = types.InlineKeyboardMarkup(row_width=1)
    logger.debug('Создание клавиатуры с выбором города')
    for city in city_list:
        cities_markup.add(types.InlineKeyboardButton(
            text=f'{city[1]}',
            callback_data=f'id_city:{city[0]}')
        )
    bot.send_message(message.chat.id, 'Выберите город:', reply_markup=cities_markup)
