# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'greeting' domain
in the MindMeld home assistant blueprint application
"""
from .root import app


@app.handle(intent='greet')
def greet(request, responder):
    responder.reply('Hi, I am your home assistant. I can help you to check weather, set temperature'
                    ' and control the lights and other appliances.')


@app.handle(intent='exit')
def exit(request, responder):
    responder.reply('Bye!')
