def get_current_users(bot): 
    # --- Используем множество для хранения уникальных пользователей ---
    total_users = set() 
    for guild in bot.guilds:
        if guild.voice_channels:
            for channel in guild.voice_channels:
                # --- Проверяем, есть ли кто-то в голосовом канале ---
                if channel.members:
                    total_users.update(member for member in channel.members if not member.bot)
    return total_users