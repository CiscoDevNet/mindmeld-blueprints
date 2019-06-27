# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'unsupported' domain in 
the MindMeld HR assistant blueprint application
"""

from .root import app
from hr_assistant.general import _resolve_categorical_entities, _resolve_function_entity, _resolve_extremes, _agg_function, _get_names, _get_person_info, _fetch_from_kb
import re
import random



@app.handle(intent='unsupported')
def unsupported(request, responder):
	query = random.choice(["males fired in 2014", "show me all married employees", "what is the average salary for women?", "Please tell me the average salary for employees", "What percentage of employees were born post 1970", "is there anyone older than 67 of age", "is john's salary more than 6k", "is Mia married?", "what does Ivan make?", "give me the youngest five percent of employees"])
	responder.slots['query'] = query
	responder.reply("Hmmm, I don't quite understand, you can ask me something like '{query}'")
	responder.listen()