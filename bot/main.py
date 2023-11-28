import disnake
import os
import asyncio
import configparser

from disnake.ext import commands
from loguru import logger

intents = disnake.Intents.default()
intents.members = True

bot = commands.AutoShardedInteractionBot(
    intents=intents
)

config = configparser.ConfigParser()
config.read("bot/configs/config.ini")


async def main():
    bot.embed_color = 0x2b2d31
    bot.embed_color_error = 0xc03c4d 
    bot.config = config
    for folder in os.listdir("bot/cogs"):
        for file in os.listdir(f"bot/cogs/{folder}"):
            if file.startswith("COG_"):
                bot.load_extension(f"cogs.{folder}.{file[:-3]}")
                logger.success(
                    "loading {name} {version} / {folder}.{file}".format(
                        name=config["INFO"]["name"],
                        version=config["INFO"]["version"],
                        folder=folder,
                        file=file[:-3]
                    )
                )


if __name__ == '__main__':
    asyncio.run(main())
    bot.run(config["SETTINGS"]["token"])
