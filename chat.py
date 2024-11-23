from __future__ import annotations
from typing import List, Optional, Union, Dict
from datetime import datetime
from abc import ABC, abstractmethod
import uuid
import logging
import asyncio
import os
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)


# Enums
class TicketStatus(Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    REASSIGNED = "Reassigned"


class MessageType(Enum):
    TEXT = "Text"
    IMAGE = "Image"
    FILE = "File"
    SYSTEM = "System"


# Data Models
class CustomerData:
    def __init__(self, customer_id: int, name: str, email: str):
        self.customer_id: int = customer_id
        self.name: str = name
        self.email: str = email


class SupportAgentData:
    def __init__(self, agent_id: int, name: str, email: str):
        self.agent_id: int = agent_id
        self.name: str = name
        self.email: str = email


class ChatSessionData:
    def __init__(self, session_id: uuid.UUID, customer_id: int, topic: str):
        self.session_id: uuid.UUID = session_id
        self.customer_id: int = customer_id
        self.topic: str = topic
        self.support_agent_id: Optional[int] = None
        self.strategies: List[MessageProcessingStrategy] = []


class MessageData:
    def __init__(
        self,
        message_id: uuid.UUID,
        session_id: uuid.UUID,
        sender_id: Union[int, str],
        sender_type: str,
        content: str,
        timestamp: datetime,
        message_type: MessageType,
    ):
        self.message_id: uuid.UUID = message_id
        self.session_id: uuid.UUID = session_id
        self.sender_id: Union[int, str] = sender_id
        self.sender_type: str = sender_type
        self.content: str = content
        self.timestamp: datetime = timestamp
        self.message_type: MessageType = message_type


class SupportTicketData:
    def __init__(
        self,
        ticket_id: uuid.UUID,
        agent_id: int,
        session_id: uuid.UUID,
        issue: str,
        status: TicketStatus,
    ):
        self.ticket_id: uuid.UUID = ticket_id
        self.agent_id: int = agent_id
        self.session_id: uuid.UUID = session_id
        self.issue: str = issue
        self.status: TicketStatus = status


# Repository Layer
class Repository:
    customers: Dict[int, CustomerData] = {}
    agents: Dict[int, SupportAgentData] = {}
    chat_sessions: Dict[uuid.UUID, ChatSessionData] = {}
    messages: Dict[uuid.UUID, MessageData] = {}
    support_tickets: Dict[uuid.UUID, SupportTicketData] = {}

    @classmethod
    def add_customer(cls, customer: CustomerData):
        cls.customers[customer.customer_id] = customer

    @classmethod
    def add_agent(cls, agent: SupportAgentData):
        cls.agents[agent.agent_id] = agent

    @classmethod
    def add_chat_session(cls, session: ChatSessionData):
        cls.chat_sessions[session.session_id] = session

    @classmethod
    def add_message(cls, message: MessageData):
        cls.messages[message.message_id] = message

    @classmethod
    def add_support_ticket(cls, ticket: SupportTicketData):
        cls.support_tickets[ticket.ticket_id] = ticket


# Strategy Pattern for Message Processing
class MessageProcessingStrategy(ABC):
    @abstractmethod
    def process(self, message: MessageData) -> MessageData:
        pass


class SpamFilterStrategy(MessageProcessingStrategy):
    def process(self, message: MessageData) -> MessageData:
        spam_keywords = ["buy now", "free", "click here"]
        if any(keyword in message.content.lower() for keyword in spam_keywords):
            logging.warning(f"Message {message.message_id} detected as spam.")
            message.content = "[Message removed due to spam detection]"
        return message


class ProfanityFilterStrategy(MessageProcessingStrategy):
    def process(self, message: MessageData) -> MessageData:
        profanity_list = ["badword1", "badword2"]
        for badword in profanity_list:
            message.content = message.content.replace(badword, "*" * len(badword))
        return message


class TranslationStrategy(MessageProcessingStrategy):
    def __init__(self, target_language: str):
        self.target_language = target_language

    def process(self, message: MessageData) -> MessageData:
        # Simulate translation
        message.content = f"[Translated to {self.target_language}]: {message.content}"
        return message


# Service Layer
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
        sender_id: Union[int, str],
        sender_type: str,
        content: str,
        message_type: MessageType = MessageType.TEXT,
    ) -> None:
        if session_id not in Repository.chat_sessions:
            logging.error(f"Chat session {session_id} does not exist.")
            raise ValueError("Invalid chat session ID.")

        message_id = uuid.uuid4()
        timestamp = datetime.now()
        message_data = MessageData(
            message_id,
            session_id,
            sender_id,
            sender_type,
            content,
            timestamp,
            message_type,
        )

        # Process the message through the strategies
        session = Repository.chat_sessions[session_id]
        for strategy in session.strategies:
            message_data = strategy.process(message_data)

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
            ticket_id, agent_id, session_id, issue, TicketStatus.OPEN
        )
        Repository.add_support_ticket(ticket_data)
        return ticket_id

    @staticmethod
    async def resolve_ticket(ticket_id: uuid.UUID) -> None:
        if ticket_id not in Repository.support_tickets:
            logging.error(f"Ticket {ticket_id} does not exist.")
            raise ValueError("Invalid ticket ID.")
        Repository.support_tickets[ticket_id].status = TicketStatus.RESOLVED


