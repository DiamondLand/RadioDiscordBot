import configparser
from tortoise import fields
from tortoise.models import Model

config = configparser.ConfigParser()
config.read("bot/configs/config.ini")


class VoiceManagment(Model):
    guild_id = fields.BigIntField(unique=True, pk=True)
    channel_id = fields.BigIntField()
    kicked = fields.BooleanField()