from http import HTTPStatus
from typing import Any, Union, Dict, Tuple

from flask import Response, jsonify, render_template

from . import app


class InvalidAPIUsage(Exception):
    """Исключение для обработки ошибок валидации и использования API."""

    status_code = HTTPStatus.BAD_REQUEST

    def __init__(
            self, message: str,
            status_code: Union[int, HTTPStatus, None] = None
    ):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self) -> Dict[str, str]:
        return {'message': self.message}


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(
    error: InvalidAPIUsage
) -> Tuple[Response, Union[int, HTTPStatus]]:
    """Обработчик кастомных ошибок API."""
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(404)
def page_not_found(error: Any) -> Tuple[str, Union[int, HTTPStatus]]:
    """Обработчик ошибки 404."""
    return render_template('404.html'), HTTPStatus.NOT_FOUND


@app.errorhandler(500)
def internal_error(error: Any) -> Tuple[str, Union[int, HTTPStatus]]:
    """Обработчик ошибки 500."""
    return render_template('500.html'), HTTPStatus.INTERNAL_SERVER_ERROR
