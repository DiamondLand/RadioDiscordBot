import disnake
from disnake.ext import commands
from disnake import FFmpegPCMAudio

class VoiceManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_color = bot.embed_color
        self.embed_color_error = bot.embed_color_error


    @commands.has_permissions(administrator=True)
    @commands.slash_command(name='присоединить', description='Присоединить бота к голосовому каналу')
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

        # === Воспроизведение музыки ===
        try:
            music_url = self.bot.config["SETTINGS"]["music_url"]
            source = FFmpegPCMAudio(music_url, executable="assets/ffmpeg-6.1/bin/ffmpeg.exe")
            inter.guild.voice_client.play(source)
            await inter.send(f"🎶 Играет музыка")
        except Exception as _ex:
            await inter.send(f"❌ Произошла ошибка при воспроизведении музыки: {_ex}", ephemeral=True)

    @commands.slash_command(name='отключить', description='Отключить бота от голосового канала')
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


def setup(bot):
    bot.add_cog(VoiceManagement(bot))
