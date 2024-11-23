from typing import List, Optional
import uuid

from chat.models.customer_data import CustomerData
from chat.models.enums import ParticipantType
from chat.models.support_agent_data import SupportAgentData
from chat.participants.chat_participant_factory import ChatParticipantFactory
from chat.repository.repository import Repository
from chat.strategies.message_processing_strategy import MessageProcessingStrategy
from chat.utils.logging import logging


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
            participant_type=ParticipantType.CUSTOMER, customer_id=customer_id
        )
        session_id = await customer.initiate_chat_session(topic, strategies) # type: ignore
        logging.info(
            f"Chat session {session_id} initiated for customer {customer_id} on topic '{topic}'."
        )
        return session_id

    async def customer_send_message(
        self, session_id: uuid.UUID, customer_id: int, content: str
    ):
        customer = ChatParticipantFactory.create_participant(
            participant_type=ParticipantType.CUSTOMER, customer_id=customer_id
        )
        await customer.send_message(session_id, content)
        logging.info(f"Customer {customer_id} sent message in session {session_id}.")

    async def agent_handle_session(self, session_id: uuid.UUID, agent_id: int):
        agent = ChatParticipantFactory.create_participant(
            participant_type=ParticipantType.AGENT, agent_id=agent_id
        )
        await agent.handle_chat_session(session_id) # type: ignore
        logging.info(f"Agent {agent_id} assigned to session {session_id}.")

    async def agent_send_message(
        self, session_id: uuid.UUID, agent_id: int, content: str
    ):
        agent = ChatParticipantFactory.create_participant(
            participant_type=ParticipantType.AGENT, agent_id=agent_id
        )
        await agent.send_message(session_id, content)
        logging.info(f"Agent {agent_id} sent message in session {session_id}.")

    async def chatbot_send_message(
        self, session_id: uuid.UUID, bot_id: str, name: str, content: str
    ):
        chatbot = ChatParticipantFactory.create_participant(
            participant_type=ParticipantType.BOT, bot_id=bot_id, name=name
        )
        await chatbot.send_message(session_id, content)
        logging.info(f"Chatbot {name} sent message in session {session_id}.")

    async def create_support_ticket(
        self, agent_id: int, session_id: uuid.UUID, issue: str
    ) -> uuid.UUID:
        agent = ChatParticipantFactory.create_participant(
            participant_type=ParticipantType.AGENT, agent_id=agent_id
        )
        ticket_id = await agent.create_support_ticket(session_id, issue) # type: ignore
        logging.info(
            f"Support ticket {ticket_id} created by agent {agent_id} for session {session_id}."
        )
        return ticket_id

    async def resolve_support_ticket(self, agent_id: int, ticket_id: uuid.UUID):
        agent = ChatParticipantFactory.create_participant(
            participant_type=ParticipantType.AGENT, agent_id=agent_id
        )
        await agent.resolve_ticket(ticket_id) # type: ignore
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
    
    def list_sessions(self):
        return list(Repository.chat_sessions.values())
