import disnake
import asyncio
import httpx
import itertools

from loguru import logger
from disnake.ext import commands, tasks
from functions.play_audio import play_music
from functions.get_song_info import get_current_song


class Events(commands.Cog):
    def __init__(self, bot: commands.AutoShardedInteractionBot):
        self.bot = bot
        self.config = bot.config
        self.embed_color = bot.embed_color
        self.embed_color_error = bot.embed_color_error
        self.status = itertools.cycle([
            "музыку на {guilds} серверах!",
            "{song}"
        ])
    
    def get_bot_voice_channel(self, guild):
        return next((vc for vc in guild.voice_channels if self.bot.user in vc.members), None)
    
    
    # === основной таск на смену статуса и проверку людей в канале ===
    @tasks.loop(seconds=30.0)
    async def main_task(self):
        activity_name = next(self.status).format(
            guilds=len(self.bot.guilds),
            song=get_current_song(self.config)[:100]
        )
        await self.bot.change_presence(
            activity=disnake.Activity(
                type=disnake.ActivityType.listening,
                name=activity_name
            )
        )

        for guild in self.bot.guilds:
            channel = self.get_bot_voice_channel(guild)
            if channel:
                voice_members = [member for member in channel.members if not member.bot]
                voice_client = channel.guild.voice_client
                if voice_client:
                    if len(voice_members) < 1 and voice_client.is_playing():
                        voice_client.stop()
                elif len(voice_members) >= 1 and not voice_client.is_playing():
                    play_music(channel=channel)
                    


    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Cog's loaded")
        
        self.main_task.start()
        logger.info("Main Task started")

        for guild in self.bot.guilds:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.config['SETTINGS']['backend_url']}get_voice_channel_id?guild_id={guild.id}"
                )
                kicked_response = await client.get(
                    f"{self.config['SETTINGS']['backend_url']}get_kicked_status?guild_id={guild.id}"
                )
            if (
                response.status_code == 200
                and response.json()
                and kicked_response.status_code == 200
                and not kicked_response.json()
            ):
                channel = self.bot.get_channel(response.json())
                if channel:
                    try:
                        voice_channel = await channel.connect()
                        if len(voice_channel.channel.members) > 1:
                            play_music(channel=voice_channel)
                    except:
                        pass
        logger.info("Bot join last voices")


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # === Игнорирование действий ботов ===
        if member.bot:
            return

        channel_before, channel_after = before.channel, after.channel

        # === Пользователь был в канале с ботом и вышел из него ===
        if channel_before and self.bot.user in channel_before.members and channel_after != channel_before:
            voice_members = [member for member in channel_before.members if not member.bot]
            voice_client = channel_before.guild.voice_client
            if len(voice_members) < 1 and voice_client and voice_client.is_playing():
                voice_client.stop()

        # === Пользователь зашёл в канал с ботом ===
        elif channel_after and self.bot.user in channel_after.members and channel_before != channel_after:
            voice_members = [member for member in channel_after.members if not member.bot]
            voice_client = channel_after.guild.voice_client
            if len(voice_members) >= 1 and voice_client and not voice_client.is_playing():
                play_music(channel=channel_after)
        
        # === Если наш бот ===
        elif member.id == self.bot.user.id and channel_after:
            voice_members = [member for member in channel_after.members if not member.bot]
            voice_client = channel_after.guild.voice_client

            if len(voice_members) >= 1 and voice_client and not voice_client.is_playing():
                await asyncio.sleep(1)
                if voice_client.is_connected():
                    play_music(channel=channel_after)
            elif voice_client and voice_client.is_playing():
                voice_client.stop()


    @commands.Cog.listener()
    async def on_slash_command_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, commands.MissingPermissions):
            emb = disnake.Embed(
                description="У вас недостаточно прав, для использования этой команды!",
                colour=self.embed_color_error
            )
        else:
            emb = disnake.Embed(
                description="В данный момент вы не можете использовать эту команду.",
                colour=self.embed_color_error
            )
        
        emb.set_author(
            name=f"{inter.author.nick or inter.author.name}, произошла ошибка!",
            icon_url=inter.author.avatar,
        )

        try:
            await inter.response.send_message(embed=emb, ephemeral=True)
        except:
            await inter.send(embed=emb, ephemeral=True)

def setup(bot: commands.AutoShardedInteractionBot):
    bot.add_cog(Events(bot))
