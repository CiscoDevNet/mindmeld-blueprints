# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'unknown' domain in
the home assistant blueprint application
"""
from .root import app


@app.handle(intent='unknown')
def unknown(request, responder):
    replies = ["Sorry, not sure what you meant there."]
    responder.reply(replies)
