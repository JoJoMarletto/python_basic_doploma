import telebot
from telebot.types import Message
from decouple import config
from loguru import logger

from users import User, users_dict


bot = telebot.TeleBot(token=config('TOKEN'))

logger.add('debug.log', format='{time} | {level} | {file} | {function} | {message} | {line}',
           level='DEBUG', encoding='UTF-8')



@logger.catch
def get_querystring(message: Message) -> dict:
    cls_user: User = users_dict[f'{message.chat.id}']
    sort_order = {'/lowprice': 'PRICE', '/highprice': 'PRICE_HIGHEST_FIRST', '/bestdeal': 'DISTANCE_FROM_LANDMARK'}
    querystring = {
        "destinationId": cls_user.city_id,
        "pageNumber": "1",
        "pageSize": "25",
        "checkIn": cls_user.check_in,
        "checkOut": cls_user.check_out,
        "adults1": "1",
        "priceMin": cls_user.price_min,
        "priceMax": cls_user.price_max,
        "sortOrder": sort_order[cls_user.call_method],
        "locale": cls_user.locale,
        "currency": f'{"RUB" if cls_user.locale == "ru_RU" else "USD"}'
    }
    return querystring


@logger.catch
def get_headers() -> dict:
    headers = {
        'x-rapidapi-host': config("HOTEL_API_HOST"),
        'x-rapidapi-key': config("HOTEL_API_KEY")
    }
    return headers
