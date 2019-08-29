# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'smart_home' domain in
the home assistant blueprint application
"""
from mindmeld.ser import get_candidates_for_text

from .root import app


DEFAULT_THERMOSTAT_TEMPERATURE = 72
DEFAULT_THERMOSTAT_CHANGE = 1
DEFAULT_THERMOSTAT_LOCATION = 'home'

DEFAULT_HOUSE_LOCATION = None


@app.handle(intent='specify_location')
def specify_location(request, responder):
    selected_all = False
    selected_location = _get_location(request)

    if selected_location:
        try:
            if request.frame['desired_action'] == 'Close Door':
                reply = _handle_door_open_close_reply(selected_all, selected_location, responder,
                                                      desired_state="closed")
            elif request.frame['desired_action'] == 'Open Door':
                reply = _handle_door_open_close_reply(selected_all, selected_location, responder,
                                                      desired_state="opened")
            elif request.frame['desired_action'] == 'Lock Door':
                reply = _handle_door_lock_unlock_reply(selected_all, selected_location, responder,
                                                       desired_state="locked")
            elif request.frame['desired_action'] == 'Unlock Door':
                reply = _handle_door_lock_unlock_reply(selected_all, selected_location, responder,
                                                       desired_state="unlocked")
            elif request.frame['desired_action'] == 'Check Door':
                reply = _handle_check_door_reply(selected_location, responder)
            elif request.frame['desired_action'] == 'Turn On Lights':
                color = _get_color(request) or request.frame.get('desired_color')
                reply = _handle_lights_reply(selected_all, selected_location, responder,
                                             desired_state="on", color=color)
            elif request.frame['desired_action'] == 'Turn Off Lights':
                reply = _handle_lights_reply(selected_all, selected_location, responder,
                                             desired_state="off")
            elif request.frame['desired_action'] == 'Check Lights':
                reply = _handle_check_lights_reply(selected_location, responder)
            elif request.frame['desired_action'] == 'Turn On Appliance':
                selected_appliance = request.frame['appliance']
                reply = _handle_appliance_reply(selected_all, selected_location, selected_appliance,
                                                desired_state="on")
            elif request.frame['desired_action'] == 'Turn Off Appliance':
                selected_appliance = request.frame['appliance']
                reply = _handle_appliance_reply(selected_all, selected_location, selected_appliance,
                                                desired_state="off")
        except KeyError:
            reply = "Please specify an action to go along with that location."

        responder.reply(reply)
    else:
        reply = "I'm sorry, I wasn't able to recognize that location, could you try again?"
        responder.reply(reply)


@app.handle(intent='check_door')
def check_door(request, responder):
    selected_location = _get_location(request)

    if selected_location:
        reply = _handle_check_door_reply(selected_location, responder)
        responder.reply(reply)
    else:
        responder.frame['desired_action'] = 'Check Door'
        reply = "Of course, which door?"
        responder.reply(reply)


@app.handle(intent='close_door')
def close_door(request, responder):
    _handle_door(request, responder, desired_state='closed', desired_action='Close Door')


@app.handle(intent='open_door')
def open_door(request, responder):
    _handle_door(request, responder, desired_state='opened', desired_action='Open Door')


@app.handle(intent='lock_door')
def lock_door(request, responder):
    _handle_door(request, responder, desired_state='locked', desired_action='Lock Door')


@app.handle(intent='unlock_door')
def unlock_door(request, responder):
    _handle_door(request, responder, desired_state='unlocked', desired_action='Unlock Door')


@app.handle(intent='turn_appliance_on', name='turn_on_appliance')
def turn_appliance_on(request, responder):
    _handle_appliance(request, responder, desired_state='on', desired_action='Turn On Appliance',
                      target_dialogue_state='turn_on_appliance')


@app.handle(intent='turn_appliance_off', name='turn_off_appliance')
def turn_appliance_off(request, responder):
    _handle_appliance(request, responder, desired_state='off', desired_action='Turn Off Appliance',
                      target_dialogue_state='turn_off_appliance')


@app.handle(intent='check_lights')
def check_lights(request, responder):
    selected_location = _get_location(request)

    if selected_location:
        reply = _handle_check_lights_reply(selected_location, responder)
        responder.reply(reply)
    else:
        responder.frame['desired_action'] = 'Check Lights'
        reply = "Of course, which lights?"
        responder.reply(reply)


@app.handle(intent='turn_lights_on')
def turn_lights_on(request, responder):
    _handle_lights(request, responder, desired_state='on', desired_action='Turn On Lights')


@app.handle(intent='turn_lights_off')
def turn_lights_off(request, responder):
    _handle_lights(request, responder, desired_state='off', desired_action='Turn Off Lights')


@app.handle(intent='check_thermostat')
def check_thermostat(request, responder):
    selected_location = _get_thermostat_location(request)

    try:
        current_temp = request.frame['thermostat_temperatures'][selected_location]
    except KeyError:
        current_temp = DEFAULT_THERMOSTAT_TEMPERATURE
        responder.frame['thermostat_temperatures'] = {selected_location: current_temp}

    reply = "Current thermostat temperature in the {location} is {temp} degrees F.".format(
        location=selected_location.lower(), temp=current_temp)
    responder.reply(reply)


@app.handle(intent='set_thermostat')
def set_thermostat(request, responder):
    selected_location = _get_thermostat_location(request)
    selected_temperature = _get_temperature(request)

    try:
        thermostat_temperature_dict = request.frame['thermostat_temperatures']
    except KeyError:
        thermostat_temperature_dict = {}
        responder.frame['thermostat_temperatures'] = thermostat_temperature_dict

    thermostat_temperature_dict[selected_location] = selected_temperature
    reply = _handle_thermostat_change_reply(selected_location,
                                            desired_temperature=selected_temperature)
    responder.reply(reply)


@app.handle(intent='turn_up_thermostat')
@app.handle(intent='turn_down_thermostat')
def change_thermostat(request, responder):
    if request.intent == 'turn_up_thermostat':
        desired_direction = 'up'
    else:
        desired_direction = 'down'

    selected_location = _get_thermostat_location(request)
    selected_temperature_change = _get_temperature_change(request)

    new_temp = _modify_thermostat(selected_location, selected_temperature_change, request,
                                  responder, desired_direction)

    reply = _handle_thermostat_change_reply(selected_location, desired_temperature=new_temp)
    responder.reply(reply)


@app.handle(intent='turn_off_thermostat')
@app.handle(intent='turn_on_thermostat')
def turn_off_thermostat(request, responder):
    if request.intent == 'turn_off_thermostat':
        desired_state = 'off'
    else:
        desired_state = 'on'

    selected_location = _get_thermostat_location(request)
    reply = _handle_thermostat_change_reply(selected_location, desired_state=desired_state)
    responder.reply(reply)


# Helpers

def _handle_door(request, responder, desired_state, desired_action):
    selected_all = _get_command_for_all(request)
    selected_location = _get_location(request)

    if selected_all or selected_location:
        reply = _handle_door_lock_unlock_reply(
            selected_all, selected_location, responder, desired_state=desired_state)
        responder.reply(reply)
    else:
        responder.frame['desired_action'] = desired_action
        reply = "Of course, which door?"
        responder.reply(reply)
        responder.listen()


def _handle_appliance(request, responder, desired_state, desired_action, target_dialogue_state):
    selected_all = _get_command_for_all(request)
    selected_location = _get_location(request)
    selected_appliance = _get_appliance(request)

    if request.intent == 'specify_location' or selected_location or selected_all:
        if selected_all:
            reply = "Ok. All {app} have been turned {state}.".format(
                app=selected_appliance, state=desired_state)
            responder.params.target_dialogue_state = None
        elif selected_location:
            reply = "Ok. The {loc} {app} has been turned {state}.".format(
                loc=selected_location, app=selected_appliance, state=desired_state)
            responder.params.target_dialogue_state = None
        else:
            reply = "I'm sorry, I wasn't able to recognize that location, could you try again?"
        responder.reply(reply)
    else:
        responder.frame['desired_action'] = desired_action
        responder.frame['appliance'] = selected_appliance
        responder.params.target_dialogue_state = target_dialogue_state

        reply = "Of course, which {appliance}?".format(appliance=selected_appliance)
        responder.reply(reply)
        responder.listen()


def _handle_lights(request, responder, desired_state, desired_action):
    selected_all = _get_command_for_all(request)
    selected_location = _get_location(request)
    color = _get_color(request)

    if selected_all or selected_location:
        reply = _handle_lights_reply(
            selected_all, selected_location, responder, desired_state=desired_state, color=color)
        responder.reply(reply)
    else:
        responder.frame['desired_action'] = desired_action
        responder.frame['desired_color'] = color
        reply = "Of course, which lights?"
        responder.reply(reply)
        responder.listen()


def _modify_thermostat(selected_location, selected_temperature_change, request, responder,
                       direction):
    try:
        thermostat_temperature_dict = request.frame['thermostat_temperatures']
    except KeyError:
        thermostat_temperature_dict = {selected_location: DEFAULT_THERMOSTAT_TEMPERATURE}
        responder.frame['thermostat_temperatures'] = thermostat_temperature_dict

    if direction == 'up':
        thermostat_temperature_dict[selected_location] += selected_temperature_change
    else:
        thermostat_temperature_dict[selected_location] -= selected_temperature_change

    return thermostat_temperature_dict[selected_location]


def _handle_check_lights_reply(selected_location, responder):
    if 'lights' not in responder.frame:
        responder.frame['lights'] = {}

    try:
        state = responder.frame['lights'][selected_location]
        reply = "The {location} lights are {state}.".format(location=selected_location, state=state)

    except KeyError:
        responder.frame['lights'][selected_location] = 'off'
        reply = "The {location} lights are off.".format(location=selected_location)

    return reply


def _handle_lights_reply(selected_all, selected_location, responder, desired_state, color=None):
    if 'lights' not in responder.frame:
        responder.frame['lights'] = {}

    if selected_all:
        for light_location in responder.frame['lights'].keys():
            responder.frame['lights'][light_location] = desired_state
        reply = "Ok. All lights have been turned {state}.".format(state=desired_state)
    elif selected_location and color:
        responder.frame['lights'][selected_location] = desired_state
        reply = "Ok. The {location} lights have been turned {state} with {color}.".format(
            location=selected_location.lower(), state=desired_state, color=color)
    elif selected_location:
        responder.frame['lights'][selected_location] = desired_state
        reply = "Ok. The {location} lights have been turned {state}.".format(
            location=selected_location.lower(), state=desired_state)

    return reply


def _handle_check_door_reply(selected_location, responder):
    if 'doors' not in responder.frame:
        responder.frame['doors'] = {}

    if selected_location not in responder.frame['doors']:
        responder.frame['doors'][selected_location] = {}

    try:
        lock_state = responder.frame['doors'][selected_location]['lock_state']
    except KeyError:
        responder.frame['doors'][selected_location]['lock_state'] = 'locked'
        lock_state = 'locked'

    try:
        open_state = responder.frame['doors'][selected_location]['open_state']
    except KeyError:
        responder.frame['doors'][selected_location]['open_state'] = 'closed'
        open_state = 'closed'

    reply = "The {location} door is {lock_state} and {open_state}.".format(
        location=selected_location, lock_state=lock_state, open_state=open_state)
    return reply


def _handle_door_open_close_reply(selected_all, selected_location, responder, desired_state):
    if 'doors' not in responder.frame:
        responder.frame['doors'] = {}

    if selected_all:
        for door_location in responder.frame['doors'].keys():
            responder.frame['doors'][door_location]['open_state'] = desired_state
        reply = "Ok. All doors have been {state}.".format(state=desired_state)
    elif selected_location:
        if selected_location not in responder.frame['doors']:
            responder.frame['doors'][selected_location] = {}

        responder.frame['doors'][selected_location]['open_state'] = desired_state
        reply = "Ok. The {location} door has been {state}.".format(
            location=selected_location.lower(), state=desired_state)

    return reply


def _handle_door_lock_unlock_reply(selected_all, selected_location, responder, desired_state):
    if 'doors' not in responder.frame:
        responder.frame['doors'] = {}

    if selected_all:
        for door_location in responder.frame['doors'].keys():
            responder.frame['doors'][door_location]['lock_state'] = desired_state
        reply = "Ok. All doors have been {state}.".format(state=desired_state)
    elif selected_location:
        if selected_location not in responder.frame['doors']:
            responder.frame['doors'][selected_location] = {}

        responder.frame['doors'][selected_location]['lock_state'] = desired_state
        reply = "Ok. The {location} door has been {state}.".format(
            location=selected_location.lower(), state=desired_state)

    return reply


def _handle_appliance_reply(selected_all, selected_location, selected_appliance, desired_state):
    if selected_all:
        reply = "Ok. All {app} have been turned {state}.".format(
            app=selected_appliance, state=desired_state)
    elif selected_location:
        reply = "Ok. The {loc} {app} has been turned {state}.".format(
            loc=selected_location, app=selected_appliance, state=desired_state)
    else:
        reply = "I'm sorry, I wasn't able to recognize that location, could you try again?"
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


def _get_color(request):
    """
    Get color from request

    Args:
        request (Request): contains info about the conversation up to this point (e.g. domain,
          intent, entities, etc)

    Returns:
        string: resolved location entity
    """
    color_entity = next((e for e in request.entities if e['type'] == 'color'), None)
    return color_entity['text'] if color_entity else None


def _get_appliance(request):
    """
    Get's the user target appliance, should always detect something

    Args:
        request (Request): contains info about the conversation up to this point
        (e.g. domain, intent, entities, etc)

    Returns:
        string: resolved appliance entity
    """
    appliance_entity = next((e for e in request.entities if e['type'] == 'appliance'), None)

    if appliance_entity:
        return appliance_entity['text'].lower()
    elif 'appliance' in request.frame:
        return request.frame['appliance']
    else:
        raise Exception("There should always be a recognizable appliance if we go down this intent")


def _get_thermostat_location(request):
    """
    Get's the user desired thermostat location within house from the query, defaults to 'home'

    Args:
        request (Request): contains info about the conversation up to this point
        (e.g. domain, intent, entities, etc)

    Returns:
        string: resolved location entity, 'home' if no resolution
    """
    location_entity = next((e for e in request.entities if e['type'] == 'location'), None)

    if location_entity:
        return location_entity['text'].lower()
    else:
        return DEFAULT_THERMOSTAT_LOCATION


def _get_temperature(request):
    """
    Get's the user desired temperature to set thermostat to, defaults to 72 degrees

    Args:
        request (Request): contains info about the conversation up to this point
        (e.g. domain, intent, entities, etc)

    Returns:
        string: resolved temperature entity
    """
    temperature_entity = get_candidates_for_text(request.text,
                                                 entity_types='sys_temperature')

    if temperature_entity:
        return temperature_entity[0]['value']['value']
    else:
        return DEFAULT_THERMOSTAT_TEMPERATURE


def _get_temperature_change(request):
    """
    Get's the user desired temperature change for thermostat, defaults to 1 degree

    Args:
        request (Request): contains info about the conversation up to this point
        (e.g. domain, intent, entities, etc)

    Returns:
        string: resolved temperature entity
    """
    temperature_entity = get_candidates_for_text(request.text,
                                                 entity_types='sys_temperature')

    if temperature_entity:
        return temperature_entity[0]['value']['value']
    else:
        return DEFAULT_THERMOSTAT_CHANGE


def _get_location(request):
    """
    Get's the user desired location within house from the query

    Args:
        request (Request): contains info about the conversation up to this point
        (e.g. domain, intent, entities, etc)

    Returns:
        string: resolved location entity
    """
    location_entity = next((e for e in request.entities if e['type'] == 'location'), None)

    if location_entity:
        return location_entity['text'].lower()
    else:
        # Default to Fahrenheit
        return DEFAULT_HOUSE_LOCATION


def _get_command_for_all(request):
    """
    Looks at user query to see if user wants all the lights or all the doors turned off

    Args:
        request (Request): contains info about the conversation up to this point
        (e.g. domain, intent, entities, etc)

    Returns:
        bool: whether or not the user made a command for all
    """
    return next((e for e in request.entities if e['type'] == 'all'), None)
