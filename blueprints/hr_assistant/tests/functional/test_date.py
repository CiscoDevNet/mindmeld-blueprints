import pytest


class TestDate:

    hr_query = [
        ("How many people have worked here since 2016", 'The count is 11')
    ]

    @pytest.mark.parametrize("query, response", hr_query)
    def test_date(self, convo, query, response):
        texts = convo.say(query)
        assert texts[0] == response
