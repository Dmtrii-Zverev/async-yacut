import random
import re
import string

from .models import URLMap

LENGHT_SHORT_ID = 6


def get_random_short_id(length_id=LENGHT_SHORT_ID):
    """Генерирует случайный идентификатор для формирования коротких ссылок.

    Идентификатор формируется из латинских букв (регистрозависимых)
    и цифр от 0 до 9.

    Args:
        length_id (int): Длина генерируемого идентификатора.
            По умолчанию используется константа LENGHT_SHORT_ID.

    Returns:
        str: Строка из случайных символов заданной длины.
    """

    seq = string.digits + string.ascii_letters
    return ''.join(random.choices(seq, k=length_id))


def get_unique_short_id():
    """Проверяет что сгенерированный индетификатор уникальный.

    Идентификатор создается с помощью функции get_random_short_id
    после чего проверяется на уникальность в бд.

    Returns:
        str: Уникальный индетификатор.
    """

    short_id = get_random_short_id()
    while URLMap.query.filter_by(short=short_id).first() is not None:
        short_id = get_random_short_id()
    return short_id


def is_valid_short_id(short_id: str) -> bool:
    """
    Проверяет идентификатор на соответствие символам латиницы и цифрам.
    """

    pattern = r'^[A-Za-z0-9]+$'
    if re.fullmatch(pattern, short_id):
        return True
    return False