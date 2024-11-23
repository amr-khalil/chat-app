import uuid

from chat.models.enums import MessageType, ParticipantType
from chat.services.chat_service import ChatService

async def attach_file(session_id: uuid.UUID, file_name: str, file_path: str) -> None:
    await ChatService.send_message(
        session_id,
        "System",
        ParticipantType.SYSTEM,
        f"File attached: {file_name}",
        MessageType.FILE,
    )
