from http import HTTPStatus
from typing import Tuple, Union

from flask import Response, jsonify, request

from . import app  # , db
from .error_handlers import InvalidAPIUsage, UniqueError
from .models import URLMap
# from .utils import is_valid_short_id
# from .views import get_unique_short_id

MAX_LENGHT_SHORT_ID = 16


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_link(
    short_id: str
) -> Tuple[Response, Union[int, HTTPStatus]]:
    """
    Получает оригинальную ссылку по её короткому идентификатору.

    Raises:
        InvalidAPIUsage: Если идентификатор не найден в базе данных (404).
    """

    url = URLMap.get_short_url(short_id)
    if url is None:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
    return jsonify({'url': url.original}), HTTPStatus.OK


@app.route('/api/id/', methods=['POST'])
def create_short_link() -> Tuple[Response, Union[int, HTTPStatus]]:
    """
    Создает новую короткую ссылку на основе переданных JSON-данных.

    Выполняет валидацию входных данных: проверку на наличие обязательных полей,
    уникальность ID, допустимую длину и формат символов.

    Raises:
        InvalidAPIUsage: Если тело запроса пустое, отсутствует url,
                         предложенный ID некорректен или уже занят.
    """

    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage(
            'Отсутствует тело запроса'
        )
    url = data.get('url')
    if data.get('short_link'):
        short_link = data.get('short_link')
    elif data.get('custom_id'):
        short_link = data.get('custom_id')
    else:
        short_link = None
    if not url:
        raise InvalidAPIUsage(
            '\"url\" является обязательным полем!'
        )
    try:
        new_url = URLMap.create_short_url(url, short_link)
    except ValueError:
        raise InvalidAPIUsage(
            'Указано недопустимое имя для короткой ссылки'
        )
    except UniqueError:
        raise InvalidAPIUsage(
            'Предложенный вариант короткой ссылки уже существует.'
        )
    return jsonify(
        {'url': url, 'short_link': new_url.full_short_url}
    ), HTTPStatus.CREATED
