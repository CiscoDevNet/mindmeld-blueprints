# -*- coding: utf-8 -*-
"""This module contains the Workbench home assistant blueprint application"""
from __future__ import unicode_literals
from mmworkbench import Application
from mmworkbench.ser import parse_numerics
import requests
import os

app = Application(__name__)

# Weather constants
CITY_NOT_FOUND_CODE = '404'
INVALID_API_KEY_CODE = '401'
DEFAULT_TEMPERATURE_UNIT = 'fahrenheit'
DEFAULT_LOCATION = 'San Francisco'
OPENWEATHER_BASE_STRING = 'http://api.openweathermap.org/data/2.5/weather'

DEFAULT_THERMOSTAT_TEMPERATURE = 72
DEFAULT_THERMOSTAT_LOCATION = 'home'
DEFAULT_HOUSE_LOCATION = None
DEFAULT_TEMPERATURE_CHANGE = None

TIME_START_INDEX = 11
TIME_END_INDEX = 19

DEFAULT_TIMER_DURATION = '60 seconds'  # Seconds


@app.handle(frame=0)
def test(context, slots, responder):
    print("HERE!!!!")

@app.handle(intent='check_weather')
def check_weather(context, slots, responder):
    """
    When the user asks for weather, return the weather in that location or use San Francisco if no
      location is given.
    """
    # Check to make sure API key is present, if not tell them to follow setup instructions

    print(context)
    context['frame'] = 0
    try:
        openweather_api_key = os.environ['OPEN_WEATHER_KEY']
    except KeyError:
        reply = "Open weather API is not setup, please follow instructions to setup the API."
        responder.reply(reply)
        return

    # Get the location the user wants
    selected_city = _get_city(context)
    # Figure out which temperature unit the user wants information in
    selected_unit = _get_unit(context)

    # Get weather information via the API
    url_string = _construct_weather_api_url(selected_city, selected_unit, openweather_api_key)
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
        slots['condition'] = weather_info['weather'][0]['main'].lower()
        if selected_unit == "fahrenheit":
            slots['unit'] = 'F'
        else:
            slots['unit'] = 'C'
        responder.reply("The weather forecast in {city} is {condition} with a min of {temp_min} "
                        "{unit} and a max of {temp_max} {unit}")


# Smart Home #

@app.handle(intent='specify_location')
def specify_location(context, slots, responder):

    selected_all = False
    selected_location = _get_location(context)

    if context['frame']['desired_action'] == 'Close Door':
        reply = _handle_door_reply(selected_all, selected_location, desired_state="closed")
    elif context['frame']['desired_action'] == 'Open Door':
        reply = _handle_door_reply(selected_all, selected_location, desired_state="opened")
    elif context['frame']['desired_action'] == 'Lock Door':
        reply = _handle_door_reply(selected_all, selected_location, desired_state="locked")
    elif context['frame']['desired_action'] == 'Unlock Door':
        reply = _handle_door_reply(selected_all, selected_location, desired_state="unlocked")
    elif context['frame']['desired_action'] == 'Turn On Lights':
        reply = _handle_lights_reply(selected_all, selected_location, desired_state="on")
    elif context['frame']['desired_action'] == 'Turn Off Lights':
        reply = _handle_lights_reply(selected_all, selected_location, desired_state="off")
    elif context['frame']['desired_action'] == 'Turn On Appliance':
        selected_appliance = context['frame']['appliance']
        reply = _handle_appliance_reply(selected_location, selected_appliance, desired_state="on")
    elif context['frame']['desired_action'] == 'Turn Off Appliance':
        selected_appliance = context['frame']['appliance']
        reply = _handle_appliance_reply(selected_location, selected_appliance, desired_state="off")

    responder.reply(reply)


@app.handle(intent='specify_temperature')
def specify_temperature(context, slots, responder):

    selected_temperature_amount = _get_temperature(context)
    selected_location = context['frame']['thermostat_location']

    thermostat_temperature_dict = context['frame']['thermostat_temperatures']

    if context['frame']['desired_action'] == 'Set Thermostat':
        thermostat_temperature_dict[selected_location] = selected_temperature_amount
        reply = _handle_thermostat_change_reply(selected_location,
                                                desired_temperature=selected_temperature_amount)
    elif context['frame']['desired_action'] == 'Turn Up Thermostat':
        thermostat_temperature_dict[selected_location] += selected_temperature_amount

        new_temperature = thermostat_temperature_dict[selected_location]
        reply = _handle_thermostat_change_reply(selected_location,
                                                desired_temperature=new_temperature)
    elif context['frame']['desired_action'] == 'Turn Down Thermostat':
        thermostat_temperature_dict[selected_location] -= selected_temperature_amount

        new_temperature = thermostat_temperature_dict[selected_location]
        reply = _handle_thermostat_change_reply(selected_location,
                                                desired_temperature=new_temperature)

    responder.reply(reply)


