# -*- coding: utf-8 -*-
"""This module contains a template Workbench app configuration"""

# The name of the application if it should be different from the app's enclosing directory name
# APP_NAME = 'app-name'

# Dictionaries for the various NLP classifier configurations
"""

# An example decision tree model for intent classification
INTENT_MODEL_CONFIG = {
    'model_type': 'text',
    'model_settings: {
        'classifier_type': 'dtree'
    },
    'param_selection': {
        'type': 'k-fold',
        'k': 10,
        'grid': {
            'max_features': ['log2', 'sqrt', 0.01, 0.1]
        },
    },
    "features": {
        "exact": {}
    }
}

# Fill in the other model configurations if necessary
# DOMAIN_MODEL_CONFIG = {}
# ENTITY_MODEL_CONFIG = {}
# ROLE_MODEL_CONFIG = {}
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
