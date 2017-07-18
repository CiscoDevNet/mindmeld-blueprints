# -*- coding: utf-8 -*-
"""This module contains the a template Workbench application"""
from __future__ import unicode_literals
from mmworkbench import Application

app = Application(__name__)


@app.handle()
def default(context, slots, responder):
    """
    This is a default handler
    """
    responder.reply('Hello there!')


if __name__ == '__main__':
    app.cli()
