import disnake
import httpx

from disnake.ext import commands
from functions.get_song_info import get_current_song


class VoiceManagement(commands.Cog):
    def __init__(self, bot: commands.AutoShardedInteractionBot):
        self.bot = bot
        self.config = bot.config
        self.embed_color = bot.embed_color
        self.embed_color_error = bot.embed_color_error


    @commands.slash_command(name='название', description='Информация о текущей композиции')
    async def current_song(self, inter: disnake.ApplicationCommandInteraction):
        emb = disnake.Embed(
            description=f"Сейчас играет: **{get_current_song(self.config)}**",
            colour=self.embed_color
        )
        emb.set_author(
            name=inter.author.nick if inter.author.nick else inter.author.name,
            icon_url=inter.author.avatar.url if inter.author.avatar else inter.author.default_avatar
        )
        await inter.response.send_message(embed=emb, ephemeral=True)

    @commands.has_permissions(administrator=True)
    @commands.slash_command(name='старт', description='Начать проигрывание потока', default_member_permissions=disnake.Permissions(administrator=True))
    async def join_on_voice_channel(self, inter: disnake.ApplicationCommandInteraction):
        # === Выборка данных о канале из базы данных ===
        async with httpx.AsyncClient() as client:
            channel_id_response = await client.get(
                f"{self.config['SETTINGS']['backend_url']}get_voice_channel_id?guild_id={inter.guild.id}"
            )
        
        # === Блок проверки корректности обработки бэкенда ===
        if channel_id_response.status_code == 200:
            _channel = channel_id_response.json()
        else:
            await inter.response.send_message("❌ На сервере бота произошла ошибка!", ephemeral=True)
            return
        
        # === Блок получение атрибута канала из ID ===
        if _channel is not None:
            channel = inter.guild.get_channel(_channel)

        # === Если канал найден ===
        if channel is not None:
            voice_client = inter.guild.voice_client

            # === Блок обработки подключения к голосовому каналу ===
            if voice_client is None:
                await channel.connect()
                voice_client = inter.guild.voice_client # Задаём новый voice_client поскольку бот вошёл в канал
                emb = disnake.Embed(
                    description=f"Сейчас играет: **{get_current_song(self.config)}**. Приятного прослушивания! 💖",
                    colour=self.embed_color
                )
                emb.set_author(
                    name=f"Отлично, {inter.author.nick if inter.author.nick else inter.author.name}!",
                    icon_url=inter.author.avatar.url if inter.author.avatar else inter.author.default_avatar
                )
                await inter.response.send_message(embed=emb, ephemeral=True)

                # === Запись статуса kicked в базу данных ===
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{self.config['SETTINGS']['backend_url']}add_voice_channel_id", json={
                        'guild_id': inter.guild.id,
                        'channel_id': channel.id,
                        'kicked': False
                })
            else:
                emb = disnake.Embed(
                    description=f"{inter.author.mention}, бот уже подключен к голосовому каналу!",
                    colour=self.embed_color_error
                )
                emb.set_author(
                    name=inter.author.nick if inter.author.nick else inter.author.name,
                    icon_url=inter.author.avatar.url if inter.author.avatar else inter.author.default_avatar
                )
                await inter.response.send_message(embed=emb, ephemeral=True)
                return
            
        else:
            emb = disnake.Embed(
                description=f"{inter.author.mention}, боту не удалось определить канал для проигрывания!",
                colour=self.embed_color_error
            )
            emb.set_author(
                name=inter.author.nick if inter.author.nick else inter.author.name,
                icon_url=inter.author.avatar.url if inter.author.avatar else inter.author.default_avatar
            )
            emb.set_footer(
                text="Возможно, вы не указали канал в настройках бота..."
            )
            await inter.response.send_message(embed=emb, ephemeral=True)
   
    @commands.has_permissions(administrator=True)
    @commands.slash_command(name='отключить', description='Отключить бота от голосового канала', default_member_permissions = disnake.Permissions(administrator=True))
    async def leave_from_voice_channnel(self, inter: disnake.ApplicationCommandInteraction):
        voice_client = inter.guild.voice_client
        if voice_client is not None:
            await voice_client.disconnect()
            emb = disnake.Embed(
                description="Бот был отключён и не сможет играть на данном сервере пока вы не пригласите его в канал заново!",
                colour=self.embed_color
            )
            emb.set_author(
                name=inter.author.nick if inter.author.nick else inter.author.name,
                icon_url=inter.author.avatar.url if inter.author.avatar else inter.author.default_avatar
            )
            await inter.response.send_message(embed=emb, ephemeral=True)
            
            # === Изменение статуса kicked ===
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.config['SETTINGS']['backend_url']}change_kicked_status", json={
                    'guild_id': inter.guild.id,
                    'kicked': True
                })
        else:
            emb = disnake.Embed(
                description="Бот не был присоединён ни к одному каналу!",
                colour=self.embed_color_error
            )
            emb.set_author(
                name=inter.author.nick if inter.author.nick else inter.author.name,
                icon_url=inter.author.avatar.url if inter.author.avatar else inter.author.default_avatar
            )
            await inter.response.send_message(embed=emb, ephemeral=True)


def setup(bot: commands.AutoShardedInteractionBot):
    bot.add_cog(VoiceManagement(bot))