@app.handle(intent='close_door')
def close_door(context, slots, responder):

    selected_all = _get_command_for_all(context)
    selected_location = _get_location(context)

    if selected_all or selected_location:
        reply = _handle_door_reply(selected_all, selected_location, desired_state="closed")
        responder.reply(reply)
    else:
        context['frame']['desired_action'] = 'Close Door'
        prompt = "Of course, which door?"
        responder.prompt(prompt)


@app.handle(intent='open_door')
def open_door(context, slots, responder):

    selected_all = _get_command_for_all(context)
    selected_location = _get_location(context)

    if selected_all or selected_location:
        reply = _handle_door_reply(selected_all, selected_location, desired_state="opened")
        responder.reply(reply)
    else:
        context['frame']['desired_action'] = 'Open Door'
        prompt = "Of course, which door?"
        responder.prompt(prompt)


@app.handle(intent='lock_door')
def lock_door(context, slots, responder):

    selected_all = _get_command_for_all(context)
    selected_location = _get_location(context)

    if selected_all or selected_location:
        reply = _handle_door_reply(selected_all, selected_location, desired_state="locked")
        responder.reply(reply)
    else:
        context['frame']['desired_action'] = 'Lock Door'
        prompt = "Of course, which door?"
        responder.prompt(prompt)


@app.handle(intent='unlock_door')
def unlock_door(context, slots, responder):

    selected_all = _get_command_for_all(context)
    selected_location = _get_location(context)

    if selected_all or selected_location:
        reply = _handle_door_reply(selected_all, selected_location, desired_state="unlocked")
        responder.reply(reply)
    else:
        context['frame']['desired_action'] = 'Unlock Door'
        prompt = "Of course, which door?"
        responder.prompt(prompt)


@app.handle(intent='turn_appliance_on')
def turn_appliance_on(context, slots, responder):

    selected_location = _get_location(context)
    selected_appliance = _get_appliance(context)

    if selected_location:
        reply = _handle_appliance_reply(selected_location, selected_appliance, desired_state="on")
        responder.reply(reply)
    else:
        context['frame']['desired_action'] = 'Turn On'
        context['frame']['appliance'] = selected_appliance

        prompt = "Of course, which {appliance}".format(appliance=selected_appliance)
        responder.prompt(prompt)


@app.handle(intent='turn_appliance_off')
def turn_appliance_off(context, slots, responder):

    selected_location = _get_location(context)
    selected_appliance = _get_appliance(context)

    if selected_location:
        reply = _handle_appliance_reply(selected_location, selected_appliance, desired_state="off")
        responder.reply(reply)
    else:
        context['frame']['desired_action'] = 'Turn Off'
        context['frame']['appliance'] = selected_appliance

        prompt = "Of course, which {appliance}".format(appliance=selected_appliance)
        responder.prompt(prompt)


@app.handle(intent='turn_lights_on')
def turn_lights_on(context, slots, responder):

    selected_all = _get_command_for_all(context)
    selected_location = _get_location(context)

    if selected_all or selected_location:
        reply = _handle_lights_reply(selected_all, selected_location, desired_state="on")
        responder.reply(reply)
    else:
        context['frame']['desired_action'] = 'Turn On Lights'
        prompt = "Of course, which lights?"
        responder.prompt(prompt)


@app.handle(intent='turn_lights_off')
def turn_lights_off(context, slots, responder):

    selected_all = _get_command_for_all(context)
    selected_location = _get_location(context)

    if selected_all or selected_location:
        reply = _handle_lights_reply(selected_all, selected_location, desired_state="off")
        responder.reply(reply)
    else:
        context['frame']['desired_action'] = 'Turn Off Lights'
        prompt = "Of course, which lights?"
        responder.prompt(prompt)


@app.handle(intent='check_thermostat')
def check_thermostat(context, slots, responder):

    selected_location = _get_thermostat_location(context)

    try:
        current_temp = context['frame']['thermostat_temperatures'][selected_location]
    except KeyError:
        current_temp = DEFAULT_THERMOSTAT_TEMPERATURE
        context['frame']['thermostat_temperatures'] = {selected_location: current_temp}

    reply = "Current thermostat temperature in the {location} is {temp} F.".format(
        location=selected_location.lower(), temp=current_temp)
    responder.reply(reply)