# Factory Pattern for Chat Participants
class ChatParticipantFactory:
    @staticmethod
    def create_participant(participant_type: str, **kwargs) -> ChatParticipant:
        if participant_type == "Customer":
            return Customer(**kwargs)
        elif participant_type == "Agent":
            return SupportAgent(**kwargs)
        elif participant_type == "Bot":
            return ChatBot(**kwargs)
        else:
            raise ValueError(f"Unknown participant type: {participant_type}")


# Chat Participants
class ChatParticipant(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def send_message(self, session_id: uuid.UUID, content: str) -> None:
        pass


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
        self, topic: str, strategies: Optional[List[MessageProcessingStrategy]] = None
    ) -> uuid.UUID:
        return await ChatService.initiate_chat_session(
            self.customer_id, topic, strategies
        )

    async def send_message(self, session_id: uuid.UUID, content: str) -> None:
        await ChatService.send_message(
            session_id, self.customer_id, "Customer", content
        )


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
        await ChatService.assign_agent_to_session(session_id, self.agent_id)

    async def send_message(self, session_id: uuid.UUID, content: str) -> None:
        await ChatService.send_message(session_id, self.agent_id, "Agent", content)

    async def create_support_ticket(
        self, session_id: uuid.UUID, issue: str
    ) -> uuid.UUID:
        return await ChatService.create_support_ticket(self.agent_id, session_id, issue)

    async def resolve_ticket(self, ticket_id: uuid.UUID) -> None:
        await ChatService.resolve_ticket(ticket_id)


class ChatBot(ChatParticipant):
    def __init__(self, bot_id: str, name: str):
        self.bot_id: str = bot_id
        self._name: str = name

    @property
    def name(self) -> str:
        return self._name

    async def send_message(self, session_id: uuid.UUID, content: str) -> None:
        await ChatService.send_message(session_id, self.bot_id, "Bot", content)


