import json
import time
import requests
from telebot.types import InputMediaPhoto, Message
from decouple import config
from typing import List

from requests.exceptions import ReadTimeout, ConnectTimeout
from loader import logger, get_headers, bot
from users import User, users_dict


@logger.catch
def get_photo(message: Message, hotel_id: str) -> List:
    """
    Функция запроса к API для поиска фотографий отелей
    """
    cls_user: User = users_dict[f'{message.chat.id}']

    headers = get_headers()
    url = config("URL_GET_PHOTOS")
    querystring = {"id": hotel_id}

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=15)
        logger.debug(f'Сделали запрос на получение фото, овтет, статус ответа: {response.status_code}')

        if response.status_code == 200:
            data = json.loads(response.text)
            photo_list = list()
            for image in range(cls_user.count_photo):
                url = data['hotelImages'][image]['baseUrl'].format(size='y')
                photo_list.append(InputMediaPhoto(url))
            else:
                return photo_list
        else:
            raise ConnectTimeout
    except (ReadTimeout, ConnectTimeout) as e:
        bot.send_message(message.chat.id, 'Превышено время ответа сервера. Повторяю попытку через 3 секунды.')
        time.sleep(2)
        get_photo(message, hotel_id)
        logger.exception(f'Ошибка {e}')
