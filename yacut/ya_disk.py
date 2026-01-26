import asyncio
import urllib

import aiohttp

from . import app

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'
AUTH_HEADERS = {
    'Authorization': f'OAuth {app.config["DISK_TOKEN"]}'
}


async def async_upload_files_to_disk(files):
    """
    Корутина для массовой асинхронной загрузки файлов на Яндекс диск.

    Создает группу задач для одновременной загрузки всех переданных файлов
    с использованием одной сессии aiohttp.

    Args:
        files (list): Список файлов.

    Returns:
        list[str] | None: Список прямых ссылок на загруженные файлы или None,
                          если список файлов пуст.
    """

    if files:
        tasks = []
        async with aiohttp.ClientSession() as session:
            for file in files:
                tasks.append(
                    asyncio.ensure_future(
                        upload_file_and_get_url(session, file)
                    )
                )
            urls = await asyncio.gather(*tasks)
        return urls


async def upload_file_and_get_url(session, file):
    """
    Корутина для поэтапной загрузки одного файла на Яндек диск.

    Процесс включает:
    1. Запрос ссылки для загрузки (GET).
    2. Загрузку бинарных данных файла (PUT).
    3. Получение ссылки для скачивания (GET).

    Args:
        session (aiohttp.ClientSession): Активная асинхронная сессия.
        file: Объект файла, имеющий атрибуты `filename` и `stream`.

    Returns:
        str: Прямая ссылка (href) на файл в облачном хранилище.

    Raises:
        KeyError: Если в ответе API отсутствуют ожидаемые ключи.
        aiohttp.ClientError: При сетевых ошибках в процессе запросов.
    """

    payload = {
        'path': f'app:/{file.filename}',  # noqa: E231
        'overwrite': 'True'
    }
    async with session.get(
        REQUEST_UPLOAD_URL,
        params=payload,
        headers=AUTH_HEADERS
    ) as response:
        data = await response.json()
        upload_url = data['href']
    loop = asyncio.get_event_loop()
    file_data = await loop.run_in_executor(None, file.stream.read)
    async with session.put(
        upload_url,
        data=file_data
    ) as response:
        location = response.headers['Location']
        location = urllib.parse.unquote(location)
        location = location.replace('/disk', '')
    async with session.get(
        DOWNLOAD_LINK_URL,
        params={'path': location},
        headers=AUTH_HEADERS
    ) as response:
        data = await response.json()
        link = data['href']
    return link
