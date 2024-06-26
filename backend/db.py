import configparser

from tortoise.contrib.fastapi import register_tortoise

config = configparser.ConfigParser()
config.read("bot/configs/config.ini")


def init(app):
    """Функция для инициализации базы данных."""
    register_tortoise(
        app,
        db_url='sqlite://bot/assets/database.db',
        modules={"models": ['app.models']},
        generate_schemas=True,
        add_exception_handlers=False,
    )
