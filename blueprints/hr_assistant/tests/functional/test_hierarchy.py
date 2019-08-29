import pytest


class TestHierarchy:

    hr_query = [
        ("who is the manager for ivan rogers?", "Simon Roup is Ivan Rogers's manager")
    ]

    @pytest.mark.parametrize("query, response", hr_query)
    def test_hierarchy(self, convo, query, response):
        texts = convo.say(query)
        assert texts[0] == response
