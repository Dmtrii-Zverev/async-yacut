from datetime import datetime
import string
import random
import re

from flask import url_for

from yacut import db
from .constants import MAX_LENGHT_SHORT_ID, LENGHT_SHORT_ID, PATTERN, BAD_WORDS
from .error_handlers import UniqueError


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String, nullable=False)
    short = db.Column(
        db.String(MAX_LENGHT_SHORT_ID), nullable=False, unique=True
    )
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @property
    def full_short_url(self):
        return url_for('redirect_to_url', short_id=self.short, _external=True)

    @staticmethod
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

    @classmethod
    def get_unique_short_id(cls):
        """Проверяет что сгенерированный индетификатор уникальный.

        Идентификатор создается с помощью функции get_random_short_id
        после чего проверяется на уникальность в бд.

        Returns:
            str: Уникальный индетификатор.
        """

        short_id = cls.get_random_short_id()
        while cls.get_short_url(short_id) is not None:
            short_id = cls.get_random_short_id()
        return short_id

    @staticmethod
    def is_valid_short_id(short_id: str) -> bool:
        """
        Проверяет идентификатор на соответствие символам латиницы и цифрам.
        """
        if re.fullmatch(PATTERN, short_id):
            return True
        return ''

    @classmethod
    def get_short_url(cls, short_id):
        return cls.query.filter_by(short=short_id).first()

    @classmethod
    def create_short_url(cls, url, short_id=None):
        if short_id is None:
            short_id = cls.get_unique_short_id()
        elif (
            short_id in BAD_WORDS or
            not cls.is_valid_short_id(short_id) or
            len(short_id) > MAX_LENGHT_SHORT_ID
        ):
            raise ValueError
        elif cls.get_short_url(short_id) is not None:
            raise UniqueError
        new_url = cls(
            original=url,
            short=short_id
        )
        db.session.add(new_url)
        db.session.commit()
        return new_url

    def to_dict(self):
        return {
            'id': self.id,
            'original': self.original,
            'short': self.short,
            'timestamp': self.timestamp
        }

    def from_dict(self, data):
        for field in ['id', 'original', 'short', 'timestamp']:
            if field in data:
                setattr(self, field, data[field])