@app.handle(intent='set_thermostat')
def set_thermostat(context, slots, responder):

    selected_location = _get_thermostat_location(context)
    selected_temperature = _get_temperature(context)

    try:
        thermostat_temperature_dict = context['frame']['thermostat_temperatures']
    except:
        thermostat_temperature_dict = {}
        context['frame']['thermostat_temperatures'] = thermostat_temperature_dict

    if selected_temperature:
        thermostat_temperature_dict[selected_location] = selected_temperature
        reply = _handle_thermostat_change_reply(selected_location,
                                                desired_temperature=selected_temperature)
        responder.reply(reply)
    else:
        context['frame']['desired_action'] = "Set Thermostat"
        prompt = "Of course, what temperature shall I set it to?"
        responder.prompt(prompt)


@app.handle(intent='turn_down_thermostat')
def turn_down_thermostat(context, slots, responder):

    selected_location = _get_thermostat_location(context)
    selected_temperature_amount = _get_temperature(context)

    try:
        thermostat_temperature_dict = context['frame']['thermostat_temperatures']
    except:
        thermostat_temperature_dict = {selected_location: DEFAULT_THERMOSTAT_TEMPERATURE}
        context['frame']['thermostat_temperatures'] = thermostat_temperature_dict

    if selected_temperature_amount:
        thermostat_temperature_dict[selected_location] -= selected_temperature_amount
        new_temperature = thermostat_temperature_dict[selected_location]

        reply = _handle_thermostat_change_reply(selected_location,
                                                desired_temperature=new_temperature)
        responder.reply(reply)
    else:
        context['frame']['desired_action'] = "Turn Down Thermostat"
        context['frame']['thermostat_location'] = selected_location
        prompt = "Of course, by how much?"
        responder.prompt(prompt)


@app.handle(intent='turn_up_thermostat')
def turn_up_thermostat(context, slots, responder):

    selected_location = _get_thermostat_location(context)
    selected_temperature_amount = _get_temperature(context)

    try:
        thermostat_temperature_dict = context['frame']['thermostat_temperatures']
    except:
        thermostat_temperature_dict = {selected_location: DEFAULT_THERMOSTAT_TEMPERATURE}
        context['frame']['thermostat_temperatures'] = thermostat_temperature_dict

    if selected_temperature_amount:
        thermostat_temperature_dict[selected_location] += selected_temperature_amount
        new_temperature = thermostat_temperature_dict[selected_location]

        reply = _handle_thermostat_change_reply(selected_location,
                                                desired_temperature=new_temperature)
        responder.reply(reply)
    else:
        context['frame']['desired_action'] = "Turn Up Thermostat"
        prompt = "Of course, by how much?"
        responder.prompt(prompt)


@app.handle(intent='turn_off_thermostat')
def turn_off_thermostat(context, slots, responder):

    selected_location = _get_thermostat_location(context)
    reply = _handle_thermostat_change_reply(selected_location, desired_state='off')
    responder.reply(reply)


@app.handle(intent='turn_on_thermostat')
def turn_on_thermostat(context, slots, responder):

    selected_location = _get_thermostat_location(context)
    reply = _handle_thermostat_change_reply(selected_location, desired_state='on')
    responder.reply(reply)

# Times and Dates #


@app.handle(intent='change_alarm')
def change_alarm(context, slots, responder):

    selected_old_time = _get_old_time(context)
    selected_new_time = _get_new_time(context)

    try:
        existing_alarms_dict = context['frame']['alarms']
        if selected_old_time in existing_alarms_dict:
            del existing_alarms_dict[selected_old_time]
            existing_alarms_dict[selected_new_time] = None

            reply = "Ok. I have changed your {old} alarm to {new}".format(old=selected_old_time,
                                                                          new=selected_new_time)
        else:
            reply = "There is no alarm currently set for that time that you want to change."

    except KeyError:
        reply = "There are no alarms currently set."

    responder.reply(reply)


@app.handle(intent='check_alarm')
def check_alarm(context, slots, responder):

    try:
        ordered_alarms = sorted(context['frame']['alarms'].keys())
        reply = "Your current active alarms: {alarms}".format(alarms=", ".join(ordered_alarms))
    except KeyError:
        reply = "You have no alarms currently set."

    responder.reply(reply)