class ChatFacade:
    def __init__(self):
        # Initialize the repository or any other setup if necessary
        pass

    def create_customer(self, customer_id: int, name: str, email: str):
        customer_data = CustomerData(customer_id, name, email)
        Repository.add_customer(customer_data)
        logging.info(f"Customer {name} created with ID {customer_id}.")

    def create_agent(self, agent_id: int, name: str, email: str):
        agent_data = SupportAgentData(agent_id, name, email)
        Repository.add_agent(agent_data)
        logging.info(f"Agent {name} created with ID {agent_id}.")

    async def initiate_chat(
        self,
        customer_id: int,
        topic: str,
        strategies: Optional[List[MessageProcessingStrategy]] = None,
    ) -> uuid.UUID:
        customer = ChatParticipantFactory.create_participant(
            "Customer", customer_id=customer_id
        )
        session_id = await customer.initiate_chat_session(topic, strategies)
        logging.info(
            f"Chat session {session_id} initiated for customer {customer_id} on topic '{topic}'."
        )
        return session_id

    async def customer_send_message(
        self, session_id: uuid.UUID, customer_id: int, content: str
    ):
        customer = ChatParticipantFactory.create_participant(
            "Customer", customer_id=customer_id
        )
        await customer.send_message(session_id, content)
        logging.info(f"Customer {customer_id} sent message in session {session_id}.")

    async def agent_handle_session(self, session_id: uuid.UUID, agent_id: int):
        agent = ChatParticipantFactory.create_participant("Agent", agent_id=agent_id)
        await agent.handle_chat_session(session_id)
        logging.info(f"Agent {agent_id} assigned to session {session_id}.")

    async def agent_send_message(
        self, session_id: uuid.UUID, agent_id: int, content: str
    ):
        agent = ChatParticipantFactory.create_participant("Agent", agent_id=agent_id)
        await agent.send_message(session_id, content)
        logging.info(f"Agent {agent_id} sent message in session {session_id}.")

    async def chatbot_send_message(
        self, session_id: uuid.UUID, bot_id: str, name: str, content: str
    ):
        chatbot = ChatParticipantFactory.create_participant(
            "Bot", bot_id=bot_id, name=name
        )
        await chatbot.send_message(session_id, content)
        logging.info(f"Chatbot {name} sent message in session {session_id}.")

    async def create_support_ticket(
        self, agent_id: int, session_id: uuid.UUID, issue: str
    ) -> uuid.UUID:
        agent = ChatParticipantFactory.create_participant("Agent", agent_id=agent_id)
        ticket_id = await agent.create_support_ticket(session_id, issue)
        logging.info(
            f"Support ticket {ticket_id} created by agent {agent_id} for session {session_id}."
        )
        return ticket_id

    async def resolve_support_ticket(self, agent_id: int, ticket_id: uuid.UUID):
        agent = ChatParticipantFactory.create_participant("Agent", agent_id=agent_id)
        await agent.resolve_ticket(ticket_id)
        logging.info(f"Support ticket {ticket_id} resolved by agent {agent_id}.")

    def get_chat_history(self, session_id: uuid.UUID) -> List:
        messages = [
            message
            for message in Repository.messages.values()
            if message.session_id == session_id
        ]
        messages.sort(key=lambda x: x.timestamp)
        return messages

    def list_customers(self):
        return list(Repository.customers.values())

    def list_agents(self):
        return list(Repository.agents.values())

    def get_customer(self, customer_id: int):
        return Repository.customers.get(customer_id)

    def get_agent(self, agent_id: int):
        return Repository.agents.get(agent_id)


# Utility Functions
async def attach_file(session_id: uuid.UUID, file_name: str, file_path: str) -> None:
    if not os.path.exists(file_path):
        logging.error(f"File {file_path} does not exist.")
        raise FileNotFoundError(f"File {file_path} does not exist.")
    await ChatService.send_message(
        session_id,
        "System",
        "System",
        f"File attached: {file_name}",
        MessageType.FILE,
    )


