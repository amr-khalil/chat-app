import pytest


from chat.models.enums import TicketStatus
from chat.repository.repository import Repository
from chat.api.chat_facade import ChatFacade
from chat.strategies.profanity_filter_strategy import ProfanityFilterStrategy
from chat.strategies.spam_filter_strategy import SpamFilterStrategy

@pytest.fixture
def setup_repository():
    """Clear the repository before each test."""
    Repository.customers.clear()
    Repository.agents.clear()
    Repository.chat_sessions.clear()
    Repository.messages.clear()
    Repository.support_tickets.clear()


@pytest.fixture
def facade():
    """Provide a ChatFacade instance."""
    return ChatFacade()


@pytest.fixture
def setup_customers_and_agents(facade):
    """Create a few customers and agents for testing."""
    facade.create_customer(1, "John Doe", "john@example.com")
    facade.create_customer(2, "Jane Smith", "jane@example.com")
    facade.create_agent(101, "Agent A", "agent_a@example.com")
    facade.create_agent(102, "Agent B", "agent_b@example.com")


@pytest.mark.asyncio
async def test_full_workflow(facade, setup_repository, setup_customers_and_agents):
    # 1. Customer initiates a chat session
    session_id = await facade.initiate_chat(
        customer_id=1,
        topic="Billing Issue",
        strategies=[SpamFilterStrategy(), ProfanityFilterStrategy()],
    )
    assert session_id in Repository.chat_sessions
    session = Repository.chat_sessions[session_id]
    assert session.customer_id == 1
    assert session.topic == "Billing Issue"

    # 2. Customer sends a message
    await facade.customer_send_message(session_id, 1, "Hello, I need help with my bill.")
    assert len(Repository.messages) == 1
    message = list(Repository.messages.values())[0]
    assert message.content == "Hello, I need help with my bill."

    # 3. Agent assigns themselves to the session
    await facade.agent_handle_session(session_id, 101)
    session = Repository.chat_sessions[session_id]
    assert session.support_agent_id == 101

    # 4. Agent sends a message
    await facade.agent_send_message(session_id, 101, "I am here to assist you.")
    assert len(Repository.messages) == 2
    messages = list(Repository.messages.values())
    assert messages[-1].content == "I am here to assist you."

    # 5. Customer sends a spam message (to trigger the SpamFilterStrategy)
    await facade.customer_send_message(session_id, 1, "Buy now! Limited offer.")
    assert len(Repository.messages) == 3
    spam_message = list(Repository.messages.values())[-1]
    assert spam_message.content == "[Message removed due to spam detection]"

    # 6. Agent creates a support ticket for the issue
    ticket_id = await facade.create_support_ticket(
        agent_id=101, session_id=session_id, issue="Billing discrepancy"
    )
    assert ticket_id in Repository.support_tickets
    ticket = Repository.support_tickets[ticket_id]
    assert ticket.issue == "Billing discrepancy"
    assert ticket.status == TicketStatus.OPEN

    # 7. Agent resolves the ticket
    await facade.resolve_support_ticket(101, ticket_id)
    ticket = Repository.support_tickets[ticket_id]
    assert ticket.status == TicketStatus.RESOLVED


@pytest.mark.asyncio
async def test_multiple_sessions_and_tickets(facade, setup_repository, setup_customers_and_agents):
    # Create two sessions for two customers
    session_id_1 = await facade.initiate_chat(1, "General Inquiry")
    session_id_2 = await facade.initiate_chat(2, "Technical Support")

    # Assign agents to each session
    await facade.agent_handle_session(session_id_1, 101)
    await facade.agent_handle_session(session_id_2, 102)

    # Verify assignments
    assert Repository.chat_sessions[session_id_1].support_agent_id == 101
    assert Repository.chat_sessions[session_id_2].support_agent_id == 102

    # Create tickets for both sessions
    ticket_id_1 = await facade.create_support_ticket(101, session_id_1, "General Inquiry Issue")
    ticket_id_2 = await facade.create_support_ticket(102, session_id_2, "Technical Issue")

    # Resolve tickets
    await facade.resolve_support_ticket(101, ticket_id_1)
    await facade.resolve_support_ticket(102, ticket_id_2)

    # Verify ticket statuses
    assert Repository.support_tickets[ticket_id_1].status == TicketStatus.RESOLVED
    assert Repository.support_tickets[ticket_id_2].status == TicketStatus.RESOLVED