@app.handle(intent='remove_alarm')
def remove_alarm(context, slots, responder):

    # Get time entity from query
    selected_time = _get_sys_time(context)

    try:
        existing_alarms_dict = context['frame']['alarms']

        if selected_time in existing_alarms_dict:
            del existing_alarms_dict[selected_time]
            reply = "Ok, I have removed your {time} alarm.".format(selected_time)
        else:
            reply = "There is no alarm currently set for that time."

    except KeyError:
        reply = "There are no alarms currently set."

    responder.reply(reply)


@app.handle(intent='set_alarm')
def set_alarm(context, slots, responder):

    selected_time = _get_sys_time(context)

    if selected_time:
        try:
            existing_alarms_dict = context['frame']['alarms']
            existing_alarms_dict[selected_time] = None
        except KeyError:
            context['frame']['alarms'] = {selected_time: None}

        reply = "Ok, I have set your alarm for {time}.".format(time=selected_time)
        responder.reply(reply)
    else:
        prompt = "Please try your request again with a specific time."
        responder.prompt(prompt)


@app.handle(intent='start_timer')
def start_timer(context, slots, responder):

    selected_duration = _get_duration(context)
    try:
        current_timer = context['frame']['timer']
    except KeyError:
        current_timer = None

    if current_timer:
        reply = 'There is already a timer running!'
    else:
        context['frame']['timer'] = True
        reply = "Ok. A timer for {amt} has been set.".format(amt=selected_duration)

    responder.reply(reply)


@app.handle(intent='stop_timer')
def stop_timer(context, slots, responder):

    try:
        current_timer = context['frame']['timer']
    except KeyError:
        current_timer = None
        context['frame']['timer'] = None

    if current_timer:
        context['frame']['timer'] = None
        reply = 'Ok. The current timer has been cancelled'
    else:
        reply = 'There is no active timer to cancel!'

    responder.reply(reply)


@app.handle(intent='unsupported')
@app.handle()
def default(context, slots, responder):
    prompts = ["Sorry, not sure what you meant there."]
    responder.prompt(prompts)


# Helper Functions

def _timer_finished(context):
    context['frame']['timer'] = None  # Remove the timer


def _construct_weather_api_url(selected_location, selected_unit, openweather_api_key):
    unit_string = 'metric' if selected_unit.lower() == 'celsius' else 'imperial'
    url_string = "{base_string}?q={location}&units={unit}&appid={key}".format(
        base_string=OPENWEATHER_BASE_STRING, location=selected_location.replace(" ", "+"),
        unit=unit_string, key=openweather_api_key)

    return url_string


def _handle_lights_reply(selected_all, selected_location, desired_state):

    if selected_all:
        reply = "Ok. All lights have been turned {state}.".format(state=desired_state)
    elif selected_location:
        reply = "Ok. The {location} lights have been turned {state}.".format(
            location=selected_location.lower(), state=desired_state)

    return reply


def _handle_door_reply(selected_all, selected_location, desired_state):

    if selected_all:
        reply = "Ok. All doors have been {state}.".format(state=desired_state)
    elif selected_location:
        reply = "Ok. The {location} door has been {state}.".format(
            location=selected_location.lower(), state=desired_state)

    return reply


def _handle_appliance_reply(selected_location, selected_appliance, desired_state):

    reply = "Ok. The {appliance} has been turned {state}.".format(appliance=selected_appliance,
                                                                  state=desired_state)
    return reply


def _handle_thermostat_change_reply(selected_location, desired_temperature=None,
                                    desired_state=None):

    if desired_temperature:
        reply = "The thermostat temperature in the {location} is now {temp} degrees F.".format(
            location=selected_location, temp=desired_temperature)
    elif desired_state:
        reply = "Ok. The thermostat in the {location} has been turned {state}.".format(
            location=selected_location, state=desired_state)

    return reply


# Entity Resolvers


def _get_duration(context):
    """
    Get's the duration the user wants to set a timer for

    Args:
        context (dict): contains info about the conversation up to this point
        (e.g. domain, intent, entities, etc)

    Returns:
        int: the seconds
    """
    duration_entity = next((e for e in context['entities'] if e['type'] == 'duration'), None)

    if duration_entity:
        return duration_entity['text'].lower()
    else:
        return DEFAULT_TIMER_DURATION


def _get_sys_time(context):
    """
    Get's the user desired time

    Args:
        context (dict): contains info about the conversation up to this point
        (e.g. domain, intent, entities, etc)

    Returns:
        string: resolved 24-hour time in XX:XX:XX format
    """
    sys_time_entity = next((e for e in context['entities'] if e['type'] == 'sys_time'), None)

    if sys_time_entity:
        resolved_time = parse_numerics(sys_time_entity['text'].lower(), dimensions=['time'])
        return resolved_time['data'][0]['value'][0][TIME_START_INDEX:TIME_END_INDEX]
    else:
        return None


