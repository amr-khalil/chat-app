import pytest
import uuid
from datetime import datetime

from chat.models.chat_session_data import ChatSessionData
from chat.models.customer_data import CustomerData
from chat.models.enums import MessageType, ParticipantType, TicketStatus
from chat.models.message_data import MessageData
from chat.models.support_agent_data import SupportAgentData
from chat.models.support_ticket_data import SupportTicketData
from chat.repository.repository import Repository


@pytest.fixture
def setup_repository():
    """Clear the repository before each test."""
    Repository.customers.clear()
    Repository.agents.clear()
    Repository.chat_sessions.clear()
    Repository.messages.clear()
    Repository.support_tickets.clear()


def test_add_and_get_customer(setup_repository):
    customer = CustomerData(1, "John Doe", "john@example.com")
    Repository.add_customer(customer)
    assert Repository.customers[1].name == "John Doe"
    assert Repository.customers[1].email == "john@example.com"


def test_add_and_get_agent(setup_repository):
    agent = SupportAgentData(101, "Jane Smith", "jane@example.com")
    Repository.add_agent(agent)
    assert Repository.agents[101].name == "Jane Smith"
    assert Repository.agents[101].email == "jane@example.com"


def test_add_and_get_chat_session(setup_repository):
    session_id = uuid.uuid4()
    session = ChatSessionData(session_id, 1, "Support Request")
    Repository.add_chat_session(session)
    assert Repository.chat_sessions[session_id].topic == "Support Request"
    assert Repository.chat_sessions[session_id].customer_id == 1


def test_add_and_get_message(setup_repository):
    message_id = uuid.uuid4()
    session_id = uuid.uuid4()
    message = MessageData(
        message_id,
        session_id,
        1,
        ParticipantType.CUSTOMER,
        "Test Message",
        datetime.now(),
        MessageType.TEXT,
    )
    Repository.add_message(message)
    assert Repository.messages[message_id].content == "Test Message"
    assert Repository.messages[message_id].participant_id == 1


def test_add_and_get_support_ticket(setup_repository):
    ticket_id = uuid.uuid4()
    session_id = uuid.uuid4()
    ticket = SupportTicketData(
        101, session_id, "Issue description", ticket_id, TicketStatus.OPEN
    )
    Repository.add_support_ticket(ticket)
    assert Repository.support_tickets[ticket_id].issue == "Issue description"
    assert Repository.support_tickets[ticket_id].status == TicketStatus.OPEN
