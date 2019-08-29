import pytest


class TestFaq:

    hr_query = [
        ("can you answer a question for me", "Sure, what do you want to know?",
         "how can I print my pay statement")
    ]

    @pytest.mark.parametrize("query1, response1, query2", hr_query)
    def test_follow_up(self, convo, query1, response1, query2):
        texts = convo.say(query1)
        assert texts[0] == response1

        texts = convo.say(query2)
        assert texts[0].startswith('Here is the top result')

    hr_query = [
        ("what should i do if i don't receieve my w2",)
    ]

    @pytest.mark.parametrize("query", hr_query)
    def test_single_query(self, convo, query):
        texts = convo.say(query)
        assert texts[0].startswith('Here is the top result')
