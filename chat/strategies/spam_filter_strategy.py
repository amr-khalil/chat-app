from chat.models.message_data import MessageData
from chat.strategies.message_processing_strategy import MessageProcessingStrategy
from chat.utils.logging import logging

class SpamFilterStrategy(MessageProcessingStrategy):
    def process(self, message: MessageData) -> MessageData:
        spam_keywords = ["buy now", "free", "click here"]
        if any(keyword in message.content.lower() for keyword in spam_keywords):
            logging.warning(f"Message {message.message_id} detected as spam.")
            message.content = "[Message removed due to spam detection]"
        return message
