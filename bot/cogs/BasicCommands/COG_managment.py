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
    @commands.slash_command(name='старт', description='Начать проигрывание потока', default_member_permissions=disnake.Permissions(administrator=True))
    async def join_on_voice_channel(self, inter: disnake.ApplicationCommandInteraction):
        # === Проверка на наличие канала в базе данных ===
        async with httpx.AsyncClient() as client:
            channel_id_response = await client.get(
                f"{self.config['SETTINGS']['backend_url']}get_voice_channel_id?guild_id={inter.guild.id}"
            )
        
        if channel_id_response.status_code == 200 and channel_id_response.json():
            # === Пытаемся найти канал, указанный в настройках ===
            try:
                channel = self.bot.get_channel(channel_id_response.json())
            except Exception:
                await inter.response.send_message("❌ Указанный в настройках бота канал не был обнаружен!", ephemeral=True)
                return

            voice_client = inter.guild.voice_client
            if not voice_client:
                # === Если не подключён к каналу ===
                try:
                    await channel.connect()
                except Exception: 
                    await inter.response.send_message("❌ Не получилось подключиться к каналу, указанному в настройках бота!", ephemeral=True)
                    return

                # === Изменение статуса kicked ===
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{self.config['SETTINGS']['backend_url']}change_kicked_status", json={
                        'guild_id': inter.guild.id,
                        'kicked': False
                    })
                await inter.response.send_message("✅", ephemeral=True)
            else:
                await inter.response.send_message(f"Бот уже играет в канале! Приятного прослушивания 🐼", ephemeral=True)
        else:
            await inter.response.send_message("❌ Сперва укажите канал для проигрывания потока по команде управления!", ephemeral=True)

        
    @commands.has_permissions(administrator=True)
    @commands.slash_command(name='отключить', description='Отключить бота от голосового канала', default_member_permissions = disnake.Permissions(administrator=True))
    async def leave_from_voice_channnel(self, inter: disnake.ApplicationCommandInteraction):
        if inter.guild.voice_client.is_connected():
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
        
        # === Изменение статуса kicked ===
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.config['SETTINGS']['backend_url']}change_kicked_status", json={
                'guild_id': inter.guild.id,
                'kicked': True
            })


def setup(bot: commands.AutoShardedInteractionBot):
    bot.add_cog(VoiceManagement(bot))
