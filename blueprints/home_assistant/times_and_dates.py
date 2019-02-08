# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'times_and_dates' domain in
the home assistant blueprint application
"""
import time

from mmworkbench.ser import get_candidates_for_text, parse_numerics

from .root import app


TIME_START_INDEX = 11
TIME_END_INDEX = 19

DEFAULT_TIMER_DURATION = '60 seconds'  # Seconds


# Times and Dates #


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
        reply = "I'm sorry, I wasn't able to recognize that time. Could you try again?"
        responder.reply(reply)


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
            reply = "Of course. Which alarm? Your current alarms: {alarms}".format(
                alarms=ordered_alarms)
            responder.reply(reply)
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
        reply = "Of course. At what time?"
        responder.reply(reply)


@app.handle(intent='start_timer')
def start_timer(context, responder):
    selected_duration = _get_duration(context)

    if _check_timer_status(context):
        reply = 'There is already a timer running!'
    else:
        context['frame']['timer'] = {'start_time': time.time(),
                                     'duration': selected_duration}
        reply = "Ok. A timer for {amt} has been set.".format(amt=selected_duration)

    responder.reply(reply)


@app.handle(intent='stop_timer')
def stop_timer(context, responder):
    if _check_timer_status(context):
        context['frame']['timer'] = None
        reply = 'Ok. The current timer has been cancelled.'
    else:
        reply = 'There is no active timer to cancel!'

    responder.reply(reply)


# Helper Functions


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


def _get_duration_in_seconds(selected_duration):
    """
    Converts hours/minutes to seconds

    Args:
        selected_duration (string): String with number followed by unit
        (e.g. 3 hours, 2 minutes)

    Returns:
        int: duration in seconds
    """
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

        return elapsed_time < timer_amt_in_sec
    else:
        return False


def _timer_finished(context):
    context['frame']['timer'] = None  # Remove the timer


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
        count = duration_entity['value']['value']
        if count == 1:
            unit = duration_entity['value']['unit']
        else:
            unit = duration_entity['value']['unit'] + 's'  # Plural if greater than 1

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
        duckling_result = parse_numerics(sys_time_entity['text'].lower(), dimensions=['time'])
        for candidate in duckling_result[0]:
            if candidate['body'] == sys_time_entity['text'].lower():
                return candidate['value']['value'][TIME_START_INDEX:TIME_END_INDEX]
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
    old_time_entity = next(
        (e for e in context['entities'] if e['role']['type'] == 'old_time'), None)

    if old_time_entity:
        duckling_result = parse_numerics(old_time_entity['text'].lower(), dimensions=['time'])
        for candidate in duckling_result[0]:
            if candidate['body'] == old_time_entity['text'].lower():
                return candidate['value']['value'][TIME_START_INDEX:TIME_END_INDEX]
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
    new_time_entity = next(
        (e for e in context['entities'] if e['role']['type'] == 'new_time'), None)

    if new_time_entity:
        resolved_time = parse_numerics(new_time_entity['text'].lower(), dimensions=['time'])
        for candidate in resolved_time[0]:
            if candidate['body'] == new_time_entity['text'].lower():
                return candidate['value']['value'][TIME_START_INDEX:TIME_END_INDEX]
    else:
        return None


def _get_command_for_all(context):
    """
    Looks at user query to see if user wants to modify all the alarms

    Args:
        context (dict): contains info about the conversation up to this point
        (e.g. domain, intent, entities, etc)

    Returns:
        bool: whether or not the user made a command for all
    """
    return next((e for e in context['entities'] if e['type'] == 'all'), None)
