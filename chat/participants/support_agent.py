import uuid

from chat.models.enums import ParticipantType
from chat.participants.chat_participant import ChatParticipant
from chat.repository.repository import Repository
from chat.services.chat_service import ChatService
from chat.utils.logging import logging


class SupportAgent(ChatParticipant):
    def __init__(self, agent_id: int):
        agent = Repository.agents.get(agent_id)
        if not agent:
            raise ValueError("Agent does not exist.")
        self.agent_id = agent_id
        self._name = agent.name
        self.email = agent.email

    @property
    def name(self) -> str:
        return self._name

    async def handle_chat_session(self, session_id: uuid.UUID) -> None:
        logging.debug(f"Agent {self.agent_id} handling session {session_id}")
        await ChatService.assign_agent_to_session(session_id, self.agent_id)

    async def send_message(self, session_id: uuid.UUID, content: str) -> None:
        await ChatService.send_message(session_id, self.agent_id, ParticipantType.AGENT, content)

    async def create_support_ticket(
        self, session_id: uuid.UUID, issue: str
    ) -> uuid.UUID:
        return await ChatService.create_support_ticket(self.agent_id, session_id, issue)

    async def resolve_ticket(self, ticket_id: uuid.UUID) -> None:
        await ChatService.resolve_ticket(ticket_id)