# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'greeting' domain
in the Workbench home assistant blueprint application
"""
from .app import app


@app.handle(intent='greet')
def greet(context, responder):
    responder.reply('Hi, I am your home assistant. I can help you to check weather, set temperature'
                    ' and control the lights and other appliances.')


@app.handle(intent='exit')
def exit(context, responder):
    responder.reply('Bye!')
