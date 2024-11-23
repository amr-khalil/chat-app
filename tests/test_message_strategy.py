import uuid
from datetime import datetime

from chat.models.enums import MessageType, ParticipantType
from chat.models.message_data import MessageData
from chat.strategies.profanity_filter_strategy import ProfanityFilterStrategy
from chat.strategies.spam_filter_strategy import SpamFilterStrategy
from chat.strategies.translation_strategy import TranslationStrategy


def test_spam_filter_strategy():
    message = MessageData(
        uuid.uuid4(),
        uuid.uuid4(),
        1,
        ParticipantType.CUSTOMER,
        "Click here to buy now!",
        datetime.now(),
        MessageType.TEXT,
    )
    strategy = SpamFilterStrategy()
    processed_message = strategy.process(message)
    assert processed_message.content == "[Message removed due to spam detection]"


def test_profanity_filter_strategy():
    message = MessageData(
        uuid.uuid4(),
        uuid.uuid4(),
        1,
        ParticipantType.CUSTOMER,
        "This contains badword1 and badword2.",
        datetime.now(),
        MessageType.TEXT,
    )
    strategy = ProfanityFilterStrategy()
    processed_message = strategy.process(message)
    assert processed_message.content == "This contains ******** and ********."


def test_translation_strategy():
    message = MessageData(
        uuid.uuid4(),
        uuid.uuid4(),
        1,
        ParticipantType.CUSTOMER,
        "Hello, how are you?",
        datetime.now(),
        MessageType.TEXT,
    )
    strategy = TranslationStrategy(target_language="Latin")
    processed_message = strategy.process(message)
    assert processed_message.content == "[Translated to Latin]: Quid agis?"
