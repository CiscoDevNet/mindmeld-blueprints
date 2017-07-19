import pytest
from conversational_test import ConversationalTest


class TestWeather(ConversationalTest):
    test_data = [
        ('what is the weather today', 'San Francisco', 'Fahrenheit'),
        ('what is the weather today in Celsius', 'San Francisco', 'Celsius'),
        ('what is the weather today in seattle', 'Seattle', 'Fahrenheit'),
        ('what is the weather today in seattle in celsius', 'Seattle', 'Celsius')
    ]

    @pytest.mark.parametrize("query, city, unit", test_data)
    def test_weather(self, query, city, unit):
        texts = self.conv.say(query)
        assert city in texts[0]
        if unit == 'Fahrenheit':
            assert ' F ' in texts[0]
        else:
            assert ' C ' in texts[0]
        self.assert_intent(self.conv, 'check_weather')
