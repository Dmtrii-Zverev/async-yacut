from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import URLField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp


class URLMapForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле')]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Length(1, 16),
            Optional(),
            Regexp(
                r'^[A-Za-z0-9]+$',
                message='Допустимы только латниские буквы и цифры'
            )
        ]
    )
    submit = SubmitField('Создать')


class FilesForm(FlaskForm):
    files = MultipleFileField()
    submit = SubmitField('Загрузить')