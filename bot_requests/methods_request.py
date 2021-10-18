import requests
import datetime
import json
import re
import time
from requests.exceptions import ReadTimeout, ConnectTimeout, ConnectionError
from decouple import config
from telebot.types import Message

from loader import logger, get_querystring, get_headers, bot
from check import check_method_best_deal, check_hotel
from bot_requests.get_hotel_photos import get_photo
from users import User, users_dict
import handlers


@logger.catch
def low_price(message: Message) -> None:
    """
    Запрос к API по методу сортировки low_price и вызова функции search_hotels
    для поиска отелей
    """
    querystring = get_querystring(message)
    headers = get_headers()
    bot.send_message(message.chat.id, 'Идёт поиск отелей...')

    try:
        response = requests.request("GET", url=config('URL'), headers=headers, params=querystring, timeout=15)
        logger.debug(f'Сдедали запрос на поиск отелей по сортировке low_price, статус ответа: {response.status_code}')
        if response.status_code == 200:
            search_hotels(message, response)
        else:
            raise ConnectionError
    except (ReadTimeout, ConnectTimeout, ConnectionError) as e:
        bot.send_message(message.chat.id, 'Превышено время ответа сервера. Повторяю попытку через 3 секунды.')
        time.sleep(3)
        low_price(message)
        logger.exception(f'Ошибка {e}')


@logger.catch
def high_price(message: Message) -> None:
    """
    Запрос к API по методу сортировки high_price и вызова функции search_hotels
    для поиска отелей
    """
    querystring = get_querystring(message)
    headers = get_headers()
    bot.send_message(message.chat.id, 'Идёт поиск отелей...')

    try:
        response = requests.request("GET", url=config('URL'), headers=headers, params=querystring, timeout=15)
        logger.debug(f'Сдедали запрос на поиск отелей по сортировке high_price, статус ответа: {response.status_code}')
        if response.status_code == 200:
            search_hotels(message, response)
        else:
            raise ConnectionError
    except (ReadTimeout, ConnectTimeout, ConnectionError) as e:
        bot.send_message(message.chat.id, 'Превышено время ответа сервера. Повторяю попытку через 3 секунды.')
        time.sleep(3)
        high_price(message)
        logger.exception(f'Ошибка {e}')


@logger.catch
def best_deal(message: Message) -> None:
    """
    Запрос к API по методу сортировки best_deal и вызова функции search_hotels
    для поиска отелей
    """
    querystring = get_querystring(message)
    headers = get_headers()
    bot.send_message(message.chat.id, 'Идёт поиск отелей...')

    try:
        response = requests.request("GET", url=config('URL'), headers=headers, params=querystring, timeout=15)
        logger.debug(f'Сдедали запрос на поиск отелей по сортировке best_deal, статус ответа: {response.status_code}')
        if response.status_code == 200:
            search_hotels(message, response)
        else:
            raise ConnectionError
    except (ReadTimeout, ConnectTimeout, ConnectionError) as e:
        bot.send_message(message.chat.id, 'Превышено время ответа сервера. Повторяю попытку через 3 секунды.')
        time.sleep(3)
        best_deal(message)
        logger.exception(f'Ошибка {e}')


@logger.catch
def search_hotels(message: Message, response: json) -> None:
    """
    Функция для поиска отелей по заданному пользователем методу,
    для проверки наличия параметров вызывается функция check_hotel
    """
    cls_user = users_dict[f'{message.chat.id}']
    count_hotel: int = cls_user.count_hotel
    data_hotels: dict = json.loads(response.text)
    hotels: dict = data_hotels['data']['body']['searchResults']['results']
    hotel_list = list()

    logger.debug('Производится поиск отелей')
    for i_hotel in hotels:
        if check_hotel(i_hotel):
            dist_hotel = ''.join(re.findall(r'\d+\S\d+', i_hotel['landmarks'][0]['distance'])).replace(',', '.')
            hotel_cost = ''.join(re.findall(r'\d+', i_hotel["ratePlan"]["price"]["current"])).replace(',', '.')
            address = i_hotel["address"]["streetAddress"]
            star_rating = i_hotel['starRating']
            hotel = {
                'hotel_id': i_hotel['id'],
                'Имя': i_hotel['name'],
                'Адрес': address,
                'Количество звёзд': star_rating,
                'До центра города': f'{dist_hotel} {"км" if cls_user.locale == "ru_RU" else "miles"}',
                'Стоимость': f'{hotel_cost} {"руб" if cls_user.locale == "ru_RU" else "$"}'
            }
            if cls_user.call_method == '/bestdeal':
                if check_method_best_deal(message, dist_hotel, hotel_cost):
                    hotel_list.append(hotel)
                else:
                    continue
            else:
                hotel_list.append(hotel)
            if count_hotel == len(hotel_list):
                hotel_withdrawal(message, hotel_list)
                break
    else:
        hotel_withdrawal(message, hotel_list)


@logger.catch
def hotel_withdrawal(message: Message, list_hotel: list) -> None:
    """
    Вывод найденых отелей, для поиска фотографий используется функция get_photo
    """
    try:
        logger.debug('Производится вывод найденых отелей пользователю')
        cls_user: User = users_dict[f'{message.chat.id}']
        cls_user.history_list.append(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")}\n'
                                     f'Команда поиска: {cls_user.call_method}\n'
                                     f'Найденные отели:')
        if list_hotel:
            for i, hotels in enumerate(list_hotel):
                hotel = f'{i+1}.\nИмя: {hotels["Имя"]}\n' \
                        f'Адрес: {hotels["Адрес"]}\n' \
                        f'Кол-во звёзд: {hotels["Количество звёзд"]}\n' \
                        f'До центра города: {hotels["До центра города"]}\n' \
                        f'Стоимость: {hotels["Стоимость"]}'
                cls_user.history_list.append(hotel)
                if cls_user.photo:
                    photo_list = get_photo(message, hotels['hotel_id'])
                    bot.send_media_group(message.chat.id, photo_list)
                bot.send_message(message.chat.id, hotel)
        else:
            cls_user.history_list.append('Отелей с такими параметрами не найдено.')
            bot.send_message(message.chat.id, 'Отелей с такими параметрами не найдено.')
        handlers.menu(message)
    except Exception as e:
        logger.exception(f'Ошибка: {e}')
