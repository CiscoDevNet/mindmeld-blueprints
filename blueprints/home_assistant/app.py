# -*- coding: utf-8 -*-
"""This module contains the Workbench home assistant blueprint application"""
from __future__ import unicode_literals
from mmworkbench import Application
import json

app = Application(__name__)

@app.handle(intent='check-weather')
def check_weather(context, slots, responder):
    """
    When the user asks for weather, return the weather in that location or use San Francisco if no location given
    """

    selected_location = None
    selected_unit = None
    current_location_coordinates = None

    # Check for user's requested city and temperature unit
    location_entity = next((e for e in context['entities'] if e['type'] == 'city'), None)
    unit_entity = next((e for e in context['entities'] if e['type'] == 'unit'), None)

    # Use user location if location is none
    if location_entity:
        selected_location = _kb_fetch('cities', location_entity['value'][0]['id'])
    else:
        # Option 1: Prompt them for location if it cannot be determined
        # try:
        #     current_location_coordinates = context['request']['session']['location']
        #
        # except KeyError:
        #
        #     responder.prompt("I couldn't figure out where you are, what city would you like the weather for?")
        #     return

        # Option 2: Default to San Francisco
        selected_location = 'San Francisco'

    # Figure out which unit the user wants information in
    if unit_entity:
        selected_unit = _kb_fetch('units', unit_entity['value'][0]['id'])
        context['frame']['unit'] = selected_unit
    else:
        # Default to Fahrenheit
        selected_unit = 'Fahrenheit'

    # TODO - Is this necessary for this type of flow?
    context['frame']['city'] = selected_location
    context['frame']['unit'] = selected_unit

    # Construct the api url to get the weather information
    base_string = "http://api.openweathermap.org/data/2.5/weather"
    api_key_string = "&appid=9a648df5a003b74f815f0d3f27a5be84"
    unit_key_string = '&units='
    if selected_unit=='Celcius':
        unit_key_string += 'metric'
    else:
        unit_key_string += 'imperial'

    if selected_location: # City
        location_string = "?q=" + selected_location.replace(" ", "+")
    else: # Coordinates
        location_string = "?lat={}&lon={}".format(current_location_coordinates['lat'], current_location_coordinates['lon'])

    url = base_string + api_key_string + unit_key_string + location_string
    weather_info = json.load(url)

    if weather_info['message'] == 'city not found':
        reply = "Sorry, I wasn't able to recognize that city"
        responder.reply(reply)
    else:
        slots['city'] = weather_info['name']
        slots['temp_min'] = weather_info['main']['temp_min']
        slots['temp_max'] = weather_info['main']['temp_max']
        slots['condition'] = weather_info['weather'][0]['main']
        responder.reply("The weather in {city} is {condition} with a min of {temp_min} and a max of {temp_max}")


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


if __name__ == '__main__':
    app.cli()