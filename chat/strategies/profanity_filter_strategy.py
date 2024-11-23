from chat.models.message_data import MessageData
from chat.strategies.message_processing_strategy import MessageProcessingStrategy
from chat.utils.logging import logging

class ProfanityFilterStrategy(MessageProcessingStrategy):
    def process(self, message: MessageData) -> MessageData:
        profanity_list = ["badword1", "badword2"]
        contains_profanity = False

        for badword in profanity_list:
            if badword in message.content:
                contains_profanity = True
                message.content = message.content.replace(badword, "*" * len(badword))

        if contains_profanity:
            logging.warning(
                f"Message {message.message_id} includes badwords: {message.content}"
            )
        return message
