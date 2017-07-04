class ConversationalTest(object):
    def assert_text(self, texts, expected_text):
        assert texts[0] == expected_text
