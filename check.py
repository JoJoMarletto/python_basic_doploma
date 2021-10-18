from telebot.types import Message
from typing import List, Optional
import re

from users import User, users_dict
from loader import logger


@logger.catch
def check_user(message: Message) -> None:
    """Функция проверки наличия пользователя в списке, если нету - добавить в список"""
    logger.debug('Проверка пользователя по Id')
    if message.chat.id not in users_dict:
        users_dict[f'{message.chat.id}'] = User(chat_id=message.chat.id)
    cls_user: User = users_dict[f'{message.chat.id}']
    cls_user.city_name = cls_user.city_id = cls_user.call_method = cls_user.count_hotel = cls_user.locale = None
    cls_user.price_min = cls_user.price_max = cls_user.min_dist = cls_user.max_dist = cls_user.count_photo = None
    cls_user.photo = False


@logger.catch
def check_count_photo(message: Message) -> bool:
    """
    Функция для проверки ввода количества фотографий
    """
    logger.debug('Проверка ввода количества фотографий')
    if message.text.isdigit():
        if 0 < int(message.text) < 6:
            return True
        else:
            return False
    else:
        return False


@logger.catch
def check_hotel_count(message: Message) -> bool:
    """
    Функция для проверки ввода количества отелей
    """
    logger.debug('Проверка ввода количество отелей')
    if message.text.isdigit():
        if 0 < int(message.text) < 11:
            return True
        else:
            return False
    else:
        return False

@logger.catch
def check_min_max_price(message: Message) -> Optional[List]:
    """
    Функция для проверки ввода цены отеля
    """
    logger.debug('Проверка ввода максимальной и минимальной цены')
    result = re.findall(r'\d+', message.text)
    if len(result) == 2:
        return result
    else:
        return None


@logger.catch
def check_min_max_dist(message: Message) -> Optional[List]:
    """
    Функция для проверки диапазона растояния отеля
    """
    logger.debug('Проверка ввода максимальной и минимальной дистанции')
    result = re.findall(r'\d+', message.text)
    if len(result) == 2:
        return result
    else:
        return None


@logger.catch
def check_choice_city(message: Message) -> bool:
    """
    Функция для ввода названия города
    """
    logger.debug('Проверка ввода названия города')
    result = re.findall(r'[А-Яа-яЁё|A-Za-z]+', message.text)
    if 0 < len(result) < 4:
        return True
    else:
        return False


@logger.catch
def check_method_best_deal(message: Message, dist_hotel, hotel_cost):
    """
    Проверка цены для метода best_deal взависимости от языка.
    """
    logger.debug('Проверка цены и дистанции для метода best_deal')
    cls_user = users_dict[f'{message.chat.id}']
    if cls_user.locale == 'ru_RU':
        if (float(cls_user.min_dist) < float(dist_hotel) < float(cls_user.max_dist)) and (
             float(cls_user.price_min) / 1000 < float(hotel_cost) < float(cls_user.price_max)) / 1000:
            return True
        return False
    elif cls_user.locale == 'en_US':
        if (float(cls_user.min_dist) < float(dist_hotel) < float(cls_user.max_dist)) and (
             float(cls_user.price_min) < float(hotel_cost) < float(cls_user.price_max)):
            return True
        return False


@logger.catch
def check_hotel(hotel: dict) -> bool:
    """
    Проверка наличия нужных параметров
    """
    logger.debug('Производится проверка параметров отеля')
    name = 'name' in hotel
    address = 'streetAddress' in hotel['address']
    star_rating = 'starRating' in hotel
    current = 'current' in hotel['ratePlan']['price']
    dist_hotel = 'distance' in hotel['landmarks'][0]
    return all([name, address, star_rating, current, dist_hotel])
