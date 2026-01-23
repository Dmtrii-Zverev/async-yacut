import string
import random

from flask import abort, render_template, flash, redirect

from . import app, db
from .forms import URLMapForm, FilesForm
from .models import URLMap
from .ya_disk import async_upload_files_to_disk


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
    short_id = get_random_short_id()
    while URLMap.query.filter_by(short=short_id).first() is not None:
        short_id = get_random_short_id()
    return short_id


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLMapForm()
    if form.validate_on_submit():
        original = form.original_link.data
        custom_id = form.custom_id.data
        if not custom_id:
            custom_id = get_unique_short_id()
        elif (
            custom_id == 'files' or
            URLMap.query.filter_by(original=original).first() is not None
        ):
            flash('Предложенный вариант короткой ссылки уже существует.')
            return render_template('index.html', form=form)
        url = URLMap(
            original=original,
            short=custom_id
        )
        db.session.add(url)
        db.session.commit()
        flash('Ваша новая ссылка готова!')
        return render_template('index.html', form=form, custom_id=custom_id)
    return render_template('index.html', form=form)


@app.route('/files', methods=['GET', 'POST'])
async def files_view():
    form = FilesForm()
    results = []
    if form.validate_on_submit():
        uploaded_urls = await async_upload_files_to_disk(form.files.data)
        for file, url in zip(form.files.data, uploaded_urls):
            custom_id = get_unique_short_id()
            while URLMap.query.filter_by(short=custom_id).first() is not None:
                custom_id = get_unique_short_id()
            new_map = URLMap(
                original=url,
                short=custom_id
            )
            db.session.add(new_map)
            results.append({
                'filename': file.filename,
                'short_url': custom_id
            })
            db.session.commit()
    return render_template('add_files.html', form=form, results=results)


@app.route('/<string:short_id>')
def redirect_to_url(short_id):
    url = URLMap.query.filter_by(short=short_id).first()
    if url:
        return redirect(url.original)
    abort(404)
