import pydantic


class AddChannelId(pydantic.BaseModel):
    guild_id: int
    channel_id: int
    kicked: bool


class ChangeKickedStatus(pydantic.BaseModel):
    guild_id: int
    kicked: bool