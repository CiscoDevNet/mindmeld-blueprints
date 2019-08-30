import pytest


class TestGreeting:

    hr_query = [
        ("Hi There!", "Hi, I am your HR assistant. You can ask me about an employee's individual "
         "information (eg. Is Mia married?), some employee statistic (eg. average salary of "
         "females) or names of employees according to your criteria(eg. give me a list of all "
         "married employees) or general policy questions")
    ]

    @pytest.mark.parametrize("query, response", hr_query)
    def test_greeting(self, convo, query, response):
        texts = convo.say(query)
        assert texts[0] == response
