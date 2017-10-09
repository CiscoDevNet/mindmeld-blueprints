# -*- coding: utf-8 -*-
"""This module contains the Workbench home assistant blueprint application"""
from __future__ import unicode_literals

import os

import requests

import time
from mmworkbench import Application
from mmworkbench.ser import get_candidates_for_text
from mmworkbench.ser import parse_numerics

#if __name__ == "__main__" and __package__ is None:
#    load_app_package(os.path.dirname(os.path.realpath(__file__)))
#    __package__ = 'home_assistant'

#from .ha_exception import UnitNotFound  # noqa: E402

app = Application(__name__)

# Weather constants
CITY_NOT_FOUND_CODE = 404
INVALID_API_KEY_CODE = 401
DEFAULT_TEMPERATURE_UNIT = 'fahrenheit'
DEFAULT_LOCATION = 'San Francisco'
OPENWEATHER_BASE_STRING = 'http://api.openweathermap.org/data/2.5/weather'

DEFAULT_THERMOSTAT_TEMPERATURE = 72
DEFAULT_THERMOSTAT_CHANGE = 1
DEFAULT_THERMOSTAT_LOCATION = 'home'

DEFAULT_HOUSE_LOCATION = None

TIME_START_INDEX = 11
TIME_END_INDEX = 19

DEFAULT_TIMER_DURATION = '60 seconds'  # Seconds


@app.handle(intent='greet')
def greet(context, responder):
    responder.reply('Hi, I am your home assistant. I can help you to check weather, set temperature'
                    ' and control the lights and other appliances.')


@app.handle(intent='exit')
def exit(context, responder):
    responder.reply('Bye!')


@app.handle(intent='check_weather')
def check_weather(context, responder):
    """
    When the user asks for weather, return the weather in that location or use San Francisco if no
      location is given.
    """
    # Check to make sure API key is present, if not tell them to follow setup instructions
    try:
        openweather_api_key = os.environ['OPEN_WEATHER_KEY']
    except KeyError:
        reply = "Open weather API is not setup, please regsiter an API key at https://" \
                "openweathermap.org/api and set env variable OPEN_WEATHER_KEY to be that key."
        responder.reply(reply)
        return

    try:
        # Get the location the user wants
        selected_city = _get_city(context)
        # Figure out which temperature unit the user wants information in
        selected_unit = _get_unit(context)

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


# Smart Home #

@app.handle(intent='specify_location')
def specify_location(context, responder):
    selected_all = False
    selected_location = _get_location(context)

    if selected_location:
        try:
            if context['frame']['desired_action'] == 'Close Door':
                reply = _handle_door_open_close_reply(selected_all, selected_location, context,
                                                      desired_state="closed")
            elif context['frame']['desired_action'] == 'Open Door':
                reply = _handle_door_open_close_reply(selected_all, selected_location, context,
                                                      desired_state="opened")
            elif context['frame']['desired_action'] == 'Lock Door':
                reply = _handle_door_lock_unlock_reply(selected_all, selected_location, context,
                                                       desired_state="locked")
            elif context['frame']['desired_action'] == 'Unlock Door':
                reply = _handle_door_lock_unlock_reply(selected_all, selected_location, context,
                                                       desired_state="unlocked")
            elif context['frame']['desired_action'] == 'Check Door':
                reply = _handle_check_door_reply(selected_location, context)
            elif context['frame']['desired_action'] == 'Turn On Lights':
                color = _get_color(context) or context['frame'].get('desired_color')
                reply = _handle_lights_reply(selected_all, selected_location, context,
                                             desired_state="on", color=color)
            elif context['frame']['desired_action'] == 'Turn Off Lights':
                reply = _handle_lights_reply(selected_all, selected_location, context,
                                             desired_state="off")
            elif context['frame']['desired_action'] == 'Check Lights':
                reply = _handle_check_lights_reply(selected_location, context)
            elif context['frame']['desired_action'] == 'Turn On Appliance':
                selected_appliance = context['frame']['appliance']
                reply = _handle_appliance_reply(selected_all, selected_location, selected_appliance,
                                                desired_state="on")
            elif context['frame']['desired_action'] == 'Turn Off Appliance':
                selected_appliance = context['frame']['appliance']
                reply = _handle_appliance_reply(selected_all, selected_location, selected_appliance,
                                                desired_state="off")

            del context['frame']['desired_action']

        except KeyError:
            reply = "Please specify an action to go along with that location."

        responder.reply(reply)
    else:
        prompt = "I'm sorry, I wasn't able to recognize that location, could you try again?"
        responder.prompt(prompt)


