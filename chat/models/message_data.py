from dataclasses import dataclass, field
from typing import Union
from datetime import datetime
import uuid

from chat.models.enums import MessageType, ParticipantType


@dataclass
class MessageData:
    message_id: uuid.UUID = field(default_factory=uuid.uuid4)  # Auto-generate UUID
    session_id: uuid.UUID = field(default_factory=uuid.uuid4)  # Auto-generate UUID
    participant_id: Union[int, str] = "System"  # Default sender ID
    participant_type: ParticipantType = ParticipantType.BOT
    content: str = "No Content"
    timestamp: datetime = field(default_factory=datetime.now)
    message_type: MessageType = MessageType.TEXT
