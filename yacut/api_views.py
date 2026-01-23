import re

from flask import jsonify, request

from . import app, db
from .models import URLMap
from .error_handlers import InvalidAPIUsage
from .views import get_unique_short_id


def is_valid_short_id(short_id):
    pattern = r'^[A-Za-z0-9]+$'
    if re.fullmatch(pattern, short_id):
        return True
    return False


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_link(short_id):
    url = URLMap.query.filter_by(short=short_id).first()
    if url is None:
        raise InvalidAPIUsage('Указанный id не найден', 404)
    return jsonify({'url': url.original}), 200


@app.route('/api/id/', methods=['POST'])
def create_short_link():
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
        len(short_link) > 16
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
    print(short_link)
    return jsonify(
        {'url': url, 'short_link': request.host_url + short_link}
    ), 201
