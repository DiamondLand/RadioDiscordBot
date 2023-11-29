import disnake

from disnake import FFmpegPCMAudio
from main import config

async def play_music(channel: disnake.VoiceChannel):
    if channel.guild.voice_client.is_connected():
        try:
            music_source = FFmpegPCMAudio(
                source=config["SETTINGS"]["music_url"],
                executable="bot/assets/ffmpeg-6.1/bin/ffmpeg.exe"
            )
            channel.guild.voice_client.play(music_source)
        except Exception as _ex:
            print(_ex)
    else:
        print("Не подключено")
