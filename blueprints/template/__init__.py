# -*- coding: utf-8 -*-
"""This module contains a template Workbench application"""
from mindmeld import Application

app = Application(__name__)

__all__ = ['app']


@app.handle(default=True)
def default(request, responder):
    """This is a default handler."""
    responder.reply('Hello there!')
