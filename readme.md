# YaCut
#### Проект YaCut — это сервис укорачивания ссылок. Его назначение — ассоциировать длинную пользовательскую ссылку с короткой, которую предлагает сам пользователь или предоставляет сервис.
#### Дополнительная функция YaCut — загрузка сразу нескольких файлов на Яндекс Диск и предоставление коротких ссылок пользователю для скачивания этих файлов.

## Используемые технологии
* Python 3.12: Основной язык разработки.
* Фреймворк: Flask 3.0.2
* База данных: SQLAlchemy 2.0 (ORM), Flask-Migrate (Alembic) для миграций.
* Асинхронность: aiohttp (для работы с внешними API), asyncio.
* Валидация данных: Flask-WTF / WTForms.
* Тестирование: Pytest (pytest-asyncio, pytest-aiohttp).
* Линтинг: Flake8.


### Как запустить проект Yacut:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone 
```

```
cd yacut
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Создать в директории проекта файл .env с четыремя переменными окружения:

```
FLASK_APP=yacut
FLASK_ENV=development
SECRET_KEY=your_secret_key
DB=sqlite:///db.sqlite3
```

Создать базу данных и применить миграции:

```
flask db upgrade
```

Запустить проект:

```
flask run
```
###  API Эндпоинты
* /api/id/ — POST-запрос на создание новой короткой ссылки.
* /api/id/<short_id>/ — GET-запрос на получение оригинальной ссылки по указанному короткому идентификатору.
## Авторы 
Дмитрий Зверев: 
https://github.com/Dmitrii-Zverev

Яндекс практикум: 
https://github.com/yandex-praktikum 
