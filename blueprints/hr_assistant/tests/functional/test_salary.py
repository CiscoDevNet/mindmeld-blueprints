import pytest


class TestSalary:

    hr_query = [
        ("what is the average salary in the production engineering department", "Based on your "
         "criteria, the average salary is $23.11")
    ]

    @pytest.mark.parametrize("query, response", hr_query)
    def test_salary(self, convo, query, response):
        texts = convo.say(query)
        assert texts[0] == response
