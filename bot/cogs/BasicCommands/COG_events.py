import disnake
import httpx
import itertools

from loguru import logger
from disnake.ext import commands, tasks
from functions.play_audio import play_music


class Events(commands.Cog):
    def __init__(self, bot = commands.AutoShardedInteractionBot):
        self.bot = bot
        self.config = bot.config
        self.embed_color = bot.embed_color
        self.embed_color_error = bot.embed_color_error
    

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Cog's loaded")
        
        for guild in self.bot.guilds:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.config['SETTINGS']['backend_url']}get_voice_channel_id?guild_id={guild.id}"
                )
                kicked_response = await client.get(
                    f"{self.config['SETTINGS']['backend_url']}get_kicked_status?guild_id={guild.id}"
                )
            if response.status_code == 200 and response.json() and kicked_response.status_code == 200 and kicked_response.json() == False:
                try:
                    channel = self.bot.get_channel(response.json())
                    voice_channel = await channel.connect()
                except Exception as _ex:
                    print(_ex)

                if len(voice_channel.channel.members) > 1:
                    await play_music(channel=voice_channel)
                    print("Играет")
                else:
                    print("Не играет")

        logger.info("Music start")


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # === Игнорирование действий ботов ===
        if not member.bot:

            channel = after.channel or before.channel
            # Проверка условий из вашего списка
            if channel:
                voice_client = disnake.utils.get(self.bot.voice_clients, guild=channel.guild)

                if len(channel.members) == 1 and self.bot.user in channel.members:
                    # Остался только бот в канале, прекращаем воспроизведение
                    if voice_client and voice_client.is_playing():
                        voice_client.stop()
                        print("Остановлено 1")

                elif len(channel.members) == 2 and self.bot.user in channel.members:
                    # В голосовом канале появился еще один пользователь (без бота)
                    if voice_client and not voice_client.is_playing():
                        await play_music(channel)
                        print("Включено")

            elif before.channel and not after.channel:
                # Пользователь покинул канал
                voice_client = disnake.utils.get(self.bot.voice_clients, guild=before.channel.guild)
                if len(before.channel.members) == 1 and self.bot.user in before.channel.members:
                    # Остался только бот в канале, прекращаем воспроизведение
                    if voice_client and voice_client.is_playing():
                        voice_client.stop()
                        print("Остановлено 2")

        """# === Проверяем, входит ли пользователь в голосовой канал, где присутствует бот ===
        bot_channel = next((vc for vc in self.bot.voice_clients if vc.guild.id == member.guild.id), None)

        if member.id != self.bot.user.id:
            # === Проверяем, был ли пользователь в голосовом канале и вышел из него ===
            if before.channel and not after.channel:
                # === Проверяем, остались ли еще пользователи в голосовом канале ===
                channel_members = [m for m in before.channel.members if not m.bot]
                if not channel_members:
                    if bot_channel and bot_channel.channel == before.channel:
                        bot_channel.stop()
                        print("Остановлено")
                    return

            # === Проверяем, входит ли пользователь в голосовой канал, где присутствует бот ===
            if bot_channel and bot_channel.channel == after.channel:
                await play_music(channel=after.channel)
                print("Включено")
            else:
                if bot_channel and len(bot_channel.channel.members) == 1:
                    # При перемещении пользователя
                    bot_channel.stop()
                    print("Остановлено 1")"""
        

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
        
        
