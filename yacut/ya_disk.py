import urllib

import aiohttp
import asyncio

from . import app


API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'
AUTH_HEADERS = {
    'Authorization': f'OAuth {app.config["DISK_TOKEN"]}'
}


async def async_upload_files_to_disk(files):
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
    async with session.put(
        upload_url,
        data=file.stream
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
