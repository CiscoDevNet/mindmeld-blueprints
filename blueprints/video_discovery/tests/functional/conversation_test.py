class ConversationTest(object):
    @staticmethod
    def assert_domain(response, expected):
        actual = response['domain']
        assert actual == expected

    @staticmethod
    def assert_intent(response, expected):
        actual = response['intent']
        assert actual == expected