def _get_old_time(context):
    """
    Get's the alarm time the user wants to change

    Args:
        context (dict): contains info about the conversation up to this point
        (e.g. domain, intent, entities, etc)

    Returns:
        string: resolved 24-hour time in XX:XX:XX format
    """
    old_time_entity = next((e for e in context['entities'] if e['role'] == 'old_time'), None)

    if old_time_entity:
        resolved_time = parse_numerics(old_time_entity['text'].lower(), dimensions=['time'])
        return resolved_time['data'][0]['value'][0][TIME_START_INDEX:TIME_END_INDEX]
    else:
        return None


def _get_new_time(context):
    """
    Get's the alarm time the user wants to change to

    Args:
        context (dict): contains info about the conversation up to this point
        (e.g. domain, intent, entities, etc)

    Returns:
        string: resolved 24-hour time in XX:XX:XX format
    """
    new_time_entity = next((e for e in context['entities'] if e['role'] == 'new_time'), None)

    if new_time_entity:
        resolved_time = parse_numerics(new_time_entity['text'].lower(), dimensions=['time'])

        return resolved_time['data'][0]['value'][0][TIME_START_INDEX:TIME_END_INDEX]
    else:
        return None


def _get_location(context):
    """
    Get's the user desired location within house from the query

    Args:
        context (dict): contains info about the conversation up to this point
        (e.g. domain, intent, entities, etc)

    Returns:
        string: resolved location entity
    """
    location_entity = next((e for e in context['entities'] if e['type'] == 'location'), None)

    if location_entity:
        return location_entity['text'].lower()
    else:
        # Default to Fahrenheit
        return DEFAULT_HOUSE_LOCATION


def _get_command_for_all(context):
    """
    Looks at user query to see if user wants all the lights or all the doors turned off

    Args:
        context (dict): contains info about the conversation up to this point
        (e.g. domain, intent, entities, etc)

    Returns:
        bool: whether or not the user made a command for all
    """
    return next((e for e in context['entities'] if e['type'] == 'all'), None)


def _get_appliance(context):
    """
    Get's the user target appliance, should always detect something

    Args:
        context (dict): contains info about the conversation up to this point
        (e.g. domain, intent, entities, etc)

    Returns:
        string: resolved appliance entity
    """
    appliance_entity = next((e for e in context['entities'] if e['type'] == 'appliance'), None)

    if appliance_entity:
        return appliance_entity['text'].lower()
    else:
        raise Exception("There should always be a recognizable appliance if we go down this intent")


def _get_thermostat_location(context):
    """
    Get's the user desired thermostat location within house from the query, defaults to 'home'

    Args:
        context (dict): contains info about the conversation up to this point
        (e.g. domain, intent, entities, etc)

    Returns:
        string: resolved location entity, 'home' if no resolution
    """
    location_entity = next((e for e in context['entities'] if e['type'] == 'location'), None)

    if location_entity:
        return location_entity['text'].lower()
    else:
        return DEFAULT_THERMOSTAT_LOCATION


def _get_temperature(context):
    """
    Get's the user desired temperature or temperature change

    Args:
        context (dict): contains info about the conversation up to this point
        (e.g. domain, intent, entities, etc)

    Returns:
        string: resolved temperature entity
    """
    temperature_entity = next((e for e in context['entities'] if e['type'] == 'sys_temperature'),
                              None)

    if temperature_entity:
        temperature_text = temperature_entity['text']
        # Get the first number
        return int(next(w for w in temperature_text.split() if w.isdigit()))
    else:
        return DEFAULT_TEMPERATURE_CHANGE


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
        unit_text = unit_entity['text'].lower()

        if unit_text[0] == 'c':
            return 'celsius'
        else:
            return 'fahrenheit'
    else:
        # Default to Fahrenheit
        return DEFAULT_TEMPERATURE_UNIT


def _get_city(context):
    """
    Get's the user location from the query, defaulting to San Francisco if none provided

    Args:
        context (dict): contains info about the conversation up to this point (e.g. domain, intent,
          entities, etc)

    Returns:
        string: resolved location entity
    """
    city_entity = next((e for e in context['entities'] if e['type'] == 'city'), None)

    if city_entity:
        return city_entity['text']
    else:
        # Default to San Francisco
        return DEFAULT_LOCATION


if __name__ == '__main__':
    app.cli()
