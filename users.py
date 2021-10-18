from dataclasses import dataclass
import datetime

users_dict = {}


@dataclass
class User:
    chat_id: int
    city_name: str = None
    city_id = None
    call_method: str = None
    count_hotel: int = None
    locale: str = None
    price_min: str = None
    price_max: str = None
    min_dist: int = None
    max_dist: int = None
    photo: bool = False
    count_photo: int = None
    check_in: datetime = datetime.date.today()
    check_out: datetime = check_in + datetime.timedelta(days=1)
    history_list = list()
