import pydantic


class AddChannelId(pydantic.BaseModel):
    guild_id: int
    channel_id: int