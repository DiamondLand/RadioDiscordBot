import disnake
import httpx

from disnake.ext import commands
from functions.play_audio import play_music


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
                await inter.response.send_message("❌ Укажите канал для проигрывания потока или же зайдите в него!", ephemeral=True)
                return
        
        # === Получение ID канала ===
        async with httpx.AsyncClient() as client:
            channel_id_response = await client.get(
                f"{self.config['SETTINGS']['backend_url']}get_voice_channel_id?guild_id={inter.guild.id}"
            )
        if channel_id_response.status_code == 200:
            _channel = channel_id_response.json()
        
        # === Если выбранный канал не тот же, что указан в базе ===
        if channel.id != _channel:
            voice_client = inter.guild.voice_client
            if not voice_client:
                # === Если не подключен, то подключаем ===
                voice_channel = await channel.connect()
                emb = disnake.Embed(
                    description=f"{inter.author.mention}, теперь **{channel.name}** будет каналом для воспроизведения потока.",
                    colour=self.embed_color
                )
                emb.set_author(
                    name=f"Отлично, {inter.author.nick if inter.author.nick else inter.author.name}!",
                    icon_url=inter.author.avatar.url if inter.author.avatar else inter.author.default_avatar
                )
                await inter.response.send_message(embed=emb, ephemeral=True)
            else:
                # === Если подключен к этому же каналу ===
                if voice_client.channel.id == channel.id:
                    await inter.response.send_message("❌ Бот уже подключён к этому голосовому каналу", ephemeral=True)
                    return
                else:
                    # === Если подключён, но указан другой канал, то перемещаем ===
                    voice_channel = await voice_client.move_to(channel)
                    emb = disnake.Embed(
                        description=f"{inter.author.mention}, новый канал для воспроизведения потока — **{channel.name}**.",
                        colour=self.embed_color
                    )
                    emb.set_author(
                        name=f"Отлично, {inter.author.nick if inter.author.nick else inter.author.name}!",
                        icon_url=inter.author.avatar.url if inter.author.avatar else inter.author.default_avatar
                    )
                    await inter.response.send_message(embed=emb, ephemeral=True)
        else:
            await inter.response.send_message(f"❌ {channel.name} уже является каналом для воспроизведения потока!", ephemeral=True)
            return

        # === Запись ID канала в базу ===
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.config['SETTINGS']['backend_url']}add_voice_channel_id", json={
                'guild_id': inter.guild.id,
                'channel_id': channel.id,
                'kicked': False
            })

    @commands.has_permissions(administrator=True)
    @commands.slash_command(name='удалить-канал', description='Удалить канал для вещания', default_member_permissions=disnake.Permissions(administrator=True))
    async def delete_voice_channel(self, inter: disnake.ApplicationCommandInteraction):
        # === Получение ID канала ===
        async with httpx.AsyncClient() as client:
            channel_id_response = await client.get(
                f"{self.config['SETTINGS']['backend_url']}get_voice_channel_id?guild_id={inter.guild.id}"
            )

        if channel_id_response.status_code == 200 and channel_id_response.json():
            # --- Удаление ID канала ---
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.config['SETTINGS']['backend_url']}delete_voice_channel_id?guild_id={inter.guild.id}"
                )

            #Если подключен к каналу, то выходим
            if inter.guild.voice_client.is_connected():
                await inter.guild.voice_client.disconnect()

            emb = disnake.Embed(
                description=f"{inter.author.mention}, канал для воспроизведения потока был удалён. Теперь бот не будет играть на вашем сервере!",
                colour=self.embed_color
            )
            emb.set_author(
                name=inter.author.nick if inter.author.nick else inter.author.name,
                icon_url=inter.author.avatar.url if inter.author.avatar else inter.author.default_avatar
            )
            await inter.response.send_message(embed=emb, ephemeral=True)
        else:
            await inter.response.send_message("❌ На данном сервере отсутствует канал для воспроизведения потока!", ephemeral=True)


def setup(bot: commands.AutoShardedInteractionBot):
    bot.add_cog(Settings(bot))