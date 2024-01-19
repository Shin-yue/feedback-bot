"""This module contains several constants that are relevant for the Bot."""
from enum import Enum
from telegram._utils.enum import StringEnum

__all__ = [
    "MessageType"
    "UserState",
]  

class UserState(Enum):
    COMMENTING = 0
    IDLE = 1


class MessageType(StringEnum):
    """This enum contains the available types of :class:`telegram.Message` that can be seen. The enum
    members of this enumeration are instances of :class:`str` and can be treated as such.
    """    
    ANIMATION = "animation"
    AUDIO = "audio"
    DOCUMENT = "document"
    PHOTO = "photo"
    STICKER = "sticker"
    VIDEO = "video"
    VIDEO_NOTE = "video_note"
    VOICE = "voice"
    TEXT = "text"
