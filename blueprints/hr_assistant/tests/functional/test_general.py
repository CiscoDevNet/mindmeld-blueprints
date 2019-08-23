import pytest


class TestGeneral:

    hr_query = [
        ("what is mia's role in the company", "Mia Brown's position in the organisation is: "
         "Accountant I")
    ]

    @pytest.mark.parametrize("query, response", hr_query)
    def test_general(self, convo, query, response):
        texts = convo.say(query)
        assert texts[0] == response
