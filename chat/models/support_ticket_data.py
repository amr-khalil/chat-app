from dataclasses import dataclass, field
import uuid

from chat.models.enums import TicketStatus


@dataclass
class SupportTicketData:
    agent_id: int
    session_id: uuid.UUID
    issue: str
    ticket_id: uuid.UUID = field(default_factory=uuid.uuid4)  # Auto-generate UUID
    status: TicketStatus = TicketStatus.OPEN
