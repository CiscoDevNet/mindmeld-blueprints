from conversational_test import ConversationalTest


class TestUnknown(ConversationalTest):
    def test_unknown(self):
        texts = self.conv.say("what was the soviet union?")
        self.assert_text(texts, "Sorry, not sure what you meant there.")
