from enum import Enum


class ParticipantType(Enum):
    CUSTOMER = "Customer"
    AGENT = "Agent"
    BOT = "Bot"
    SYSTEM = "System"


class MessageType(Enum):
    TEXT = "Text"
    IMAGE = "Image"
    FILE = "File"
    SYSTEM = "System"

class TicketStatus(Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    REASSIGNED = "Reassigned"
