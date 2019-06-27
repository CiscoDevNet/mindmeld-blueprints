# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'salary' domain in 
the MindMeld HR assistant blueprint application
"""
import os
import requests
from .root import app
from hr_assistant.general import _resolve_categorical_entities, _resolve_function_entity, _resolve_extremes, _agg_function, _get_names, _get_person_info, _fetch_from_kb, _not_an_employee
import numpy as np



@app.handle(intent='get_salary')
def get_salary(request, responder):
	"""
	If a user asks for the salary of a specific person, this function returns their
	hourly salary by querying into the knowledge base according to the employee name.
	"""

	responder = _get_person_info(request, responder, 'money')
	try:
		responder.reply("{name}'s hourly salary is {money}")
	except:
		responder.reply(_not_an_employee())
		return


@app.handle(intent='get_salary', has_entity='time_recur')
def get_salary_for_interval(request, responder):
	"""
	If a user asks for the salary of a specific person for a given time interval (say hourly,
	daily, weekly, monthly, yearly; default = hourly), this dialogue state fetches the hourly
	salary from the knowledge base and returns it after converting it to the requested
	time interval.
	"""
	
	recur_ent = [e['value'][0]['cname'] for e in request.entities if e['type'] == 'time_recur'][0]

	responder = _get_person_info(request, responder, 'money')

	money = responder.slots['money']
	total_money = _get_interval_amount(recur_ent, money)
	
	responder.slots['money'] = total_money
	responder.slots['interval'] = recur_ent
	
	try:
		replies = ["{name}'s {interval} salary is ${money}", "{name}'s {interval} wage is ${money}"]
		responder.reply(replies)
	except:
		responder.reply(_not_an_employee())
		return


@app.handle(intent='get_salary_aggregate')
def get_salary_aggregate(request, responder):
	"""
	When a user asks for a statistic, such as average, sum, count or percentage,
	in addition to an income related filter (required) and categorical filters (if any), 
	this function captures all the relevant entities, calculates the desired 
	statistic function and returns it.
	"""

	# Checks for existing function entity from previous turn
	func_entity = request.frame.get('function')

	# If the user provides a new function entity, it replaces the one in context from previous turns
	func_entities = [e for e in request.entities if e['type'] == 'function']
	money_entities = [e for e in request.entities if e['type'] == 'money']
	recur_ent = [e['value'][0]['cname'] for e in request.entities if e['type'] == 'time_recur']
	extreme_entity = [e for e in request.entities if e['type'] == 'extreme']

	qa, size = _resolve_categorical_entities(request, responder)
	qa = _resolve_time_in_salary(request, responder, qa)
	
	salary_response = "Hmm, looks like you want a salary statistic. You can ask me about averages, sums, counts and percentages. For eg. what is the average salary for women?" 

	if func_entities:
		func_entity = func_entities[0]

	if func_entity:
		function, responder = _resolve_function_entity(responder, func_entity)

		if money_entities:
			try:
				qa, size = _apply_money_filter(qa, money_entities, request, responder)
			except:
				responder.reply("I see you are looking for the {function}, can you be more specific?")
				responder.frame['function']=func_entity
				responder.params.allowed_intents = ('general.get_aggregate', 'salary.get_salary_aggregate', 'date.get_date_range_aggregate', 'unsupported.unsupported', 'greeting.*')
				responder.listen()
				return

			qa_out = qa.execute(size=size)
			if recur_ent and function in ('avg','sum'):
				responder = _calculate_agg_salary(responder, qa_out, function, recur_ent[0])
				if np.isnan(responder.slots['value']):
					responder.reply(salary_response)
					responder.listen()
					return
				responder.reply("the {function} {interval} salary, based on your criteria, is ${value}")
			else:
				responder = _calculate_agg_salary(responder, qa_out, function)
				if np.isnan(responder.slots['value']):
					responder.reply(salary_response)
					responder.listen()
					return

				if function in ('avg', 'sum'):
					responder.reply('Based on your criteria, the {function} salary is ${value}')
				else:
					responder.reply("The {function} of employees is {value}")

		elif function not in ('avg','sum'):
			qa_out = qa.execute(size=size)
			responder = _calculate_agg_salary(responder, qa_out, function)
			if np.isnan(responder.slots['value']):
					responder.reply(salary_response)
					responder.listen()
					return
			responder.reply("The {function} of employees is {value}")

		else:
			responder.reply("I see you are looking for the {function}, can you be more specific?")
			responder.frame['function']=func_entity
			responder.params.allowed_intents = ('general.get_aggregate', 'salary.get_salary_aggregate', 'date.get_date_range_aggregate')
			responder.listen()

	else:
		responder.reply(salary_response)
		responder.listen()



@app.handle(intent='get_salary_employees')
def get_salary_employees(request, responder):
	"""
	When a user asks for a list of employees that satisfy certain criteria in addition
	to satisfying a specified monetary criterion, this dialogue state filters the 
	knowledge base on those criteria and returns the shortlisted list of names.
	"""

	money_entities = [e for e in request.entities if e['type'] == 'money']

	categorical_entities = [e for e in request.entities if e['type'] in ('state', 'sex', 'maritaldesc','citizendesc',
		'racedesc','performance_score','employment_status','employee_source','position','department')]

	qa, size = _resolve_categorical_entities(request, responder)

	qa = _resolve_time_in_salary(request, responder, qa)

	if money_entities:
		qa, size = _apply_money_filter(qa, money_entities, request, responder)

	qa_out = qa.execute(size=size)
	responder.slots['emp_list'] = _get_names(qa_out)

	if qa_out:
		if size == 1:
			responder.reply("Here is the employee you are looking for with their hourly pay: {emp_list}")
		else:
			responder.reply("Here are some employees with their hourly pay: {emp_list}")
	else:
		responder.reply("No such employees found")


### Helper functions ###


def _resolve_time_in_salary(request, responder, qa):
	"""
	Filter out the knowledge base based on any date queries relevant to the salary data
	"""

	time_entities = [e['value'][0]['value'] for e in request.entities if e['type'] == 'sys_time']
	date_compare_ent = [e['value'][0]['cname'] for e in request.entities if e['type'] == 'date_compare']
	dob_entity = [e for e in request.entities if e['type'] == 'dob']
	action_entity=[e['value'][0]['cname'] for e in request.entities if e['type'] == 'employment_action']

	field = ''
	if action_entity:
		action_entity = action_entity[0]
		if action_entity=='hired':
			field = 'doh'
		elif action_entity=='fired':
			field = 'dot'
	elif dob_entity:
		field = 'dob'


	if time_entities and field:
		if len(time_entities)==2:
			qa = qa.filter(field=field, gte=time_entities[0], lte=time_entities[1])
		elif len(time_entities)==1:
			if date_compare_ent:
				if date_compare_ent[0]=='prev':
					qa = qa.filter(field=field, lte=time_entities[0])
				else:
					qa = qa.filter(field=field, gte=time_entities[0])
			else:
				qa = qa.filter(field=field, gte=time_entities[0])

	return qa

def _apply_money_filter(qa, age_entities, request, responder):
	"""
	This function is used to filter any salary related queries, that may include a 
	comparator, such as, 'what percentage earns less than 20 dollars an hour? ' or an extreme,
	such as, 'highest earning employee'. 
	"""

	num_entity = [float(e['value'][0]['value']) for e in request.entities if e['type'] in ('sys_number', 'sys_amount-of-money')]

	try:
		comparator_entity = [e for e in request.entities if e['type'] == 'comparator'][0]
	except:
		comparator_entity = []


	try:
		extreme_entity = [e for e in request.entities if e['type'] == 'extreme'][0]
	except:
		extreme_entity = []

	# The money entity can have either be accompanied by a comparator, extreme or no entity. 
	# These are mutually exclusive of others and hence can only be queried separately from
	# the knowledge base.

	if comparator_entity:
		comparator_canonical = comparator_entity['value'][0]['cname']

		if comparator_canonical == 'more than' and len(num_entity)==1:
			gte_val = num_entity[0]
			lte_val = 1000 # Default value since it is much above the hourly salary limit

		elif comparator_canonical == 'less than' and len(num_entity)==1:
			lte_val = num_entity[0]
			gte_val = 0

		elif comparator_canonical == 'equals to':
			gte_val = num_entity[0]
			lte_val = num_entity[0]

		elif len(num_entity)>1:
			gte_val = np.min(num_entity)
			lte_val = np.max(num_entity)


		# Apply filter iff numerical entity exists
		try:		
			qa = qa.filter(field='money', gte=gte_val, lte=lte_val)
		except:
			pass
		size = 300


	elif extreme_entity:
		qa, size = _resolve_extremes(request, responder, qa, extreme_entity, 'money', num_entity)

	elif len(num_entity)>=1:
		qa = qa.filter(field='money', gte=np.min(num_entity), lte=np.max(num_entity))
		size = 300

	else:
		size = 300

	return qa, size


def _get_interval_amount(recur_ent, money):
	"""
	Get the Salary Amount Based on a Recurring Period of Time
	param recur_ent (str): 'yearly', 'monthly', 'weely', 'daily', 'hourly'
	param money (float): Hourly Salary of an employee
	"""

	intv_mult = { "yearly": 12*4*5*8, "monthly": 4*5*8, "weekly":5*8, "daily": 8,"hourly": 1}
	return round(intv_mult[recur_ent] * money, 2)         


def _calculate_agg_salary(responder, qa_out, function, recur_ent='hourly'):
	"""
	Calculate Salary by first fetching it from the knowledge base and then
	multiplying by the appropriate time factor that the user is seeking
	"""

	value = _agg_function(qa_out, func=function, num_col='money')

	if recur_ent:
		value = _get_interval_amount(recur_ent, value)
		responder.slots['interval'] = recur_ent
		
	responder.slots['value'] = value

	return responder


def _get_names(qa_out):
	"""
	Get a List of Names from a QA Result
	param qa_out (list) Output of QA from a query
	"""

	names = [str(out['first_name']) + ' ' + str(out['last_name']) + ": " + str(out['money']) for out in qa_out]
	names = ', '.join(names)
	return names
