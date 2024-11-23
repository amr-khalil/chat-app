from email import message
from typing import List, Optional
import uuid
from chat.models.enums import MessageType, ParticipantType
from chat.participants.chat_participant import ChatParticipant
from chat.repository.repository import Repository
from chat.services.chat_service import ChatService
from chat.strategies.message_processing_strategy import MessageProcessingStrategy


class Customer(ChatParticipant):
    def __init__(self, customer_id: int):
        customer = Repository.customers.get(customer_id)
        if not customer:
            raise ValueError("Customer does not exist.")
        self.customer_id = customer_id
        self._name = customer.name
        self.email = customer.email

    @property
    def name(self) -> str:
        return self._name

    async def initiate_chat_session(
        self, topic: str, strategies: Optional[List[MessageProcessingStrategy]]
    ) -> uuid.UUID:
        return await ChatService.initiate_chat_session(
            customer_id=self.customer_id, topic=topic, strategies=strategies
        )

    async def send_message(self, session_id: uuid.UUID, content: str) -> None:
        return await ChatService.send_message(
            session_id=session_id,
            participant_id=self.customer_id,
            participant_type=ParticipantType.CUSTOMER,
            content=content,
            message_type=MessageType.TEXT,
        )
