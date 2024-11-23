from typing import List, Optional, Union
import uuid

from requests import session

from chat.models.support_ticket_data import SupportTicketData
from chat.models.enums import ParticipantType, TicketStatus
from chat.models.enums import MessageType
from chat.models.message_data import MessageData
from chat.repository.repository import Repository
from chat.models.chat_session_data import ChatSessionData
from chat.strategies.message_processing_strategy import MessageProcessingStrategy
from chat.utils.logging import logging


class ChatService:
    @staticmethod
    async def initiate_chat_session(
        customer_id: int,
        topic: str,
        strategies: Optional[List[MessageProcessingStrategy]] = None,
    ) -> uuid.UUID:
        session_id = uuid.uuid4()
        session_data = ChatSessionData(session_id, customer_id, topic)
        if strategies is not None:
            session_data.strategies = strategies
        else:
            session_data.strategies = []
        Repository.add_chat_session(session_data)
        return session_id

    @staticmethod
    async def send_message(
        session_id: uuid.UUID,
        participant_id: Union[int, str],
        participant_type: ParticipantType,
        content: str,
        message_type: MessageType = MessageType.TEXT,
    ) -> None:
        if session_id not in Repository.chat_sessions:
            logging.error(f"Chat session {session_id} does not exist.")
            raise ValueError("Invalid chat session ID.")

        message_data = MessageData(
            session_id=session_id,
            participant_id=participant_id,
            participant_type=participant_type,
            content=content,
            message_type=message_type,
        )

        # Process the message through the strategies
        session = Repository.chat_sessions[session_id]
        for strategy in session.strategies:
            message_data = strategy.process(message_data)
        
        logging.info(f"[{message_data.participant_type.value} {participant_id}]: {message_data.content}")

        Repository.add_message(message_data)

    @staticmethod
    async def assign_agent_to_session(session_id: uuid.UUID, agent_id: int) -> None:
        if session_id not in Repository.chat_sessions:
            logging.error(f"Chat session {session_id} does not exist.")
            raise ValueError("Invalid chat session ID.")
        if agent_id not in Repository.agents:
            logging.error(f"Agent {agent_id} does not exist.")
            raise ValueError("Invalid agent ID.")
        Repository.chat_sessions[session_id].support_agent_id = agent_id

    @staticmethod
    async def create_support_ticket(
        agent_id: int, session_id: uuid.UUID, issue: str
    ) -> uuid.UUID:
        ticket_id = uuid.uuid4()
        ticket_data = SupportTicketData(
            agent_id=agent_id,
            session_id=session_id,
            issue=issue,
            ticket_id=ticket_id,
            status=TicketStatus.OPEN,
        )
        Repository.add_support_ticket(ticket_data)
        return ticket_id

    @staticmethod
    async def resolve_ticket(ticket_id: uuid.UUID) -> None:
        if ticket_id not in Repository.support_tickets:
            logging.error(f"Ticket {ticket_id} does not exist.")
            raise ValueError("Invalid ticket ID.")
        Repository.support_tickets[ticket_id].status = TicketStatus.RESOLVED
