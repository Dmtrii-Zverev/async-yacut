from flask import flash, redirect, render_template

from . import app, db
from .forms import FilesForm, URLMapForm
from .models import URLMap
from .utils import get_unique_short_id
from .ya_disk import async_upload_files_to_disk


@app.route('/', methods=['GET', 'POST'])
def index_view():
    """
    Обрабатывает главную страницу: отображает форму и создает короткие ссылки.

    GET: Отображает пустую форму для ввода длинной ссылки.
    POST: Валидирует данные, проверяет уникальность короткого идентификатора,
    сохраняет новую запись в базу данных и выводит результат пользователю.

    Returns:
        str: Отрендеренный HTML-шаблон 'index.html'.
    """
    form = URLMapForm()
    if form.validate_on_submit():
        original = form.original_link.data
        custom_id = form.custom_id.data
        if not custom_id:
            custom_id = get_unique_short_id()
        elif (
            custom_id == 'files' or
            URLMap.query.filter_by(short=custom_id).first() is not None
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
    """
    Загружает файлы на яндекс диск и создает короткие ссылки для скачивания.

    GET: Отображает форму для загрузки нескольких файлов.
    POST:
        1. Асинхронно загружает выбранные файлы на Яндекс.Диск.
        2. Для каждого успешно загруженного файла
           генерирует уникальный короткий ID.
        3. Формирует список результатов для отображения пользователю.

    Returns:
        str: Отрендеренный HTML-шаблон 'add_files.html'
        со списком созданных ссылок для скачивания.
    """

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
    """ Перенапраляет пользователя на оригинальный источник.

        Args:
            short_id (str): Уникальный индетификатор.
        Returns:
            Response: Объект перенаправления
    """

    url = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url.original)
