# -*- coding: utf-8 -*-
"""This module contains the MindMeld HR assistant blueprint application"""

from hr_assistant.root import app

import hr_assistant.date
import hr_assistant.general
import hr_assistant.greeting
import hr_assistant.hierarchy
import hr_assistant.salary
import hr_assistant.helpers
import hr_assistant.unsupported
import hr_assistant.faq # noqa F401
import hr_assistant.unsupported  # noqa F401

__all__ = ['app']
