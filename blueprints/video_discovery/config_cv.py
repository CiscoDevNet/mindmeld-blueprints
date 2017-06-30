# -*- coding: utf-8 -*-
"""This module contains the Video Discovery Blueprint Application"""

PARSER_CONFIG = {
}

ENTITY_MODEL_CONFIG = {
    'model_type': 'memm',
    'model_settings': {
        'tag_scheme': 'IOB',
        'feature_scaler': 'max-abs'
    },
    'param_selection': {
        'type': 'k-fold',
        'k': 10,
        'scoring': 'accuracy',
        'grid': {
            'penalty': ['l1', 'l2'],
            'C': [0.01, 1, 100, 10000, 1000000, 100000000]
        },
    },
    'features': {
        'bag-of-words-seq': {
            'ngram_lengths_to_start_positions': {
                1: [-2, -1, 0, 1, 2],
                2: [-2, -1, 0, 1]
            }
        },
        'in-gaz-span-seq': {},
        'sys-candidates-seq': {
            'start_positions': [-1, 0, 1]
        }
    }
}

INTENT_MODEL_CONFIG = {
    'model_type': 'text',
    'model_settings': {
        'classifier_type': 'logreg'
    },
    'param_selection': {
        'type': 'k-fold',
        'k': 10,
        'grid': {
            'penalty': ['l1', 'l2'],
            'class_bias': [0, 0.5, 1],
            'C': [0.01, 1, 100, 10000, 1000000, 100000000]
        },
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
    'param_selection': {
        'type': 'k-fold',
        'k': 10,
        'grid': {
            'penalty': ['l1', 'l2'],
            'class_bias': [0, 0.5, 1],
            'C': [0.01, 1, 100, 10000, 1000000, 100000000]
        },
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
