import pytest
import uuid

from chat.models.chat_session_data import ChatSessionData
from chat.models.enums import MessageType, ParticipantType, TicketStatus
from chat.models.support_agent_data import SupportAgentData
from chat.models.support_ticket_data import SupportTicketData
from chat.repository.repository import Repository
from chat.services.chat_service import ChatService



@pytest.fixture
def setup_repository():
    """Clear the repository before each test."""
    Repository.customers.clear()
    Repository.agents.clear()
    Repository.chat_sessions.clear()
    Repository.messages.clear()
    Repository.support_tickets.clear()


@pytest.mark.asyncio
async def test_initiate_chat_session(setup_repository):
    session_id = await ChatService.initiate_chat_session(1, "Support Request")
    assert session_id in Repository.chat_sessions

    session = Repository.chat_sessions[session_id]
    assert session.customer_id == 1
    assert session.topic == "Support Request"


@pytest.mark.asyncio
async def test_send_message(setup_repository):
    session_id = uuid.uuid4()
    session = ChatSessionData(session_id, 1, "Support")
    Repository.add_chat_session(session)

    await ChatService.send_message(
        session_id, 1, ParticipantType.CUSTOMER, "Test Message", MessageType.TEXT
    )

    messages = list(Repository.messages.values())
    assert len(messages) == 1
    message = messages[0]
    assert message.content == "Test Message"
    assert message.participant_id == 1


@pytest.mark.asyncio
async def test_assign_agent_to_session(setup_repository):
    session_id = uuid.uuid4()
    session = ChatSessionData(session_id, 1, "Support")
    Repository.add_chat_session(session)

    agent_id = 101
    agent = SupportAgentData(agent_id, "Agent", "agent@example.com")
    Repository.add_agent(agent)

    await ChatService.assign_agent_to_session(session_id, agent_id)

    assigned_session = Repository.chat_sessions[session_id]
    assert assigned_session.support_agent_id == agent_id


@pytest.mark.asyncio
async def test_create_support_ticket(setup_repository):
    session_id = uuid.uuid4()
    session = ChatSessionData(session_id, 1, "Support")
    Repository.add_chat_session(session)

    agent_id = 101
    agent = SupportAgentData(agent_id, "Agent", "agent@example.com")
    Repository.add_agent(agent)

    ticket_id = await ChatService.create_support_ticket(agent_id, session_id, "Issue")
    assert ticket_id in Repository.support_tickets

    ticket = Repository.support_tickets[ticket_id]
    assert ticket.agent_id == agent_id
    assert ticket.session_id == session_id
    assert ticket.issue == "Issue"
    assert ticket.status == TicketStatus.OPEN


@pytest.mark.asyncio
async def test_resolve_ticket(setup_repository):
    ticket_id = uuid.uuid4()
    session_id = uuid.uuid4()
    ticket = SupportTicketData(101, session_id, "Issue", ticket_id, TicketStatus.OPEN)
    Repository.add_support_ticket(ticket)

    await ChatService.resolve_ticket(ticket_id)

    resolved_ticket = Repository.support_tickets[ticket_id]
    assert resolved_ticket.status == TicketStatus.RESOLVED