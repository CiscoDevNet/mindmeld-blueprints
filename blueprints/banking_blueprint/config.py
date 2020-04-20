# -*- coding: utf-8 -*-
"""This module contains a template MindMeld app configuration"""

# The namespace of the application. Used to prevent collisions in supporting services across
# applications. If not set here, the app's enclosing directory name is used.
# APP_NAMESPACE = 'app-name'

# Dictionaries for the various NLP classifier configurations

# An example decision tree model for intent classification
INTENT_CLASSIFIER_CONFIG = {
    'model_type': 'text',
    'model_settings': {
        'classifier_type': 'logreg'
    },
    'param_selection': {
        'type': 'k-fold',
        'k': 5,
        'grid': {
            'fit_intercept': [True, False],
            'C': [0.01, 1, 10, 100],
            'class_bias': [0.7, 0.3, 0]
        },
    },
    "features": {
        "bag-of-words": {
            "lengths":[1,2]
        },
        "edge-ngrams" : {"lengths": [1,2]},
        "in-gaz": {},
        "exact": {"scaling": 10},
        "gaz-freq": {},
        "freq": {"bins":5}
    }
}

"""
# Fill in the other model configurations if necessary
# DOMAIN_CLASSIFIER_CONFIG = {}
# ENTITY_RECOGNIZER_CONFIG = {}
# ROLE_CLASSIFIER_CONFIG = {}
"""

# A example configuration for the parser
"""
# *** Note: these are place holder entity types ***
PARSER_CONFIG = {
    'grandparent': {
        'parent': {},
        'child': {'max_instances': 1}
    },
    'parent': {
        'child': {'max_instances': 1}
    }
}
"""
