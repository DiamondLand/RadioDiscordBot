import disnake

from disnake import FFmpegPCMAudio
from main import config

async def play_music(channel: disnake.VoiceChannel):
    if channel.guild.voice_client is not None:
        try:
            music_url = config["SETTINGS"]["music_url"]
            source = FFmpegPCMAudio(music_url, executable="assets/ffmpeg-6.1/bin/ffmpeg.exe")
            channel.guild.voice_client.play(source)
        except Exception as _ex:
            print(_ex)
