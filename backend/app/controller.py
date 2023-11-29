from fastapi import APIRouter
from .models import VoiceManagment
from .schemas import AddChannelId, ChangeKickedStatus


controller = APIRouter()
    

# --- Добавление или же обновление ID канала ---
@controller.post('/add_voice_channel_id')
async def add_voice_channel_id(data: AddChannelId):
    await VoiceManagment.update_or_create(
        guild_id=data.guild_id,
        defaults={
            'channel_id': data.channel_id,
            'kicked': data.kicked
        }
    )


# --- Обновление статуса kicked ---
@controller.post('/change_kicked_status')
async def change_kicked_status(data: ChangeKickedStatus):
    existing_entry = await VoiceManagment.get_or_none(guild_id=data.guild_id)
    if existing_entry:
        existing_entry.kicked = data.kicked
        await existing_entry.save()
    

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
    

# --- Получение статуса kicked --- 
@controller.get('/get_kicked_status')
async def get_kicked_status(guild_id: int):
    res = await VoiceManagment.get_or_none(guild_id=guild_id)
    if res is not None:
        return res.kicked
    else:
        return False
