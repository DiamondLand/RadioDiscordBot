from fastapi import APIRouter, HTTPException
from .models import VoiceManagment
from .schemas import AddChannelId


controller = APIRouter()
    

# --- Добавление или же обновление ID канала ---
@controller.post('/add_voice_channel_id')
async def add_voice_channel_id(data: AddChannelId):
    await VoiceManagment.update_or_create(
        guild_id=data.guild_id,
        defaults={
            'channel_id': data.channel_id
        }
    )
    

# --- Удаление ID канала ---
@controller.post('/delete_voice_channel_id')
async def delete_voice_channel_id(guild_id: int):
    record = await VoiceManagment.get_or_none(guild_id=guild_id)
    if record:
        await record.delete()


# --- Получение ID канала --- 
@controller.get('/get_voice_channel_id')
async def get_voice_channel_id(guild_id: int):
    res = await VoiceManagment.get_or_none(guild_id=guild_id)
    if res and res.channel_id:
        return res.channel_id
    else:
        return None