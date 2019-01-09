# -*- coding: utf-8 -*-
"""This module contains a template Workbench application"""
from mmworkbench import Application
import template.custom_features

app = Application(__name__)

__all__ = ['app']


@app.handle(default=True)
def default(context, responder):
    """This is a default handler."""
    responder.reply('Hello there!')
