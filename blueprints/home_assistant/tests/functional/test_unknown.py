from mmworkbench.test import ConversationTest


class TestUnknown(ConversationTest):
    def test_unknown(self):
        texts = self.say("what was the soviet union?")
        self.assert_text(texts, "Sorry, not sure what you meant there.")
