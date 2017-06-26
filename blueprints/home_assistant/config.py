# -*- coding: utf-8 -*-
"""This module contains the Home Assistant Blueprint Application"""

PARSER_CONFIG = {
    'dish': {
        'option': {'linking_words': {'with'}},
        'sys_number': {'max_instances': 1, 'right': False}
    },
    'option': {
        'sys_number': {'max_instances': 1, 'right': False}
    }
}

INTENT_MODEL_CONFIG = {
    'model_type': 'text',
    'model_settings': {
        'classifier_type': 'logreg'
    },
    'params': {
        'C': 10,
        "class_bias": 0.3
    },
    'features': {
        "bag-of-words": {
            "lengths": [1, 2]
        },
        "edge-ngrams": {"lengths": [1, 2]},
        "in-gaz": {},
        "exact": {"scaling": 10},
        "gaz-freq": {},
        "freq": {"bins": 5}
    }
}

DOMAIN_MODEL_CONFIG = {
    'model_type': 'text',
    'model_settings': {
        'classifier_type': 'logreg'
    },
    'params': {
        'C': 10,
    },
    'features': {
        "bag-of-words": {
            "lengths": [1, 2]
        },
        "edge-ngrams": {"lengths": [1, 2]},
        "in-gaz": {},
        "exact": {"scaling": 10},
        "gaz-freq": {},
        "freq": {"bins": 5}
    }
}

APP_NAME = 'home_assistant'
