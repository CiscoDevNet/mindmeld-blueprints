# -*- coding: utf-8 -*-
"""This module contains the Video Discovery Blueprint Application"""

PARSER_CONFIG = {
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

APP_NAME = 'video_discovery'
