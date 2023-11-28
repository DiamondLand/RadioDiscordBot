import disnake
import httpx

from disnake.ext import commands
from functions.play_audio import play_music


class VoiceManagement(commands.Cog):
    def __init__(self, bot: commands.AutoShardedInteractionBot):
        self.bot = bot
        self.config = bot.config
        self.embed_color = bot.embed_color
        self.embed_color_error = bot.embed_color_error


    @commands.has_permissions(administrator=True)
    @commands.slash_command(name='присоединить', description='Присоединить бота к голосовому каналу', default_member_permissions=disnake.Permissions(administrator=True))
    async def join_on_voice_channel(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.VoiceChannel = (commands.Param(default=None, name="канал", description="в какой канал подключить?"))):
        # === Присоединение бота к каналу, указанному в slash команде или в тот, где находится участник ===
        if channel is None:
            if inter.author.voice:
                channel = inter.author.voice.channel
            else:
                await inter.response.send_message("❌ Укажите канал для подключения или же зайдите в него!", ephemeral=True)
                return

        voice_client = inter.guild.voice_client
        if not voice_client:
            await channel.connect()
            emb = disnake.Embed(
                description=f"{inter.author.mention}, бот присоедился к каналу **{channel.name}**.",
                colour=self.embed_color
            )
            emb.set_author(
                name=f"Приятного прослушивания, {inter.author.nick if inter.author.nick else inter.author.name}!",
                icon_url=inter.author.avatar.url if inter.author.avatar else inter.author.default_avatar
            )
            await inter.response.send_message(embed=emb, ephemeral=True)
        else:
            if voice_client.channel.id == channel.id:
                await inter.response.send_message("❌ Бот уже подключен к этому голосовому каналу", ephemeral=True)
                return
            else:
                await voice_client.move_to(channel)
                emb = disnake.Embed(
                    description=f"{inter.author.mention}, бот перемещён в канал **{channel.name}**.",
                    colour=self.embed_color
                )
                emb.set_author(
                    name=f"Приятного прослушивания, {inter.author.nick if inter.author.nick else inter.author.name}!",
                    icon_url=inter.author.avatar.url if inter.author.avatar else inter.author.default_avatar
                )
                await inter.response.send_message(embed=emb, ephemeral=True)

        # --- Запись ID канала в базу---
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.config['SETTINGS']['backend_url']}add_voice_channel_id", json={
                'guild_id': inter.guild.id,
                'channel_id': channel.id
            })

        await play_music(channel=channel)

        
    @commands.has_permissions(administrator=True)
    @commands.slash_command(name='отключить', description='Отключить бота от голосового канала', default_member_permissions = disnake.Permissions(administrator=True))
    async def leave_from_voice_channnel(self, inter: disnake.ApplicationCommandInteraction):
        if inter.guild.voice_client:
            await inter.guild.voice_client.disconnect()
            await inter.response.send_message("✅", ephemeral=True)
        else:
            emb = disnake.Embed(
                description=f"{inter.author.mention}, бот не был присоединён ни к одному каналу!",
                colour=self.embed_color_error
            )
            emb.set_author(
                name=inter.author.nick if inter.author.nick else inter.author.name,
                icon_url=inter.author.avatar.url if inter.author.avatar else inter.author.default_avatar
            )
            await inter.response.send_message(embed=emb, ephemeral=True)

        # --- Удаление ID канала ---
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.config['SETTINGS']['backend_url']}delete_voice_channel_id?guild_id={inter.guild.id}"
            )


def setup(bot: commands.AutoShardedInteractionBot):
    bot.add_cog(VoiceManagement(bot))
