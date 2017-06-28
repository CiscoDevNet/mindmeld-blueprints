# -*- coding: utf-8 -*-
"""This module contains the Workbench video discovery blueprint application"""
from __future__ import unicode_literals
from mmworkbench import Application

app = Application(__name__)


@app.handle(intent='greet')
def welcome(context, slots, responder):
    """
    When the user starts a conversation, say hi.
    """
    responder.reply("greet placeholder.")


@app.handle(intent='browse')
def show_content(context, slots, responder):
    # Show the video content based on the entities found.
    responder.reply("browse placeholder.")


@app.handle(intent='start_over')
def start_over(context, slots, responder):
    """
    When the user wants to start over, clear the dialogue frame and prompt for the next request.
    """
    responder.reply("start_over placeholder.")


@app.handle(intent='exit')
def say_goodbye(context, slots, responder):
    """
    When the user ends a conversation, clear the dialogue frame and say goodbye.
    """
    responder.reply("exit placeholder.")


@app.handle(intent='help')
def provide_help(context, slots, responder):
    """
    When the user asks for help, provide some sample queries they can try.
    """
    responder.reply("help placeholder.")


@app.handle(intent='unsupported')
def handle_unsupported(context, slots, responder):
    # Respond with a message explaining the app does not support that # query.
    responder.reply("unsupported placeholder.")


@app.handle(intent='unrelated')
def handle_unrelated(context, slots, responder):
    # Respond with a message explaining the app does not support that # query.
    responder.reply("unrelated placeholder.")


@app.handle(intent='compliment')
def say_something_nice(context, slots, responder):
    # Respond with a compliment or something nice.
    responder.reply("compliment placeholder.")


@app.handle(intent='insult')
def handle_insult(context, slots, responder):
    # Evade the insult and come back to the app usage.
    responder.reply("insult placeholder.")


@app.handle()
def default(context, slots, responder):
    """
    When the user asks an unrelated question, convey the lack of understanding for the requested
    information and prompt to return to video discovery.
    """
    responder.reply("default placeholder.")


if __name__ == '__main__':
    app.cli()
