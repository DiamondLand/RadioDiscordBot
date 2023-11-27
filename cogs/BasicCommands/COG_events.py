import disnake
import time
import itertools

from loguru import logger
from disnake.ext import commands, tasks
from functions.play_audio import play_music


class Events(commands.Cog):
    def __init__(self, bot = commands.AutoShardedInteractionBot):
        self.bot = bot
        self.embed_color = bot.embed_color
        self.embed_color_error = bot.embed_color_error
    

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Cog's loaded")
        for guild in self.bot.guilds:
            for voice_channel in guild.voice_channels:
                # Проверяем, есть ли хотя бы один человек в голосовом канале
                if voice_channel.members:
                    # Если бот уже подключен к голосовому каналу, пропускаем
                    if guild.voice_client is not None:
                        continue

                    # Если нет, подключаемся и воспроизводим музыку
                    await play_music(channel=voice_channel)
                else:
                    # Если нет никого в голосовом канале, прекращаем воспроизведение
                    if guild.voice_client is not None and guild.voice_client.is_playing():
                        guild.voice_client.stop()


        logger.info("Music start")


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Проверяем, входит ли пользователь в голосовой канал, где присутствует бот
        bot_channel = next((vc for vc in self.bot.voice_clients if vc.guild.id == member.guild.id), None)

        # Проверяем, был ли пользователь в голосовом канале и вышел из него
        if before.channel and not after.channel:
            # Проверяем, остались ли еще пользователи в голосовом канале (кроме бота)
            channel_members = [m for m in before.channel.members if not m.bot]
            if not channel_members:
                # Если больше нет пользователей, кроме бота, то прекращаем воспроизведение
                if bot_channel and bot_channel.channel == before.channel:
                    bot_channel.stop()
                return

        # Проверяем, входит ли пользователь в голосовой канал, где присутствует бот
        if bot_channel and bot_channel.channel == after.channel:
            await play_music(channel=after.channel)


    @commands.Cog.listener()
    async def on_slash_command_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, commands.MissingPermissions):
            emb = disnake.Embed(
                description="У вас недостаточно прав, для использования этой команды!",
                colour=self.embed_color_error
            )
            emb.set_author(
                name=inter.author.nick if inter.author.nick else inter.author.name +
                ", произошла ошибка!",
                icon_url=inter.author.avatar,
            )
            try:
                await inter.response.send_message(embed=emb, ephemeral=True)
            except:
                await inter.send(embed=emb, ephemeral=True)


def setup(bot: commands.AutoShardedInteractionBot):
    bot.add_cog(Events(bot))
        
        
