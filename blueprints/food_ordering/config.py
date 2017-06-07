# -*- coding: utf-8 -*-
"""This module contains the Food Ordering Blueprint Application"""

PARSER_CONFIG = {
    'dish': {
        'option': {'linking_words': {'with'}},
        'sys_number': {'max_instances': 1, 'right': False}
    },
    'option': {
        'sys_number': {'max_instances': 1, 'right': False}
    }
}

CLASSIFIER_CONFIGS = {
}

APP_NAME = 'food_ordering'
