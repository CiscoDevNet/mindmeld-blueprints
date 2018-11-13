# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'unknown' domain in
the home assistant blueprint application
"""
from .app import app


@app.handle(intent='unknown')
def unknown(context, responder):
    replies = ["Sorry, not sure what you meant there."]
    responder.reply(replies)
