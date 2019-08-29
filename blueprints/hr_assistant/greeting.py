# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'greeting' domain in
the MindMeld HR assistant blueprint application
"""

from .root import app


@app.handle(intent='greet')
def greet(request, responder):
    responder.reply("Hi, I am your HR assistant. You can ask me about "
                    "an employee's individual information (eg. Is Mia married?), "
                    "some employee statistic (eg. average salary of females) or "
                    "names of employees according to your criteria"
                    "(eg. give me a list of all married employees) or "
                    "general policy questions")


@app.handle(intent='exit')
def exit(request, responder):
    responder.reply('Alright, goodbye!')
