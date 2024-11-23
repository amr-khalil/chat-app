import uuid
from chat.models.enums import ParticipantType
from chat.participants.chat_participant import ChatParticipant
from chat.services.chat_service import ChatService


class ChatBot(ChatParticipant):
    def __init__(self, bot_id: str, name: str):
        self.bot_id: str = bot_id
        self._name: str = name

    @property
    def name(self) -> str:
        return self._name

    async def send_message(self, session_id: uuid.UUID, content: str) -> None:
        await ChatService.send_message(session_id=session_id,
                                       participant_id=self.bot_id,
                                       participant_type=ParticipantType.BOT,
                                       content=content)