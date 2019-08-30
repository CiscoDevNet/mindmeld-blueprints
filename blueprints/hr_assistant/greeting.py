# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'greeting' domain in
the MindMeld HR assistant blueprint application
"""

from .root import app


@app.handle(intent='greet')
def greet(request, responder):
    responder.reply("Hi, I am your HR assistant. Ask me about an individual "
                    "employee, company's employee demographic or "
                    "general policy questions. You can say 'Is Mia married?' or "
                    "'Average salary of females' or 'When will I get my W2?'")


@app.handle(intent='exit')
def exit(request, responder):
    responder.reply('Alright, goodbye!')
