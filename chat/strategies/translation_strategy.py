from chat.models.message_data import MessageData
from chat.strategies.message_processing_strategy import MessageProcessingStrategy


class TranslationStrategy(MessageProcessingStrategy):
    def __init__(self, target_language):
        self.target_language = target_language

    def process(self, message: MessageData) -> MessageData:
        message.content = f"[Translated to {self.target_language}]: Lorem ipsum dolor sit amet, consectetur adipisici elit …"
        return message
