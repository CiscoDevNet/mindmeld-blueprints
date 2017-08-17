import pytest
import os
from mmworkbench.test import ConversationTest


WEATHER_KEY = 'OPEN_WEATHER_KEY'
WEATHER_INTENT = 'check_weather'


class TestWeather(ConversationTest):
    test_data = [
        ('what is the weather today', 'San Francisco', 'Fahrenheit'),
        ('whats the weather around here', 'San Francisco', 'Fahrenheit'),
        ('what is the weather today in Celsius', 'San Francisco', 'Celsius'),
        ('what is the weather today in seattle', 'Seattle', 'Fahrenheit'),
        ('what is the weather today in seattle in celsius', 'Seattle', 'Celsius')
    ]

    @pytest.mark.parametrize("query, city, unit", test_data)
    def test_weather(self, query, city, unit):
        texts = self.say(query)
        assert city in texts[0]
        if unit == 'Fahrenheit':
            assert ' F ' in texts[0]
        else:
            assert ' C ' in texts[0]
        self.assert_intent(self.conv, expected_intent=WEATHER_INTENT)

    def test_weather_not_setup(self):
        key = os.environ.pop(WEATHER_KEY)
        texts = self.say("what's the weather today?")
        self.assert_intent(self.conv, expected_intent=WEATHER_INTENT)
        self.assert_text(texts, expected_text='Open weather API is not setup, please follow instructions to setup the API.')  # noqa: E501
        os.environ[WEATHER_KEY] = key

    def test_weather_invalid(self):
        key = os.environ.pop(WEATHER_KEY)
        os.environ[WEATHER_KEY] = 'some key'
        texts = self.say("what's the weather today?")
        self.assert_intent(self.conv, expected_intent=WEATHER_INTENT)
        self.assert_text(texts, expected_text='Sorry, the API key is invalid.')
        os.environ[WEATHER_KEY] = key
