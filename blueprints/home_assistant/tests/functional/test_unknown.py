import pytest
from conversational_test import ConversationalTest


@pytest.fixture()
def app_path():
    import os
    return os.path.dirname(os.path.realpath(__file__)).replace('tests/functional', '')


@pytest.fixture()
def nlp(app_path):
    from mmworkbench.components import NaturalLanguageProcessor
    nlp = NaturalLanguageProcessor(app_path=app_path)
    nlp.load()
    return nlp


@pytest.fixture()
def conv(nlp, app_path):
    from mmworkbench import Conversation
    return Conversation(nlp=nlp, app_path=app_path)


class TestUnknown(ConversationalTest):
    def test_unknown(self, conv):
        texts = conv.say("what was the soviet union?")
        self.assert_text(texts, "Sorry, not sure what you meant there.")
