# -*- coding: utf-8 -*-
"""This module contains the Workbench home assistant blueprint application"""
from __future__ import unicode_literals
from mmworkbench import Application
import requests
import os

app = Application(__name__)

CITY_NOT_FOUND_CODE = '404'
INVALID_API_KEY_CODE = '401'
DEFAULT_TEMPERATURE_UNIT = 'Fahrenheit'
DEFAULT_LOCATION = 'San Francisco'
OPENWEATHER_BASE_STRING = 'http://api.openweathermap.org/data/2.5/weather'


@app.handle(intent='check-weather')
def check_weather(context, slots, responder):
    """
    When the user asks for weather, return the weather in that location or use San Francisco if no
      location is given.
    """
    # Check to make sure API key is present, if not tell them to follow setup instructions
    try:
        openweather_api_key = os.environ['OPEN_WEATHER_KEY']
    except KeyError:
        reply = "Open weather API is not setup, please follow instructions to setup the API."
        responder.reply(reply)
        return

    # Get the location the user wants
    selected_location = _get_location(context)
    # Figure out which temperature unit the user wants information in
    selected_unit = _get_unit(context)

    # Get weather information via the API
    url_string = _construct_weather_api_url(selected_location, selected_unit, openweather_api_key)
    try:
        weather_info = requests.get(url_string).json()
    except ConnectionError:
        reply = "Sorry, I was unable to connect to the weather API, please check your connection."
        responder.reply(reply)
        return

    if weather_info['cod'] == CITY_NOT_FOUND_CODE:
        reply = "Sorry, I wasn't able to recognize that city."
        responder.reply(reply)
    elif weather_info['cod'] == INVALID_API_KEY_CODE:
        reply = "Sorry, the API key is invalid."
        responder.reply(reply)
    else:
        slots['city'] = weather_info['name']
        slots['temp_min'] = weather_info['main']['temp_min']
        slots['temp_max'] = weather_info['main']['temp_max']
        slots['condition'] = weather_info['weather'][0]['main']
        responder.reply("The weather in {city} is {condition} with a min of {temp_min} and a max of"
                        " {temp_max}")


@app.handle(intent='unsupported')
@app.handle()
def default(context, slots, responder):
    prompts = ["Sorry, not sure what you meant there."]
    responder.prompt(prompts)


def _kb_fetch(kb_index, kb_id):
    """
    Retrieve the detailed knowledge base entry for a given ID from the specified index.

    Args:
        index (str): The knowledge base index to query
        id (str): Identifier for a specific entry in the index

    Returns:
        dict: The full knowledge base entry corresponding to the given ID.
    """
    return app.question_answerer.get(index=kb_index, id=kb_id)[0]


def _construct_weather_api_url(selected_location, selected_unit, openweather_api_key):
    unit_string = 'metric' if selected_unit == 'Celsius' else 'imperial'
    url_string = "{base_string}?q={location}&units={unit}&appid={key}".format(
        base_string=OPENWEATHER_BASE_STRING, location=selected_location.replace(" ", "+"),
        unit=unit_string, key=openweather_api_key)

    return url_string


def _get_unit(context):
    """
    Get's the user desired temperature unit from the query, defaulting to Fahrenheit if none
      is provided

    Args:
        context (dict): contains info about the conversation up to this point (e.g. domain, intent,
          entities, etc)

    Returns:
        string: resolved temperature unit entity
    """
    unit_entity = next((e for e in context['entities'] if e['type'] == 'unit'), None)

    if unit_entity:
        return _kb_fetch('units', unit_entity['value'][0]['id'])
    else:
        # Default to Fahrenheit
        return DEFAULT_TEMPERATURE_UNIT


def _get_location(context):
    """
    Get's the user location from the query, defaulting to San Francisco if none provided

    Args:
        context (dict): contains info about the conversation up to this point (e.g. domain, intent,
          entities, etc)

    Returns:
        string: resolved location entity
    """
    location_entity = next((e for e in context['entities'] if e['type'] == 'city'), None)

    if location_entity:
        return _kb_fetch('cities', id=location_entity['value'][0]['id'])
    else:
        # Default to San Francisco
        return DEFAULT_LOCATION


if __name__ == '__main__':
    app.cli()
