# -*- coding: utf-8 -*-
"""This module contains the Food Ordering Blueprint Application"""

PARSER_CONFIG = {
    'dish': {
        'option': {'linking_words': {'with'}},
        'quantity': {'max_instances': 1, 'right': False}
    },
    'option': {
        'quantity': {'max_instances': 1, 'right': False}
    }
}

CLASSIFIER_CONFIGS = {
}
