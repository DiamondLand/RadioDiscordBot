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

            if response.status_code == 200 and response.json():
                try:
                    channel = self.bot.get_channel(response.json())
                    voice_channel = await channel.connect()
                    await play_music(channel=voice_channel)
                except Exception as _ex:
                    print(_ex)

               
        logger.info("Music start")


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # === Проверяем, входит ли пользователь в голосовой канал, где присутствует бот ===
        bot_channel = next((vc for vc in self.bot.voice_clients if vc.guild.id == member.guild.id), None)

        # === Проверяем, был ли пользователь в голосовом канале и вышел ли из него ===
        if before.channel and not after.channel:
            # === Проверяем, остались ли еще пользователи в голосовом канале ===
            channel_members = [m for m in before.channel.members if not m.bot]
            if not channel_members:
                if bot_channel.is_connected() and bot_channel.channel == before.channel:
                    bot_channel.stop()
                    print("остановлено")
                return

        # === Проверяем, входит ли пользователь в голосовой канал, где присутствует бот ===
        if after.channel:
            if not bot_channel.is_connected() or bot_channel.channel.id != after.channel.id:
                # === Проверяем есть ли бот в канале ===
                bot_channel = await after.channel.connect()
        await play_music(channel=bot_channel)


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
        
        
