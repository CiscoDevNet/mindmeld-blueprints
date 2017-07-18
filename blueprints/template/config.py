# -*- coding: utf-8 -*-
"""This module contains a template Workbench app configuration"""

# The name of the application if it should be different from the app's enclosing directory name
# APP_NAME = 'app-name'

# A dict containing the configuration for the various NLP classifiers.
"""
CLASSIFIER_CONFIGS = {
    'intent': { # An example decision tree model
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
    }
}
"""

# A example configuration for the parser
"""
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