@app.handle(intent='specify_time')
def specify_time(context, responder):
    selected_time = _get_sys_time(context)
    selected_all = _get_command_for_all(context)

    reply = "Please try again and specify an action to go along with that time."

    if selected_time:

        if 'desired_action' in context['frame']:
            if context['frame']['desired_action'] == 'Set Alarm':
                reply = _handle_set_alarm_reply(selected_time, context)

            elif context['frame']['desired_action'] == 'Remove Alarm':
                existing_alarms_dict = context['frame']['alarms']
                ordered_alarms = sorted(context['frame']['alarms'].keys())

                reply = _handle_remove_alarm_reply(selected_all, selected_time,
                                                   existing_alarms_dict,
                                                   ordered_alarms)

            del context['frame']['desired_action']

        responder.reply(reply)

    else:
        prompt = "I'm sorry, I wasn't able to recognize that time. Could you try again?"
        responder.prompt(prompt)


@app.handle(intent='check_door')
def check_door(context, responder):
    selected_location = _get_location(context)

    if selected_location:
        reply = _handle_check_door_reply(selected_location, context)
        responder.reply(reply)
    else:
        context['frame']['desired_action'] = 'Check Door'
        prompt = "Of course, which door?"
        responder.prompt(prompt)


@app.handle(intent='close_door')
def close_door(context, responder):
    _handle_door(context, responder, desired_state='closed', desired_action='Close Door')


@app.handle(intent='open_door')
def open_door(context, responder):
    _handle_door(context, responder, desired_state='opened', desired_action='Open Door')


@app.handle(intent='lock_door')
def lock_door(context, responder):
    _handle_door(context, responder, desired_state='locked', desired_action='Lock Door')


@app.handle(intent='unlock_door')
def unlock_door(context, responder):
    _handle_door(context, responder, desired_state='unlocked', desired_action='Unlock Door')


@app.handle(intent='turn_appliance_on', has_entity='appliance', name='turn_on_appliance')
@app.handle(intent='turn_appliance_on', name='turn_on_appliance')
def turn_appliance_on(context, responder):
    print "in turn appliance on intent"
    context['target_dialogue_state'] = "turn_on_appliance"
    _handle_appliance(context, responder, desired_state='on', desired_action='Turn On Appliance')


@app.handle(intent='turn_appliance_off', has_entity='appliance', name='turn_off_appliance')
@app.handle(intent='turn_appliance_off', name='turn_off_appliance')
def turn_appliance_off(context, responder):
    print "in turn appliance off intent"
    context['target_dialogue_state'] = "turn_off_appliance"
    _handle_appliance(context, responder, desired_state='off', desired_action='Turn Off Appliance')


@app.handle(intent='check_lights')
def check_lights(context, responder):
    selected_location = _get_location(context)

    if selected_location:
        reply = _handle_check_lights_reply(selected_location, context)
        responder.reply(reply)
    else:
        context['frame']['desired_action'] = 'Check Lights'
        prompt = "Of course, which lights?"
        responder.prompt(prompt)


@app.handle(intent='turn_lights_on')
def turn_lights_on(context, responder):
    _handle_lights(context, responder, desired_state='on', desired_action='Turn On Lights')


@app.handle(intent='turn_lights_off')
def turn_lights_off(context, responder):
    _handle_lights(context, responder, desired_state='off', desired_action='Turn Off Lights')


@app.handle(intent='check_thermostat')
def check_thermostat(context, responder):
    selected_location = _get_thermostat_location(context)

    try:
        current_temp = context['frame']['thermostat_temperatures'][selected_location]
    except KeyError:
        current_temp = DEFAULT_THERMOSTAT_TEMPERATURE
        context['frame']['thermostat_temperatures'] = {selected_location: current_temp}

    reply = "Current thermostat temperature in the {location} is {temp} degrees F.".format(
        location=selected_location.lower(), temp=current_temp)
    responder.reply(reply)


@app.handle(intent='set_thermostat')
def set_thermostat(context, responder):
    selected_location = _get_thermostat_location(context)
    selected_temperature = _get_temperature(context)

    try:
        thermostat_temperature_dict = context['frame']['thermostat_temperatures']
    except:
        thermostat_temperature_dict = {}
        context['frame']['thermostat_temperatures'] = thermostat_temperature_dict

    thermostat_temperature_dict[selected_location] = selected_temperature
    reply = _handle_thermostat_change_reply(selected_location,
                                            desired_temperature=selected_temperature)
    responder.reply(reply)


