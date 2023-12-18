import disnake
import httpx

from disnake.ext import commands
from functions.get_song_info import get_current_song


class Settings(commands.Cog):
    def __init__(self, bot: commands.AutoShardedInteractionBot):
        self.bot = bot
        self.config = bot.config
        self.embed_color = bot.embed_color
        self.embed_color_error = bot.embed_color_error


    @commands.has_permissions(administrator=True)
    @commands.slash_command(name='выбрать-канал', description='Выбрать канал для вещания', default_member_permissions=disnake.Permissions(administrator=True))
    async def set_voice_channel(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.VoiceChannel = (commands.Param(default=None, name="канал", description="какой канал будет использоваться для проигрывания потока?"))):
        # === Присоединение бота к каналу, указанному в slash команде, или в тот, где находится участник ===
        if channel is None:
            if inter.author.voice:
                channel = inter.author.voice.channel
            else:
                emb = disnake.Embed(
                    description=f"{inter.author.mention}, чтобы выбрать канал для вещания вам потребуется указать или зайти в него.",
                    colour=self.embed_color_error
                )
                emb.set_author(
                    name=f"Не-а, {inter.author.nick if inter.author.nick else inter.author.name}!",
                    icon_url=inter.author.avatar.url if inter.author.avatar else inter.author.default_avatar
                )
                await inter.response.send_message(embed=emb, ephemeral=True)
                return
        
        # === Получение ID канала ===
        async with httpx.AsyncClient() as client:
            channel_id_response = await client.get(
                f"{self.config['SETTINGS']['backend_url']}get_voice_channel_id?guild_id={inter.guild.id}"
            )

        # === Блок проверки обработки бэкенда ===
        if channel_id_response.status_code == 200:
            _channel = channel_id_response.json()
        else:
            await inter.response.send_message("❌ На сервере бота произошла ошибка!", ephemeral=True)
            return
        
        # === Если выбран не тот же канал что указан в базе ===
        if channel.id != _channel:
            voice_client = inter.guild.voice_client

            # === Если не подключен, то подключаем ===
            if voice_client is None:
                await channel.connect()
                emb = disnake.Embed(
                    description=f"{inter.author.mention}, теперь **{channel.name}** будет каналом для воспроизведения потока.\
                    \n\nСейчас играет: **{get_current_song(self.config)}**. Приятного прослушивания! 💖",
                    colour=self.embed_color
                )
                emb.set_author(
                    name=f"Отлично, {inter.author.nick if inter.author.nick else inter.author.name}!",
                    icon_url=inter.author.avatar.url if inter.author.avatar else inter.author.default_avatar
                )
                await inter.response.send_message(embed=emb, ephemeral=True)
            # === Если подключён, но указан другой канал, то перемещаем ===
            else:
                await voice_client.move_to(channel)
                emb = disnake.Embed(
                    description=f"{inter.author.mention}, новый канал для воспроизведения потока — **{channel.name}**.\
                    \n\nСейчас играет: **{get_current_song(self.config)}**. Приятного прослушивания! 💖",
                    colour=self.embed_color
                )
                emb.set_author(
                    name=f"Отлично, {inter.author.nick if inter.author.nick else inter.author.name}!",
                    icon_url=inter.author.avatar.url if inter.author.avatar else inter.author.default_avatar
                )
                await inter.response.send_message(embed=emb, ephemeral=True)
            
            # === Запись статуса kicked ===
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.config['SETTINGS']['backend_url']}add_voice_channel_id", json={
                    'guild_id': inter.guild.id,
                    'channel_id': channel.id,
                    'kicked': False
                })
            
        else:
            emb = disnake.Embed(
                description=f"{inter.author.mention}, выбранный вами **{channel.name}** уже является каналом вещания бота!",
                colour=self.embed_color_error
            )
            emb.set_author(
                name=f"Повторюшка {inter.author.nick if inter.author.nick else inter.author.name}!",
                icon_url=inter.author.avatar.url if inter.author.avatar else inter.author.default_avatar
            )
            await inter.response.send_message(embed=emb, ephemeral=True)
            return

    @commands.has_permissions(administrator=True)
    @commands.slash_command(name='удалить-канал', description='Удалить канал для вещания', default_member_permissions=disnake.Permissions(administrator=True))
    async def delete_voice_channel(self, inter: disnake.ApplicationCommandInteraction):
        # === Получение ID канала ===
        async with httpx.AsyncClient() as client:
            channel_id_response = await client.get(
                f"{self.config['SETTINGS']['backend_url']}get_voice_channel_id?guild_id={inter.guild.id}"
            )

        # === Блок проверки корректности обработки бэкенда ===
        if channel_id_response.status_code != 200:
            await inter.response.send_message("❌ На сервере бота произошла ошибка!", ephemeral=True)
            return
        
        # === Если есть данные, то удаляем ===
        if channel_id_response.json():
            # === Удаление ID канала ===
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.config['SETTINGS']['backend_url']}delete_voice_channel_id?guild_id={inter.guild.id}"
                )

            voice_client = inter.guild.voice_client
            # === Если подключен к каналу, то выходим ===
            if voice_client.is_connected():
                await voice_client.disconnect()

            emb = disnake.Embed(
                description=f"{inter.author.mention}, канал для воспроизведения потока был удалён. Бот не будет играть на данном сервере!",
                colour=self.embed_color
            )
            emb.set_author(
                name=inter.author.nick if inter.author.nick else inter.author.name,
                icon_url=inter.author.avatar.url if inter.author.avatar else inter.author.default_avatar
            )
            await inter.response.send_message(embed=emb, ephemeral=True)
        else:
            emb = disnake.Embed(
                description=f"{inter.author.mention}, на данном сервере отсутствует канал для воспроизведения потока!",
                colour=self.embed_color_error
            )
            emb.set_author(
                name=f"Как же так, {inter.author.nick if inter.author.nick else inter.author.name}?",
                icon_url=inter.author.avatar.url if inter.author.avatar else inter.author.default_avatar
            )
            await inter.response.send_message(embed=emb, ephemeral=True)


def setup(bot: commands.AutoShardedInteractionBot):
    bot.add_cog(Settings(bot))