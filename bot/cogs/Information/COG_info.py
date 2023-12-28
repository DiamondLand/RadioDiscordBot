import disnake

from .info_view import InfoSelectMenuView
from disnake.ext import commands
from functions.get_song_info import get_current_song, get_kbps, get_djname


class Information(commands.Cog):
    def __init__(self, bot: commands.AutoShardedInteractionBot):
        self.bot = bot
        self.config = bot.config
        self.embed_color = bot.embed_color
        self.embed_color_error = bot.embed_color_error


    @commands.slash_command(name='название', description='Информация о текущей композиции')
    async def current_song(self, inter: disnake.ApplicationCommandInteraction):
        emb = disnake.Embed(
            description=f"> Сейчас играет: **{get_current_song(self.config)}**\
            \n> Диджей: **{get_djname(self.config)}**",
            colour=self.embed_color
        )
        emb.set_author(
            name=inter.author.nick if inter.author.nick else inter.author.name,
            icon_url=inter.author.avatar.url if inter.author.avatar.url else inter.author.default_avatar
        )
        emb.set_footer(
            text=f"Качество аудиофайла — {get_kbps(self.config)} kbps"
        )
        await inter.response.send_message(embed=emb, ephemeral=True)

    
    @commands.slash_command(name='хелп', description='Меню помощи')
    async def information(self, inter: disnake.ApplicationCommandInteraction):
        emb = disnake.Embed(
            title=f"Меню помощи {self.config['INFO']['name']}:",
            description=f"> В данном меню вы можете ознакомиться с базовой информацией, которая пригодится во время эксплуатации бота, однако рекомендуем зайти на **[сервер поддержки]({self.config['INFO']['support_server_link']})** для получения дополнительных услуг 😉",
            color=self.embed_color
        )
        emb.set_thumbnail(
            url=self.bot.user.avatar if self.bot.user.avatar else None
        )
        await inter.response.send_message(embed=emb, view=InfoSelectMenuView(self.bot, self.embed_color), ephemeral=True)


def setup(bot: commands.AutoShardedInteractionBot):
    bot.add_cog(Information(bot))
