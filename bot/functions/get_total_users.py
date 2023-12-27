def get_current_users(bot): 
    total_members = 0
    for guild in bot.guilds:
        for voice_channel in guild.voice_channels:
            if bot.user in voice_channel.members:
                total_members += len(voice_channel.members)
    return total_members