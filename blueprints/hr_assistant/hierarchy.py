# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'salary' domain in 
the MindMeld HR assistant blueprint application
"""
from .root import app
from hr_assistant.general import _resolve_categorical_entities, _resolve_function_entity, _resolve_extremes, _agg_function, _get_names, _get_person_info, _fetch_from_kb



@app.handle(intent='get_hierarchy_up')
def get_hierarchy_up(request, responder):
	"""
	If a user asks about any employees manager or whether they are some other employee's 
	manager, this function captures all the names in the query and returns the employee-manager
	mapping for each one of them.
	"""

	try:
		name_ent = [e['value'][0]['cname'] for e in request.entities if e['type'] == 'name']

		# if no name, shift to exception flow
		name_ent[0]

		for name in name_ent:
			responder = _fetch_from_kb(responder, name, 'manager')
			reply = ["{manager} is {name}'s manager"]
			responder.reply(reply)

	except:
		responder.reply("Who's manager would you like to know? (You can try saying 'Mia's manager')")


@app.handle(intent='get_hierarchy_down')
def get_hierarchy_down(request, responder):
	"""
	If a user asks about any employees subordinates or who reports to them, 
	this function fetches that info from the KB.
	"""

	try:
		name_ent = [e['value'][0]['cname'] for e in request.entities if e['type'] == 'name']

		# if no name, shift to exception flow
		name_ent[0]

		for name in name_ent:
			responder = _fetch_from_kb(responder, name, 'subordinates')
			if len(responder.slots['subordinates'])==0:
				responder.reply("{name} has no subordinates")
				return
			reply = ["The following people work under {name}: {subordinates}"]
			responder.reply(reply)

	except:
		responder.reply("Who's subordinates would you like to know? (You can try saying 'which employees report to Mia?')")