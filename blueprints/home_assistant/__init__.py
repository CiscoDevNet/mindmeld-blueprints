# -*- coding: utf-8 -*-
"""This module contains the MindMeld home assistant blueprint application"""
from home_assistant.root import app

import home_assistant.greeting
import home_assistant.smart_home
import home_assistant.times_and_dates
import home_assistant.unknown
import home_assistant.weather  # noqa: ignore=F401

__all__ = ['app']
