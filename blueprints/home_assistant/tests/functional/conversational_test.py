LATEST_INDEX_IN_CONVERSATION_CONTEXT_HISTORY = 0


def load_conversation():
    import os
    app_path = os.path.dirname(os.path.realpath(__file__)).replace('tests/functional', '')

    from mmworkbench.components import NaturalLanguageProcessor
    nlp = NaturalLanguageProcessor(app_path=app_path)
    nlp.load()

    from mmworkbench import Conversation
    return Conversation(nlp=nlp, app_path=app_path)


class ConversationalTest(object):
    @classmethod
    def setup_class(cls):
        cls.conv = load_conversation()

    @staticmethod
    def assert_text(texts, expected_text):
        assert texts[0] == expected_text

    @staticmethod
    def assert_intent(conv, expected_intent):
        last_history = conv.history[LATEST_INDEX_IN_CONVERSATION_CONTEXT_HISTORY]
        assert last_history['intent'] == expected_intent
