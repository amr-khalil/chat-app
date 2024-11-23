from abc import ABC, abstractmethod
import uuid


class ChatParticipant(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def send_message(self, session_id: uuid.UUID, content: str) -> None:
        pass


