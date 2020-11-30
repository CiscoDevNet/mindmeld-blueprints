# -*- coding: utf-8 -*-
"""
This module contains the dialogue states for the greetings domain
"""
from .root import app

import screening_app.prediabetes as pd
from screening_app.screening import screen_prediabetes

@app.handle(default=True)
@app.handle(intent='greet')
def welcome(request, responder):
    """
    When the user begins the conversation with a greeting. Explain the system options.
    """
    responder.reply(pd.WELCOME_MSG)


@app.handle(intent='exit')
@screen_prediabetes.handle(intent='exit')
def say_goodbye(request, responder):
    """
    When the user ends a conversation, clear the dialogue frame and say goodbye.
    """
    # Clear the dialogue frame to start afresh for the next user request.
    responder.frame = {}

    # Respond with a random selection from one of the canned "goodbye" responses.
    responder.reply(['Gracias por su visita. ¡Adios!',
                     'Gracias por su visita. ¡Hasta luego!',
                     'Gracias por su visita. Que tenga buen día.'])

    responder.exit_flow()
