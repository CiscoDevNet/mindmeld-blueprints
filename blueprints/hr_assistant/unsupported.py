# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'unsupported' domain in
the MindMeld HR assistant blueprint application
"""

from .root import app
import random


@app.handle(intent='unsupported')
def unsupported(request, responder):
    query = random.choice(["Males fired in 2014.", "Show me all married employees.",
                           "What is the average salary for women?",
                           "Please tell me the average salary for employees.",
                           "What percentage of employees were born post 1970?",
                           "Is there anyone older than 67 of age?", "What does Ivan make?",
                           "Is John's salary more than 6k?", "Is Mia married?",
                           "Give me the youngest five percent of employees."])

    responder.slots['query'] = query
    responder.reply("Hmmm, I don't quite understand, you can ask me something like '{query}'")
    responder.listen()