# Main Execution
async def main() -> None:
    # Initialize the facade
    chat_facade = ChatFacade()

    # Create repository data using the facade
    chat_facade.create_customer(1, "John Doe", "john.doe@example.com")
    chat_facade.create_agent(101, "Jane Smith", "jane.smith@support.com")

    # Set up strategies
    strategies = [
        SpamFilterStrategy(),
        ProfanityFilterStrategy(),
        # TranslationStrategy(target_language='Spanish'),  # Uncomment to enable translation
    ]

    # Customer initiates a chat session
    chat_session_id = await chat_facade.initiate_chat(1, "Payment Issue", strategies)
    logging.info(f"Chat session initiated: {chat_session_id}, Topic: 'Payment Issue'")

    # Customer sends a message
    try:
        await chat_facade.customer_send_message(
            chat_session_id, 1, "I am unable to process my payment."
        )
        logging.info("Customer sent a message.")
    except Exception as e:
        logging.error(f"Error sending message: {e}")

    # Agent handles the chat session
    try:
        await chat_facade.agent_handle_session(chat_session_id, 101)
        logging.info(f"Agent with ID 101 is handling the chat session.")
    except Exception as e:
        logging.error(f"Error assigning agent: {e}")

    # Agent responds to the customer
    try:
        await chat_facade.agent_send_message(
            chat_session_id,
            101,
            "I'm sorry to hear that. Could you provide more details?",
        )
        logging.info("Agent responded to the customer.")
    except Exception as e:
        logging.error(f"Error sending message: {e}")

    # Customer attaches a file
    file_name = "payment_error.png"
    file_path = "/path/to/payment_error.png"
    try:
        await attach_file(chat_session_id, file_name, file_path)
        logging.info("Customer attached a file.")
    except Exception as e:
        logging.error(f"Error attaching file: {e}")

    # Chatbot interaction
    try:
        await chat_facade.chatbot_send_message(
            chat_session_id,
            "Bot-501",
            "HelpBot",
            "Have you tried clearing your browser cache?",
        )
        logging.info("Chatbot sent a message.")
    except Exception as e:
        logging.error(f"Error sending chatbot message: {e}")

    # Customer replies
    try:
        await chat_facade.customer_send_message(
            chat_session_id, 1, "Yes, I tried that but it didn't help."
        )
        logging.info("Customer replied to the chatbot.")
    except Exception as e:
        logging.error(f"Error sending message: {e}")

    # Agent creates a support ticket
    try:
        ticket_id = await chat_facade.create_support_ticket(
            101, chat_session_id, "Customer unable to process payment"
        )
        logging.info(f"Support ticket created: {ticket_id}")
    except Exception as e:
        logging.error(f"Error creating support ticket: {e}")

    # Agent resolves the ticket
    try:
        await chat_facade.resolve_support_ticket(101, ticket_id)
        logging.info(f"Support ticket {ticket_id} resolved.")
    except Exception as e:
        logging.error(f"Error resolving ticket: {e}")

    # Simulate concurrent sessions
    await simulate_concurrent_sessions(chat_facade)

    # Print chat history
    logging.info("\n=== Chat Session Messages ===")
    messages = chat_facade.get_chat_history(chat_session_id)
    for message in messages:
        logging.info(
            f"{message.timestamp} - {message.sender_type} ({message.sender_id}): {message.content}"
        )


# Simulate concurrent sessions
async def simulate_concurrent_sessions(chat_facade):
    async def customer_interaction(customer_id: int, topic: str):
        try:
            strategies = [
                SpamFilterStrategy(),
                ProfanityFilterStrategy(),
                TranslationStrategy(target_language="French"),
            ]
            session_id = await chat_facade.initiate_chat(customer_id, topic, strategies)
            customer = chat_facade.get_customer(customer_id)
            logging.info(
                f"[{customer.name}] initiated chat session {session_id} on topic '{topic}'"
            )
            await chat_facade.customer_send_message(
                session_id, customer_id, "I have a question regarding my account."
            )
            logging.info(f"[{customer.name}] sent a message.")

            # Assign first available agent
            agents = chat_facade.list_agents()
            if not agents:
                logging.error("No agents available.")
                return
            agent = agents[0]
            await chat_facade.agent_handle_session(session_id, agent.agent_id)
            logging.info(f"[{agent.name}] is handling the chat session.")

            await chat_facade.agent_send_message(
                session_id, agent.agent_id, "How can I assist you with your account?"
            )
            logging.info(f"[{agent.name}] responded to the customer.")
        except Exception as e:
            logging.error(f"Error in customer interaction: {e}")

    # Add more customers using the facade
    chat_facade.create_customer(2, "Alice", "alice@example.com")
    chat_facade.create_customer(3, "Bob", "bob@example.com")

    await asyncio.gather(
        customer_interaction(2, "Account Inquiry"),
        customer_interaction(3, "Technical Support"),
    )


if __name__ == "__main__":
    asyncio.run(main())
