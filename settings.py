import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///db.sqlite3')
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret_key_dev')
    DISK_TOKEN = os.getenv(
        'DISK_TOKEN', 'y0__xCeipvDBBjU8zwgwP2OiBZ2SwQxg0ERUfIfurTUM20uUKhf6A'
    )