@app.handle(intent='turn_up_thermostat')
@app.handle(intent='turn_down_thermostat')
def change_thermostat(context, responder):
    if context['intent'] == 'turn_up_thermostat':
        desired_direction = 'up'
    else:
        desired_direction = 'down'

    selected_location = _get_thermostat_location(context)
    selected_temperature_change = _get_temperature_change(context)

    new_temp = _modify_thermostat(selected_location, selected_temperature_change, context,
                                  desired_direction)

    reply = _handle_thermostat_change_reply(selected_location, desired_temperature=new_temp)
    responder.reply(reply)


@app.handle(intent='turn_off_thermostat')
@app.handle(intent='turn_on_thermostat')
def turn_off_thermostat(context, responder):
    if context['intent'] == 'turn_off_thermostat':
        desired_state = 'off'
    else:
        desired_state = 'on'

    selected_location = _get_thermostat_location(context)
    reply = _handle_thermostat_change_reply(selected_location, desired_state=desired_state)
    responder.reply(reply)


# Times and Dates #


@app.handle(intent='change_alarm')
def change_alarm(context, responder):
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
def check_alarm(context, responder):
    try:
        ordered_alarms = sorted(context['frame']['alarms'].keys())
        if len(ordered_alarms) == 0:
            reply = "You have no alarms currently set."
        else:
            reply = "Your current active alarms: {alarms}".format(alarms=", ".join(ordered_alarms))
    except KeyError:
        reply = "You have no alarms currently set."

    responder.reply(reply)


@app.handle(intent='remove_alarm')
def remove_alarm(context, responder):
    # Get time entity from query
    selected_all = _get_command_for_all(context)
    selected_time = _get_sys_time(context)

    try:
        existing_alarms_dict = context['frame']['alarms']
        ordered_alarms = sorted(context['frame']['alarms'].keys())

        if selected_all or selected_time:

            reply = _handle_remove_alarm_reply(selected_all, selected_time, existing_alarms_dict,
                                               ordered_alarms)

        else:
            context['frame']['desired_action'] = 'Remove Alarm'
            prompt = "Of course. Which alarm? Your current alarms: {alarms}".format(
                alarms=ordered_alarms)
            responder.prompt(prompt)
            return

    except KeyError:
        reply = "There are no alarms currently set."

    responder.reply(reply)


@app.handle(intent='set_alarm')
def set_alarm(context, responder):
    selected_time = _get_sys_time(context)

    if selected_time:
        reply = _handle_set_alarm_reply(selected_time, context)
        responder.reply(reply)
    else:
        context['frame']['desired_action'] = 'Set Alarm'
        prompt = "Of course. At what time?"
        responder.prompt(prompt)


@app.handle(intent='start_timer')
def start_timer(context, responder):
    selected_duration = _get_duration(context)
    is_timer_running = _check_timer_status(context)

    if is_timer_running:
        reply = 'There is already a timer running!'
    else:
        context['frame']['timer'] = {'start_time': time.time(),
                                     'duration': selected_duration}
        reply = "Ok. A timer for {amt} has been set.".format(amt=selected_duration)

    responder.reply(reply)


@app.handle(intent='stop_timer')
def stop_timer(context, responder):
    is_timer_running = _check_timer_status(context)

    if is_timer_running:
        context['frame']['timer'] = None
        reply = 'Ok. The current timer has been cancelled.'
    else:
        reply = 'There is no active timer to cancel!'

    responder.reply(reply)


@app.handle(intent='unknown')
def unknown(context, responder):
    replies = ["Sorry, not sure what you meant there."]
    responder.reply(replies)


# Helper Functions


def _get_duration_in_seconds(selected_duration):
    num_time, num_unit = selected_duration.split(' ')

    if num_unit == 'hours':
        num_time = int(num_time) * 3600
    elif num_unit == 'minutes':
        num_time = int(num_time) * 60

    return int(num_time)


def _check_timer_status(context):
    try:
        current_timer = context['frame']['timer']
    except KeyError:
        current_timer = None

    if current_timer:
        selected_duration = current_timer['duration']
        current_timer_start_time = current_timer['start_time']

        timer_amt_in_sec = _get_duration_in_seconds(selected_duration)
        elapsed_time = time.time() - current_timer_start_time

        is_timer_running = elapsed_time < timer_amt_in_sec
    else:
        is_timer_running = False

    return is_timer_running


def _handle_door(context, responder, desired_state, desired_action):
    selected_all = _get_command_for_all(context)
    selected_location = _get_location(context)

    if selected_all or selected_location:
        reply = _handle_door_lock_unlock_reply(
            selected_all, selected_location, context, desired_state=desired_state)
        responder.reply(reply)
    else:
        context['frame']['desired_action'] = desired_action
        prompt = "Of course, which door?"
        responder.prompt(prompt)


