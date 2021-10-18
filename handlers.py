from telebot.types import Message
from telebot import types

from check import check_count_photo, check_hotel_count, check_min_max_price, check_min_max_dist
from bot_requests.methods_request import high_price, best_deal, low_price
from users import User, users_dict
from loader import logger, bot


@logger.catch
def count_photo(message: Message) -> None:
    """
    Функция для записывания количество фотографий и запроса у пользователя количества отелей
    """
    cls_user: User = users_dict[f'{message.chat.id}']
    if check_count_photo(message):
        cls_user.count_photo = int(message.text)
        logger.debug('Записали количество фотографий')
        bot.send_message(message.chat.id, 'Введите количество отелей (Не более 10)')
        bot.register_next_step_handler(message, hotel_count)
    else:
        bot.send_message(message.chat.id, 'Введите число от 1 до 5')
        bot.register_next_step_handler(message, count_photo)


@logger.catch
def hotel_count(message: Message) -> None:
    """
    Запись количества отелей и выбор функции по методу сортировки.
    Если выбран best_deal - запрашивается диапазон цен.
    """
    cls_user: User = users_dict[f'{message.chat.id}']
    if check_hotel_count(message):
        logger.debug('Записываем количество отелей')
        cls_user.count_hotel = int(message.text)
        if cls_user.call_method == '/bestdeal':
            bot.send_message(message.chat.id, 'Введите диапазон цен для поиска. (Пример: 0-3000):')

            bot.register_next_step_handler(message, min_max_price)
        else:
            if cls_user.call_method == '/lowprice':
                low_price(message)
            elif cls_user.call_method == '/highprice':
                high_price(message)
    else:
        bot.send_message(message.chat.id, 'Введите число от 1 до 10')
        bot.register_next_step_handler(message, hotel_count)


@logger.catch
def min_max_price(message: Message) -> None:
    """
    Функция для записи минимальной и максимальной цены отеля, а так же запроса диапазона растояния
    """
    cls_user: User = users_dict[f'{message.chat.id}']
    result = check_min_max_price(message)
    if result:
        min_price, max_price = result[0], result[1]
        if int(min_price) > int(max_price):
            bot.send_message(message.chat.id, 'Минимальное число больше максимального, меняю их местами.')
            min_price, max_price = max_price, min_price
        cls_user.price_min, cls_user.price_max = min_price, max_price
        logger.debug('Записываем минимальную и максимальную цену отеля')
        msg = bot.send_message(message.chat.id,
                               'Введите диапазон расстояния, на котором находится отель от центра (Пример: 0-10)')
        bot.register_next_step_handler(msg, min_max_dist)
    else:
        bot.send_message(message.chat.id, 'Ошибка! Введите диапазон цен для поиска (Пример: 1000-5000):')
        bot.register_next_step_handler(message, min_max_price)


@logger.catch
def min_max_dist(message: Message) -> None:
    """
    Функция для записи минимального и максимального диапазона отеля, а так же вызова функции best_deal
    """
    cls_user = users_dict[f'{message.chat.id}']
    result = check_min_max_dist(message)
    if result:
        min_distance, max_distance = result[0], result[1]
        if int(min_distance) > int(max_distance):
            bot.send_message(message.chat.id, 'Минимальное число больше максимального, меняю их местами.')
            min_distance, max_distance = max_distance, min_distance
            logger.debug('Записываем минимальную и максимальную дистанцию')
        cls_user.min_dist, cls_user.max_dist = int(min_distance), int(max_distance)
        best_deal(message)
    else:
        bot.send_message(message.chat.id,
                         'Введите диапазон расстояния, на котором находится отель от центра (Пример: 0-10)')
        bot.register_next_step_handler(message, min_max_dist)


@logger.catch
def menu(message: Message) -> None:
    """
    Функция меню с кнопками команд bestdeal, highprice, lowprice, history, help
    """
    logger.debug('Пользователь зашел в меню')
    menu_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    but_lowprice = types.KeyboardButton('/bestdeal')
    but_highprice = types.KeyboardButton('/highprice')
    but_bestdeal = types.KeyboardButton('/lowprice')
    but_history = types.KeyboardButton('/history')
    but_help = types.KeyboardButton('/help')
    menu_markup.add(but_lowprice)
    menu_markup.add(but_bestdeal, but_highprice)
    menu_markup.add(but_history, but_help)

    bot.send_message(message.chat.id, 'Меню:', reply_markup=menu_markup)
