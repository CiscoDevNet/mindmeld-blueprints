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
    'params': {
        'penalty': 'l2',
        'C': 10000
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
        'C': 1000000,
        "class_bias": 1
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