def _handle_appliance(context, responder, desired_state, desired_action):
    selected_all = _get_command_for_all(context)
    selected_location = _get_location(context)
    selected_appliance = _get_appliance(context)

    if selected_all or selected_location:
        reply = _handle_appliance_reply(
            selected_all, selected_location, selected_appliance, desired_state=desired_state)
        context['target_dialogue_state'] = None
        responder.reply(reply)
    else:
        context['frame']['desired_action'] = desired_action
        context['frame']['appliance'] = selected_appliance

        prompt = "Of course, which {appliance}?".format(appliance=selected_appliance)
        responder.prompt(prompt)


def _handle_lights(context, responder, desired_state, desired_action):
    selected_all = _get_command_for_all(context)
    selected_location = _get_location(context)
    color = _get_color(context)

    if selected_all or selected_location:
        reply = _handle_lights_reply(
            selected_all, selected_location, context, desired_state=desired_state, color=color)
        responder.reply(reply)
    else:
        context['frame']['desired_action'] = desired_action
        context['frame']['desired_color'] = color
        prompt = "Of course, which lights?"
        responder.prompt(prompt)


def _modify_thermostat(selected_location, selected_temperature_change, context, direction):
    try:
        thermostat_temperature_dict = context['frame']['thermostat_temperatures']
    except:
        thermostat_temperature_dict = {selected_location: DEFAULT_THERMOSTAT_TEMPERATURE}
        context['frame']['thermostat_temperatures'] = thermostat_temperature_dict

    if direction == 'up':
        thermostat_temperature_dict[selected_location] += selected_temperature_change
    else:
        thermostat_temperature_dict[selected_location] -= selected_temperature_change

    return thermostat_temperature_dict[selected_location]


def _timer_finished(context):
    context['frame']['timer'] = None  # Remove the timer


def _construct_weather_api_url(selected_location, selected_unit, openweather_api_key):
    unit_string = 'metric' if selected_unit.lower() == 'celsius' else 'imperial'
    url_string = "{base_string}?q={location}&units={unit}&appid={key}".format(
        base_string=OPENWEATHER_BASE_STRING, location=selected_location.replace(" ", "+"),
        unit=unit_string, key=openweather_api_key)

    return url_string


def _handle_check_lights_reply(selected_location, context):
    if 'lights' not in context['frame']:
        context['frame']['lights'] = {}

    try:
        state = context['frame']['lights'][selected_location]
        reply = "The {location} lights are {state}.".format(location=selected_location, state=state)

    except KeyError:
        context['frame']['lights'][selected_location] = 'off'
        reply = "The {location} lights are off.".format(location=selected_location)

    return reply


def _handle_lights_reply(selected_all, selected_location, context, desired_state, color=None):
    if 'lights' not in context['frame']:
        context['frame']['lights'] = {}

    if selected_all:
        for light_location in context['frame']['lights'].keys():
            context['frame']['lights'][light_location] = desired_state
        reply = "Ok. All lights have been turned {state}.".format(state=desired_state)
    elif selected_location and color:
        context['frame']['lights'][selected_location] = desired_state
        reply = "Ok. The {location} lights have been turned {state} with {color}.".format(
            location=selected_location.lower(), state=desired_state, color=color)
    elif selected_location:
        context['frame']['lights'][selected_location] = desired_state
        reply = "Ok. The {location} lights have been turned {state}.".format(
            location=selected_location.lower(), state=desired_state)

    return reply


def _handle_check_door_reply(selected_location, context):
    if 'doors' not in context['frame']:
        context['frame']['doors'] = {}

    if selected_location not in context['frame']['doors']:
        context['frame']['doors'][selected_location] = {}

    try:
        lock_state = context['frame']['doors'][selected_location]['lock_state']
    except KeyError:
        context['frame']['doors'][selected_location]['lock_state'] = 'locked'
        lock_state = 'locked'

    try:
        open_state = context['frame']['doors'][selected_location]['open_state']
    except KeyError:
        context['frame']['doors'][selected_location]['open_state'] = 'closed'
        open_state = 'closed'

    reply = "The {location} door is {l} and {o}.".format(location=selected_location,
                                                         l=lock_state, o=open_state)
    return reply


