# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'date' domain in
the MindMeld HR assistant blueprint application
"""
from .root import app
from .helpers import extract_entities_from_type
from hr_assistant.general import (
    _resolve_categorical_entities, _resolve_function_entity,
    _resolve_extremes, _agg_function, _get_names, NOT_AN_EMPLOYEE,
    SIZE
)
from dateutil.relativedelta import relativedelta
import datetime
import re


@app.handle(intent='get_date')
def get_date(request, responder):
    """
    If a user asks for a date related information of any person, this function returns
    the required date. In case of a termination date related query, it also informs the user
    of the reason for termination. For non-terminated employees, it informs the user about
    the active current state of the employee in question.
    """

    # Look for name from the context of previous turn
    name = request.frame.get('name')

    # If user presents a new name, update the name in context
    try:
        name_ent = extract_entities_from_type(request, 'name')
        if name_ent:
            name = name_ent[0]['value'][0]['cname']
    except IndexError:
        name = None

    # If neither context nor the current query has an employee name, return not an employee
    if not name:
        responder.reply(NOT_AN_EMPLOYEE)
        responder.listen()
        return

    # If name is found but not in the database, return not an employee
    if name == '':
        responder.reply(NOT_AN_EMPLOYEE)
        return

    responder.slots['name'] = name
    responder.frame['name'] = name

    employee = app.question_answerer.get(index='employee_data', emp_name=name)[0]

    # 'action' entities represent employment action such as hiring or termination
    action_entity = extract_entities_from_type(request, 'employment_action')

    # 'dob' entities represent the date of birth entity
    dob_entity = extract_entities_from_type(request, 'dob')

    # Search for the determined action entity or date of birth in the KB and return.
    # 'doh' - 'date of hire', 'dot' - 'date of termination', 'dob' - 'date of birth'
    if action_entity:
        action_entity = action_entity[0]['value'][0]['cname']

        if action_entity == 'hired':
            date = employee['doh']
            responder.slots['date'] = date
            responder.reply("{name}'s date of hire was {date}")

        # If action is that of termination:
        # If employee was not terminated, express the active employment status of the employee
        # If the employee was terminated, return both the reason and the date of temrination
        elif action_entity == 'fired':
            date = employee['dot']
            responder.slots['date'] = date
            responder.slots['reason'] = employee['rft']

            if responder.slots['reason'] == 'N/A - still employed':
                responder.reply("{name} is still employed.")
            else:
                responder.reply("{name}'s date of termination was {date}.\
                    The reason for termination was: {reason}.")

    elif dob_entity:
        date = employee['dob']
        responder.slots['date'] = date
        responder.reply("{name}'s date of birth is {date}")

    # If no action of dob entities specified by the user, prompt them for specifics in the next turn
    # If the user wants to exit this state they can choose to do that in the return prompt
    # by invoking the 'exit' intent.
    else:
        if request.frame.get('date_visited'):
            responder.reply("If you want to know something else, say 'exit'")
            responder.frame['date_visited'] = False

        else:
            responder.reply('What would you like to know about {name}?\
                You can ask about date of hire, date of termination or date of birth.')
            responder.frame['date_visited'] = True
            responder.params.allowed_intents = ('date.get_date', 'general.get_info',
                                                'salary.get_salary', 'hierarchy.*', 'greeting.*')
            responder.listen()


@app.handle(intent='get_date_range_aggregate')
def get_date_range_aggregate(request, responder):
    """
    When a user asks for a statistic, such as average, sum, count or percentage,
    in addition to a date range filter such as date of hire, termination or birth (required),
    and categorical filters (if any), this function captures all the relevant entities,
    calculates the desired statistic function and returns it.

    'function' entities represent the statistic functions - sum, average, percentage, count
    """

    # Checks for existing function entity from previous turn
    func_entity = request.frame.get('function')

    # If the user provides a new function entity, it replaces the one in context from previous turns
    func_entities = extract_entities_from_type(request, 'function')

    if func_entities:
        func_entity = func_entities[0]

    if func_entity:
        # Resolve the recognized function entity to its canonical form, one that can be used in
        # the output dialog as well as in the '_agg_function', which is used to calculate the values
        # of these desired function entities
        function, responder = _resolve_function_entity(responder, func_entity)

        # If there are any categorical entities (eg. race, gender, position etc.) in the query that
        # need filtering on, '_resolve_categorical_entities' fetches these entities, resolves them
        # to their canonical form and filters the knowledge base on all the conditions requested by
        # the user query
        qa, size = _resolve_categorical_entities(request, responder)

        # Resolve the duration that is explicitly or implicitly mentioned in the query
        # and then filtering the KB to retain all employees satisfying that duration criteria
        out = _resolve_time(request, responder, qa, size)

        if out:
            qa, size, field = out
        qa_out = qa.execute(size=size)

        # Calculate and return desired mathemical value
        responder.slots['value'] = _agg_function(qa_out, func=function)

        if function == 'pct':
            responder.reply("Of the total employees, the {function} "
                            "that meet your criteria is {value}")
        else:
            responder.reply("The {function} of employees is {value}")

    else:
        responder.reply('What time-filtered statistic would you like to know?')
        responder.listen()


@app.handle(intent='get_date_range_employees')
def get_date_range_employees(request, responder):
    """
    When a user asks for a list of employees that satisfy certain criteria in addition
    to satisfying a specified date range criterion (date of hire/termination/birth),
    this dialogue state filters the knowledge base on those criteria and returns the
    shortlisted list of names.
    """

    # If there are any categorical entities (eg. race, gender, department etc.) in the query that
    # need filtering on, '_resolve_categorical_entities' fetches these entities, resolves them to
    # their canonical form and filters the database on all the conditions requested by the query
    qa, size = _resolve_categorical_entities(request, responder)

    # Resolve the duration that is explicitly or implicitly mentioned in the query
    # and then filtering the KB to retain all employees satisfying that duration criteria
    out = _resolve_time(request, responder, qa, size)

    if out:
        qa, size, field = out

        # Finding extreme entities such as 'highest', 'lowest', 'youngest' etc. (if any)
        extreme_entity = extract_entities_from_type(request, 'extreme')

        # Filter on the extreme entities if they exist
        if extreme_entity:
            extreme_entity = extreme_entity[0]
            qa, size = _resolve_extremes(request, responder, qa, extreme_entity, field)

        qa_out = qa.execute(size=size)

        if qa_out:
            responder.slots['emp_list'] = _get_names(qa_out)

            # Give the natural language response according to the size of the list to be displayed
            if len(qa_out) == 1:
                responder.reply("Here is the employee you are looking for: {emp_list}")
            else:
                responder.reply("Here are some employees that match your criteria: {emp_list}")

    else:
        responder.listen()


# Helper functions #

def _check_time_ent(time_ent, date_compare_ent):
    """
    Helper function for resolving non numeric time entities, time entities with
    incompatible date formats, and intervals into the format of time that is
    accepted by the dialogue states defined in this file.
    """

    time_dict = {}
    time_dict.update(dict.fromkeys(['last year', 'this year', 'past year'], 'years'))
    time_dict.update(dict.fromkeys(['last month', 'this month', 'past month'], 'months'))
    time_dict.update(dict.fromkeys(['last week', 'this week', 'past week'], 'weeks'))

    for i in range(len(time_ent)):
        if time_ent[i] in ('last year', 'last month', 'last week', 'past year', 'past week',
                           'past month', 'this year', 'this week', 'this month'):

            # capture duration according to the period in the time entity
            d = datetime.datetime.today()
            kw = {time_dict[time_ent[i]]: 1}
            old_d = d-relativedelta(**kw)
            d = d.strftime('%Y-%m-%d')
            old_d = old_d.strftime('%Y-%m-%d')
            time_ent[i] = old_d
            time_ent.append(d)

        # Accept correct format, continue
        elif len(time_ent[i].split('-')) == 3:
            continue

        # resolve years entities (eg. 2016) and capture the whole year as duration
        elif len(re.split('-|\\|/', time_ent[i])) == 1:

            # check if time entity is numeric
            try:
                int(time_ent[i])
            except ValueError:
                return

            # add duration (i.e. start and end dates) to the time entities list
            try:
                # Consider the beginning of the year as the comparator point if
                # date compare entity is provided
                if date_compare_ent:
                    time_ent[i] = str(time_ent[i])+'-01-01'

                # If no date compare entity, add both beginning and end of year
                # dates to the time entities (to keep track of the whole duration)
                else:
                    # time_old : year mentioned
                    # Added entities: 01-01-YEAR and 12-31-YEAR to cover duration
                    time_old = str(time_ent[i])
                    time_ent[i] = time_old+'-01-01'
                    time_ent.append(time_old+'-12-31')
            except Exception:
                return

        else:
            return

    return time_ent


def _resolve_time(request, responder, qa, size):
    """
    This helper function is useful to resolve any time related entities in the database, including
    both system entities and custom entities. It captures the type of date entity being talked about
    by the user (say employment related -- hired/fired, or birth). It in-turn determines the time
    period being talked about and filters the knowledge to narrow it down to only the datapoints
    satisfying the duration. The returned value is this shortlisted set of employees.
    """

    # 'action' entities represent employment action such as hiring of termination
    # 'dob' entities represent the date of birth entity

    # Fetch existing action entity from a previous turn and clear 'action' context
    action_entity = []
    if request.frame.get('action'):
        action_entity.append(request.frame.get('action'))
        responder.frame['action'] = None

    time_ent = extract_entities_from_type(request, 'sys_time')
    date_compare_ent = extract_entities_from_type(request, 'date_compare')

    # Catch new action entity and update the existing one in context (if any)
    new_action_entity = [e['value'][0]['cname']
                         for e in request.entities
                         if e['type'] == 'employment_action']

    dob_entity = extract_entities_from_type(request, 'dob')

    if new_action_entity:
        action_entity = [e['value'][0]['cname']
                         for e in request.entities
                         if e['type'] == 'employment_action']

    actions = {'hired': 'doh', 'fired': 'dot'}
    if action_entity:
        field = actions[action_entity[0]]
    elif dob_entity:
        field = 'dob'
    else:
        responder.reply("What date would you like to know about? Hire, termination or birth?")
        return []

    # Filter knowledge base on defined time periods
    if time_ent:

        # Check if time entities are in an acceptable format
        time_ent = _check_time_ent(time_ent, date_compare_ent)

        if not time_ent:
            responder.reply('Please repeat your query with a valid date format (YYYY-MM-DD)')
            return []

        # Two time entities specify an exact time period to filter
        if len(time_ent) == 2:
            qa = qa.filter(field=field, gte=time_ent[0], lte=time_ent[1])

        # If there is only one time entity specified, then it could be either
        # the beginning or end of an infinite time period from that date
        elif len(time_ent) == 1:
            if date_compare_ent:
                date_compare_canonical = date_compare_ent[0]['value'][0]['cname']

                if date_compare_canonical == 'prev':
                    qa = qa.filter(field=field, lte=time_ent[0])

                elif date_compare_canonical == 'post':
                    qa = qa.filter(field=field, gte=time_ent[0])

            else:
                qa = qa.filter(field=field, gte=time_ent[0], lte=time_ent[0])

        return [qa, size, field]

    # If no specified time entities, and general query about termination date is asked
    # filter all employees who were fired
    else:
        if field == 'dot':
            qa = qa.filter(field='dot', gt='1800-01-01')
        return [qa, SIZE, field]
