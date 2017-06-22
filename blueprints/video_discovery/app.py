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
    try:
        # Get user's name from session information in request context to personalize the greeting.
        slots['name'] = context['request']['session']['name']
        prefix = 'Hello, {name}. '
    except KeyError:
        prefix = 'Hello. '

    # Build up the final natural language response and reply to the user.
    responder.prompt(prefix + 'How are you doing? Want to watch some movies?')


@app.handle(intent='exit')
def say_goodbye(context, slots, responder):
    """
    When the user ends a conversation, clear the dialogue frame and say goodbye.
    """
    # Clear the dialogue frame to start afresh for the next user request.
    context['frame'] = {}

    # Respond with a random selection from one of the canned "goodbye" responses.
    responder.reply(['Bye!', 'Goodbye!', 'Have a nice day.', 'See you later.'])


@app.handle(intent='help')
def provide_help(context, slots, responder):
    """
    When the user asks for help, provide some sample queries they can try.
    """
    # Respond with examples demonstrating how the user can search for movies.
    # For simplicity, we have a fixed set of demonstrative queries here, but they could also be
    # randomly sampled from a pool of example queries each time.
    prompts = ["I can help you find movies that you might be interested. For example, "
               "you can say 'I would like some comedy movies' or 'I feel like "
               "to watch movies with Tom Hanks.'"]
    responder.prompt(prompts)


@app.handle(intent='start_over')
def start_over(context, slots, responder):
    """
    When the user wants to start over, clear the dialogue frame and prompt for the next request.
    """
    # Clear the dialogue frame and respond with a variation of the welcome message.
    context['frame'] = {}
    prompts = ["Ok, let's start over! What movies do you want to watch?"]
    responder.prompt(prompts)


@app.handle(intent='unsupported')
@app.handle()
def default(context, slots, responder):
    """
    When the user asks an unrelated question, convey the lack of understanding for the requested
    information and prompt to return to video discovery.
    """
    prompts = ['Sorry, not sure what you meant there. I can help you find some good movies.']
    responder.prompt(prompts)


if __name__ == '__main__':
    app.cli()
