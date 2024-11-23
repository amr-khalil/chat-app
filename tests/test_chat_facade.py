import pytest

from chat.models.enums import TicketStatus
from chat.repository.repository import Repository
from chat.api.chat_facade import ChatFacade


@pytest.fixture
def setup_repository():
    """Clear the repository before each test."""
    Repository.customers.clear()
    Repository.agents.clear()
    Repository.chat_sessions.clear()
    Repository.messages.clear()
    Repository.support_tickets.clear()


@pytest.mark.asyncio
async def test_initiate_chat(setup_repository):
    facade = ChatFacade()
    facade.create_customer(1, "John Doe", "john@example.com")

    session_id = await facade.initiate_chat(1, "Support Request")
    assert session_id in Repository.chat_sessions

    session = Repository.chat_sessions[session_id]
    assert session.customer_id == 1
    assert session.topic == "Support Request"


@pytest.mark.asyncio
async def test_send_message(setup_repository):
    facade = ChatFacade()
    facade.create_customer(1, "John Doe", "john@example.com")
    session_id = await facade.initiate_chat(1, "Support Request")

    await facade.customer_send_message(session_id, 1, "Test message")
    messages = Repository.messages.values()
    assert len(messages) == 1
    message = list(messages)[0]
    assert message.content == "Test message"


@pytest.mark.asyncio
async def test_assign_agent_to_chat(setup_repository):
    facade = ChatFacade()
    facade.create_customer(1, "John Doe", "john@example.com")
    facade.create_agent(101, "Jane Smith", "jane@example.com")

    session_id = await facade.initiate_chat(1, "Support Request")
    await facade.agent_handle_session(session_id, 101)

    session = Repository.chat_sessions[session_id]
    assert session.support_agent_id == 101


@pytest.mark.asyncio
async def test_create_and_resolve_ticket(setup_repository):
    facade = ChatFacade()
    facade.create_customer(1, "John Doe", "john@example.com")
    facade.create_agent(101, "Jane Smith", "jane@example.com")

    session_id = await facade.initiate_chat(1, "Support Request")
    await facade.agent_handle_session(session_id, 101)

    ticket_id = await facade.create_support_ticket(101, session_id, "Issue description")
    assert ticket_id in Repository.support_tickets

    ticket = Repository.support_tickets[ticket_id]
    assert ticket.status == TicketStatus.OPEN

    await facade.resolve_support_ticket(101, ticket_id)
    assert Repository.support_tickets[ticket_id].status == TicketStatus.RESOLVED
