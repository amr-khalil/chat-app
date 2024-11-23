from chat.models.enums import ParticipantType
from chat.participants.customer import Customer
from chat.participants.support_agent import SupportAgent
from chat.participants.chatbot import ChatBot


class ChatParticipantFactory:
    @staticmethod
    def create_participant(participant_type: ParticipantType, **kwargs):
        if participant_type == ParticipantType.CUSTOMER:
            return Customer(**kwargs)
        elif participant_type ==  ParticipantType.AGENT:
            return SupportAgent(**kwargs)
        elif participant_type ==  ParticipantType.BOT:
            return ChatBot(**kwargs)
        else:
            raise ValueError(f"Unknown participant type: {participant_type}")
