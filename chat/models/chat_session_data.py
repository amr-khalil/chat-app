from dataclasses import dataclass, field
from typing import Optional, List
import uuid

from chat.strategies.message_processing_strategy import MessageProcessingStrategy



@dataclass
class ChatSessionData:
    session_id: uuid.UUID
    customer_id: int
    topic: str
    support_agent_id: Optional[int] = None
    strategies: List[MessageProcessingStrategy] = field(default_factory=list)
