import disnake
import psutil

from datetime import datetime
from functions.get_song_info import get_current_song, get_djname, get_kbps
from functions.get_total_users import get_current_users

class InfoSelectMenuView(disnake.ui.View):
    def __init__(self, bot, embed_color):
        super().__init__(timeout=None)
        self.add_item(InfoSelectMenu(bot, embed_color))


class InfoSelectMenu(disnake.ui.Select):
    def __init__(self, bot, embed_color):
        self.bot = bot
        self.embed_color = embed_color
        options = [
            disnake.SelectOption(
                label="Информация", description="Информация о боте"),
            disnake.SelectOption(
                label="Список команд", description="Получить список команд")
        ]

        super().__init__(
            placeholder="Выберите интересующий раздел",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="information",
        )


    async def callback(self, inter):
        await inter.response.defer(ephemeral=True)
        if self.values[0] == "Список команд":
            emb = disnake.Embed(
                colour=self.embed_color,
                description=f"```Команды:```\
                    \n> **</выбрать-канал:1189533702456344596>** - выбрать канал вещания\
                    \n> **</удалить-канал:1189533702456344597>** - удалить канал вещания\
                    \n> **</старт:1189533702007570506>** - начать проигрывание потока\
                    \n> **</отключить:1189533702007570507>** - отключить бота от голосового канала\
                    \n> **</название:1189533702007570505>** - информация о текущей композиции\
                    \n> **</хелп:1189696680090665041>** - панель информации\
                """)

            emb.set_author(
                name=f"{self.bot.config['INFO']['name']} - лучшее радио на ваш сервер!",
                icon_url=self.bot.user.avatar if self.bot.user.avatar else None
            )
            await inter.edit_original_response(embed=emb, view=InfoSelectMenuView(self.bot, self.embed_color))
        
        if self.values[0] == "Информация":
            emb = disnake.Embed(
                title=f"Информация о боте {self.bot.config['INFO']['name']}:",
                description=f"\n> Дата: **{datetime.now().strftime('%d.%m %H:%M')}**\n> Пинг: **{round(self.bot.latency * 1000)}**\
                \n> Загруженность CPU: **{psutil.cpu_percent()}%**\n> Использовано памяти: **{psutil.virtual_memory().percent}%**\
                \n\
                \n> Серверов: **{len(self.bot.guilds)}**\n> Пользователей: **{len(self.bot.users)}**\
                \n\
                \n> Сейчас играет: **{get_current_song(self.bot.config)}**\n> Диджей: **{get_djname(self.bot.config)}**\n> Слушает: **{get_current_users(self.bot)}**\
                \n\
                \n> Рекомендуем зайти на **[сервер поддержки]({self.bot.config['INFO']['support_server_link']})** для получения дополнительных услуг.\
                \n\
                \n```Владелец: {self.bot.config['INFO']['owner']}\nРазработчик: {self.bot.config['INFO']['developer']}\nВерсия: {self.bot.config['INFO']['version']}```",
                color=self.embed_color
            )
            emb.set_thumbnail(
                url=self.bot.user.avatar if self.bot.user.avatar else None
            )
            await inter.edit_original_response(embed=emb, view=InfoSelectMenuView(self.bot, self.embed_color))
