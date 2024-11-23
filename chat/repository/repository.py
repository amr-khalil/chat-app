from typing import Dict, Optional
import uuid
import threading

from chat.models.customer_data import CustomerData
from chat.models.enums import MessageType, ParticipantType
from chat.models.support_agent_data import SupportAgentData
from chat.models.chat_session_data import ChatSessionData
from chat.models.message_data import MessageData
from chat.models.support_ticket_data import SupportTicketData


class Repository:
    """
    A thread-safe repository class for managing in-memory data storage.

    This class stores customers, agents, chat sessions, messages, and support tickets
    in shared dictionaries. All operations are synchronized using a threading lock
    to ensure thread safety in a concurrent environment.
    """

    _lock = threading.Lock()

    customers: Dict[int, CustomerData] = {}
    agents: Dict[int, SupportAgentData] = {}
    chat_sessions: Dict[uuid.UUID, ChatSessionData] = {}
    messages: Dict[uuid.UUID, MessageData] = {}
    support_tickets: Dict[uuid.UUID, SupportTicketData] = {}

    @classmethod
    def add_customer(cls, customer: CustomerData):
        with cls._lock:
            cls.customers[customer.customer_id] = customer

    @classmethod
    def add_agent(cls, agent: SupportAgentData):
        with cls._lock:
            cls.agents[agent.agent_id] = agent

    @classmethod
    def add_chat_session(cls, session: ChatSessionData):
        with cls._lock:
            cls.chat_sessions[session.session_id] = session

    @classmethod
    def add_message(cls, message: MessageData):
        with cls._lock:
            cls.messages[message.message_id] = message

    @classmethod
    def add_support_ticket(cls, ticket: SupportTicketData):
        with cls._lock:
            cls.support_tickets[ticket.ticket_id] = ticket

    @classmethod
    def get_customer(cls, customer_id: int) -> Optional[CustomerData]:
        with cls._lock:
            return cls.customers.get(customer_id)

    @classmethod
    def get_agent(cls, agent_id: int) -> Optional[SupportAgentData]:
        with cls._lock:
            return cls.agents.get(agent_id)

    @classmethod
    def get_chat_session(cls, session_id: uuid.UUID) -> Optional[ChatSessionData]:
        with cls._lock:
            return cls.chat_sessions.get(session_id)

    @classmethod
    def get_message(cls, message_id: uuid.UUID) -> Optional[MessageData]:
        with cls._lock:
            return cls.messages.get(message_id)

    @classmethod
    def get_support_ticket(cls, ticket_id: uuid.UUID) -> Optional[SupportTicketData]:
        with cls._lock:
            return cls.support_tickets.get(ticket_id)


# Example usage
if __name__ == "__main__":

    # Add customers
    customer1 = CustomerData(1, "Alice", "alice@example.com")
    customer2 = CustomerData(2, "Bob", "bob@example.com")
    Repository.add_customer(customer1)
    Repository.add_customer(customer2)

    # Add agents
    agent1 = SupportAgentData(101, "Charlie", "charlie@support.com")
    Repository.add_agent(agent1)

    # Add chat session
    session1_id = uuid.uuid4()
    session1 = ChatSessionData(session1_id, customer1.customer_id, "Billing Issue")
    Repository.add_chat_session(session1)

    # Add message
    message1_id = uuid.uuid4()
    message1 = MessageData(
        message_id=message1_id,
        session_id=session1_id,
        participant_id=customer1.customer_id,
        participant_type=ParticipantType.CUSTOMER,
        content="I need help with my bill.",
        message_type=MessageType.TEXT,
    )
    Repository.add_message(message1)

    # Add support ticket
    ticket1_id = uuid.uuid4()
    ticket1 = SupportTicketData(
        agent_id=agent1.agent_id, session_id=session1_id, issue="Resolve billing issue"
    )
    Repository.add_support_ticket(ticket1)

    # Retrieve and display data
    retrieved_customer = Repository.get_customer(1)
    retrieved_agent = Repository.get_agent(101)
    retrieved_session = Repository.get_chat_session(session1_id)
    retrieved_message = Repository.get_message(message1_id)
    retrieved_ticket = Repository.get_support_ticket(ticket1_id)

    results = {
        "Customer": retrieved_customer,
        "Agent": retrieved_agent,
        "Chat Session": retrieved_session,
        "Message": retrieved_message,
        "Support Ticket": retrieved_ticket,
    }

    print(results)
