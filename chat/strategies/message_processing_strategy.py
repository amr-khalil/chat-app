from abc import ABC, abstractmethod

from chat.models.message_data import MessageData


class MessageProcessingStrategy(ABC):
    @abstractmethod
    def process(self, message: MessageData) -> MessageData:
        pass
