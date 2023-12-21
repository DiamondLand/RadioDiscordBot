import disnake

from disnake import FFmpegPCMAudio
from main import config

def play_music(channel: disnake.VoiceChannel):
    voice_client = channel.guild.voice_client
    if voice_client and voice_client.is_connected():
        music_source = FFmpegPCMAudio(
            source=config["SETTINGS"]["music_url"],
            executable="bot/assets/ffmpeg-6.1/bin/ffmpeg.exe"
        )
        voice_client.play(music_source)