def _handle_door_open_close_reply(selected_all, selected_location, context, desired_state):
    if 'doors' not in context['frame']:
        context['frame']['doors'] = {}

    if selected_all:
        for door_location in context['frame']['doors'].keys():
            context['frame']['doors'][door_location]['open_state'] = desired_state
        reply = "Ok. All doors have been {state}.".format(state=desired_state)
    elif selected_location:
        if selected_location not in context['frame']['doors']:
            context['frame']['doors'][selected_location] = {}

        context['frame']['doors'][selected_location]['open_state'] = desired_state
        reply = "Ok. The {location} door has been {state}.".format(
            location=selected_location.lower(), state=desired_state)

    return reply


def _handle_door_lock_unlock_reply(selected_all, selected_location, context, desired_state):
    if 'doors' not in context['frame']:
        context['frame']['doors'] = {}

    if selected_all:
        for door_location in context['frame']['doors'].keys():
            context['frame']['doors'][door_location]['lock_state'] = desired_state
        reply = "Ok. All doors have been {state}.".format(state=desired_state)
    elif selected_location:
        if selected_location not in context['frame']['doors']:
            context['frame']['doors'][selected_location] = {}

        context['frame']['doors'][selected_location]['lock_state'] = desired_state
        reply = "Ok. The {location} door has been {state}.".format(
            location=selected_location.lower(), state=desired_state)

    return reply


def _handle_appliance_reply(selected_all, selected_location, selected_appliance, desired_state):
    if selected_all:
        reply = "Ok. All {app} have been turned {state}.".format(
            app=selected_appliance, state=desired_state)
    else:
        reply = "Ok. The {loc} {app} has been turned {state}.".format(
            loc=selected_location, app=selected_appliance, state=desired_state)
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


def _handle_set_alarm_reply(selected_time, context):
    try:
        existing_alarms_dict = context['frame']['alarms']
        existing_alarms_dict[selected_time] = None
    except KeyError:
        context['frame']['alarms'] = {selected_time: None}

    reply = "Ok, I have set your alarm for {time}.".format(time=selected_time)
    return reply


def _handle_remove_alarm_reply(selected_all, selected_time, existing_alarms_dict, ordered_alarms):
    if existing_alarms_dict:
        if selected_all:
            existing_alarms_dict.clear()
            reply = "Ok, all alarms ({alarms}) have been removed".format(alarms=ordered_alarms)
        elif selected_time in existing_alarms_dict:
            del existing_alarms_dict[selected_time]
            reply = "Ok, I have removed your {time} alarm.".format(time=selected_time)
        else:
            reply = "There is no alarm currently set for that time. Your current alarms: " \
                    "{alarms}".format(alarms=ordered_alarms)
    else:
        reply = "There are no alarms currently set"

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
    duration_entity_candidates = get_candidates_for_text(
        context['request']['text'], entity_types='sys_duration')

    duration_entity = None \
        if len(duration_entity_candidates) == 0 else duration_entity_candidates[0]

    if duration_entity:
        count = duration_entity['value'][0]
        if count == 1:
            unit = duration_entity['unit']
        else:
            unit = duration_entity['unit'] + 's'  # Plural if greater than 1

        return "{count} {units}".format(count=count, units=unit)
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
    Get's the user desired temperature to set thermostat to, defaults to 72 degrees

    Args:
        context (dict): contains info about the conversation up to this point
        (e.g. domain, intent, entities, etc)

    Returns:
        string: resolved temperature entity
    """
    temperature_entity = get_candidates_for_text(context['request']['text'],
                                                 entity_types='sys_temperature')

    if temperature_entity:
        return temperature_entity[0]['value'][0]
    else:
        return DEFAULT_THERMOSTAT_TEMPERATURE


def _get_temperature_change(context):
    """
    Get's the user desired temperature change for thermostat, defaults to 1 degree

    Args:
        context (dict): contains info about the conversation up to this point
        (e.g. domain, intent, entities, etc)

    Returns:
        string: resolved temperature entity
    """
    temperature_entity = get_candidates_for_text(context['request']['text'],
                                                 entity_types='sys_temperature')

    if temperature_entity:
        return temperature_entity[0]['value'][0]
    else:
        return DEFAULT_THERMOSTAT_CHANGE


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

        if unit_text in ['c', 'celsius']:
            return 'celsius'
        elif unit_text in ['f', 'fahrenheit']:
            return 'fahrenheit'
        else:
            raise UnitNotFound

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


def _get_color(context):
    """
    Get color from context

    Args:
        context (dict): contains info about the conversation up to this point (e.g. domain, intent,
          entities, etc)

    Returns:
        string: resolved location entity
    """
    color_entity = next((e for e in context['entities'] if e['type'] == 'color'), None)
    return color_entity['text'] if color_entity else None


if __name__ == '__main__':
    app.cli()
