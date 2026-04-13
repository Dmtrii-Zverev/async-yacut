from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional, Regexp


from .constants import (
    PATTERN,
    MIN_LENGHT_SHORT_ID,
    MAX_LENGHT_SHORT_ID
)


class URLMapForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле')]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Length(MIN_LENGHT_SHORT_ID, MAX_LENGHT_SHORT_ID),
            Optional(),
            Regexp(
                PATTERN,
                message='Допустимы только латниские буквы и цифры'
            )
        ]
    )
    submit = SubmitField('Создать')


class FilesForm(FlaskForm):
    files = MultipleFileField()
    submit = SubmitField('Загрузить')
