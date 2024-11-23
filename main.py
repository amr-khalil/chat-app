# Main Execution
import asyncio

from typing import List

from chat.api.chat_facade import ChatFacade
from chat.strategies.profanity_filter_strategy import ProfanityFilterStrategy
from chat.strategies.spam_filter_strategy import SpamFilterStrategy
from chat.strategies.translation_strategy import TranslationStrategy
from chat.utils.file_attachments import attach_file
from chat.models.message_data import MessageData
from chat.utils.logging import logging


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
        raise e

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
    logging.info("\n\n=== Simulate concurrent sessions ===")
    await simulate_concurrent_sessions(chat_facade)

    # Print chat history
    logging.info("\n\n=== Chat Session Messages ===")
    messages: List[MessageData] = chat_facade.get_chat_history(chat_session_id)
    for message in messages:
        logging.info(
            f"{message.timestamp} - {message.participant_type} ({message.participant_id}): {message.content}"
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