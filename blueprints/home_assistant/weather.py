# -*- coding: utf-8 -*-
"""This module contains the weather dialogue states for the MindMeld
home assistant blueprint application
"""
import os

import requests

from .root import app
from .exceptions import UnitNotFound

# Weather constants
CITY_NOT_FOUND_CODE = 404
INVALID_API_KEY_CODE = 401
DEFAULT_TEMPERATURE_UNIT = 'fahrenheit'
DEFAULT_LOCATION = 'san francisco'
OPENWEATHER_BASE_STRING = 'http://api.openweathermap.org/data/2.5/weather'


@app.handle(intent='check_weather')
def check_weather(request, responder):
    """
    When the user asks for weather, return the weather in that location or use San Francisco if no
      location is given.
    """
    # Check to make sure API key is present, if not tell them to follow setup instructions
    try:
        openweather_api_key = os.environ['OPEN_WEATHER_KEY']
    except KeyError:
        reply = "Open weather API is not setup, please register an API key at https://" \
                "openweathermap.org/api and set env variable OPEN_WEATHER_KEY to be that key."
        responder.reply(reply)
        return

    try:
        # Get the location the user wants
        selected_city = _get_city(request)
        # Figure out which temperature unit the user wants information in
        selected_unit = _get_unit(request)

        # Get weather information via the API
        url_string = _construct_weather_api_url(selected_city, selected_unit, openweather_api_key)

        weather_info = requests.get(url_string).json()
    except ConnectionError:
        reply = "Sorry, I was unable to connect to the weather API, please check your connection."
        responder.reply(reply)
        return
    except UnitNotFound:
        reply = "Sorry, I am not sure which unit you are asking for."
        responder.reply(reply)
        return

    if int(weather_info['cod']) == CITY_NOT_FOUND_CODE:
        reply = "Sorry, I wasn't able to recognize that city."
        responder.reply(reply)
    elif int(weather_info['cod']) == INVALID_API_KEY_CODE:
        reply = "Sorry, the API key is invalid."
        responder.reply(reply)
    else:
        responder.slots['city'] = weather_info['name']
        responder.slots['temp_min'] = weather_info['main']['temp_min']
        responder.slots['temp_max'] = weather_info['main']['temp_max']
        responder.slots['condition'] = weather_info['weather'][0]['main'].lower()
        if selected_unit == "fahrenheit":
            responder.slots['unit'] = 'F'
        else:
            responder.slots['unit'] = 'C'
        responder.reply("The weather forecast in {city} is {condition} with a min of {temp_min} "
                        "{unit} and a max of {temp_max} {unit}.")


# Helpers

def _construct_weather_api_url(selected_location, selected_unit, openweather_api_key):
    unit_string = 'metric' if selected_unit.lower() == 'celsius' else 'imperial'
    url_string = "{base_string}?q={location}&units={unit}&appid={key}".format(
        base_string=OPENWEATHER_BASE_STRING, location=selected_location.replace(" ", "+"),
        unit=unit_string, key=openweather_api_key)

    return url_string


# Entity Resolvers

def _get_city(request):
    """
    Get's the user location from the query, defaulting to San Francisco if none provided

    Args:
        request (Request): contains info about the conversation up to this point (e.g. domain,
          intent, entities, etc)

    Returns:
        string: resolved location entity
    """
    city_entity = next((e for e in request.entities if e['type'] == 'city'), None)

    if city_entity:
        return city_entity['text']
    else:
        # Default to San Francisco
        return DEFAULT_LOCATION


def _get_unit(request):
    """
    Get's the user desired temperature unit from the query, defaulting to Fahrenheit if none
      is provided

    Args:
        request (Request): contains info about the conversation up to this point (e.g. domain,
          intent, entities, etc)

    Returns:
        string: resolved temperature unit entity
    """
    unit_entity = next((e for e in request.entities if e['type'] == 'unit'), None)

    if unit_entity:
        unit_text = unit_entity['text'].lower()

        if unit_text in ['c', 'celsius']:
            return 'celsius'
        elif unit_text in ['f', 'fahrenheit']:
            return 'fahrenheit'
        else:
            raise UnitNotFound

    else:
        # Default to Fahrenheit
        return DEFAULT_TEMPERATURE_UNIT
