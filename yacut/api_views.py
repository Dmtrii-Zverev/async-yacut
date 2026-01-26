from http import HTTPStatus
from typing import Tuple, Union

from flask import Response, jsonify, request

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .utils import is_valid_short_id
from .views import get_unique_short_id

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

    url = URLMap.query.filter_by(short=short_id).first()
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
    if not short_link:
        short_link = get_unique_short_id()
    elif (
        short_link == 'files' or
        not is_valid_short_id(short_link) or
        len(short_link) > MAX_LENGHT_SHORT_ID
    ):
        raise InvalidAPIUsage(
            'Указано недопустимое имя для короткой ссылки'
        )
    elif URLMap.query.filter_by(short=short_link).first() is not None:
        raise InvalidAPIUsage(
            'Предложенный вариант короткой ссылки уже существует.'
        )
    new_url = URLMap(
        original=url,
        short=short_link
    )
    db.session.add(new_url)
    db.session.commit()
    return jsonify(
        {'url': url, 'short_link': request.host_url + short_link}
    ), HTTPStatus.CREATED
