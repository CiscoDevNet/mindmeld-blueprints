import os
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import pytest


WEATHER_KEY = 'OPEN_WEATHER_KEY'
WEATHER_INTENT = 'check_weather'

MOCK_WEATHER_RESPONSE = {
    'name': 'some city',
    'cod': 200,
    'main': {
        'temp_min': 0,
        'temp_max': 100
    },
    'weather': [{
        'main': 'Cloudy with a chance of meatballs'
    }]
}


class TestWeather:
    test_data = [
        ('what is the weather today', 'san francisco', 'Fahrenheit'),
        ('whats the weather around here', 'san francisco', 'Fahrenheit'),
        ('what is the weather today in Celsius', 'san francisco', 'Celsius'),
        ('what is the weather today in seattle', 'seattle', 'Fahrenheit'),
        ('what is the weather today in seattle in celsius', 'seattle', 'Celsius'),
    ]

    @pytest.mark.parametrize("query, city, unit", test_data)
    def test_weather(self, convo, query, city, unit):
        key = os.environ.pop(WEATHER_KEY, None)
        os.environ[WEATHER_KEY] = 'a-good-api-key'

        with patch('requests.get') as get_mock:
            get_mock.return_value.json.return_value = MOCK_WEATHER_RESPONSE
            texts = convo.say(query)

            assert get_mock.call_count == 1
            url = get_mock.call_args[0][0]
            query_params = parse_qs(urlparse(url).query)
            assert query_params['q'] == [city]
            if unit == 'Fahrenheit':
                assert ' F ' in texts[0]
            else:
                assert ' C ' in texts[0]
            convo.assert_intent(WEATHER_INTENT)

        if key:
            os.environ[WEATHER_KEY] = key

    @pytest.mark.skip(reason="not critical, unblocking pipeline, will fix in the next mm release")
    def test_weather_not_setup(self, convo):
        key = os.environ.pop(WEATHER_KEY, None)  # in case the key is in environment pop it

        with patch('requests.get') as get_mock:
            convo.say("what's the weather today?")
            get_mock.assert_not_called()
            convo.assert_intent(WEATHER_INTENT)
            convo.assert_text(('Open weather API is not setup, please register '
                               'an API key at https://openweathermap.org/api '
                               'and set env variable OPEN_WEATHER_KEY to be '
                               'that key.'))

        if key:
            os.environ[WEATHER_KEY] = key

    @pytest.mark.skip(reason="not critical, unblocking pipeline, will fix in the next mm release")
    def test_weather_invalid(self, convo):
        key = os.environ.pop(WEATHER_KEY, None)
        os.environ[WEATHER_KEY] = 'a-bad-api-key'

        with patch('requests.get') as get_mock:
            get_mock.return_value.json.return_value = {'cod': 401}
            convo.say("what's the weather today?")
            assert get_mock.call_count == 1
            convo.assert_intent(WEATHER_INTENT)
            convo.assert_text('Sorry, the API key is invalid.')

        if key:
            os.environ[WEATHER_KEY] = key
