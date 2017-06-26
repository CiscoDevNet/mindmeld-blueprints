#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os

import click
import click_log

from mmworkbench import NaturalLanguageProcessor


DOMAIN_MODEL_CONFIG = {}

INTENT_MODEL_CONFIG = {
    'model_type': 'text',
    'model_settings': {
        'classifier_type': 'logreg'
    },
    'params': {
        'C': 1000000000
    },
    'features': {
        'exact': {},
    }
}

ENTITY_MODEL_CONFIG = {
    'model_type': 'memm',
    'model_settings': {
        'tag_scheme': 'IOB',
        'feature_scaler': 'none'
    },
    'params': {
        'penalty': 'l2',
        'C': 100
    },
    'features': {
        'bag-of-words-seq': {
            'ngram_lengths_to_start_positions': {
                '1': [-2, -1, 0, 1],
                '2': [-2, -1, 0, 1]
            }
        },
        'in-gaz-span-seq': {},
        'sys-candidates-seq': {
            'start_positions': [0]
        }
    }
}


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click_log.simple_verbosity_option()
@click_log.init('mmworkbench')
@click.option('-t', '--train-type', help='type of model to train',
              type=click.Choice(('domain', 'intent', 'entity')), multiple=True)
@click.option('-d', '--domain', help='domain to train for', multiple=True)
@click.option('-i', '--intent', help='intent to train for', multiple=True)
def cli(train_type, domain, intent):
    """Trains the models for delorean"""
    train_types = tuple(train_type) if len(train_type) else ('domain',
                                                             'intent',
                                                             'entity')
    domains = tuple(domain) if len(domain) else None
    intents = tuple(intent) if len(intent) else None
    train(train_types, domains, intents)



def train(train_types, domains, intents):
    """Trains the models for delorean"""
    app_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    nlp = NaturalLanguageProcessor(app_path)

    if 'domain' in train_types:
        train_domain_clf(nlp)
    if 'intent' in train_types:
        train_intent_clf(nlp, domains)
    if 'entity' in train_types:
        train_entity_rec(nlp, domains, intents)

    # save all the models that were trained
    nlp.dump()


def train_domain_clf(nlp):
    """Trains the domain classifier"""
    if len(nlp.domains) > 1:
        nlp.domain_classifier.fit(**DOMAIN_MODEL_CONFIG)


def train_intent_clf(nlp, domains=None):
    """Trains the intent classifiers"""
    all_domains = set(nlp.domains.keys())
    if domains:
        domains = set(domains).intersection(all_domains)
    else:
        domains = all_domains

    for domain in domains:
        domain_processor = nlp.domains[domain]
        if len(domain_processor.intents) > 1:
            domain_processor.intent_classifier.fit(**INTENT_MODEL_CONFIG)


def train_entity_rec(nlp, domains=None, intents=None):
    """Trains the entity recognizers"""
    all_domains = set(nlp.domains.keys())
    if domains:
        domains = set(domains).intersection(set(all_domains))
    else:
        domains = all_domains

    for domain in domains:
        domain_processor = nlp.domains[domain]
        all_domain_intents = set(domain_processor.intents.keys())
        if intents:
            domain_intents = set(intents).intersection(all_domain_intents)
        else:
            domain_intents = all_domain_intents

        for intent in domain_intents:
            intent_processor = domain_processor.intents[intent]
            intent_processor.entity_recognizer.fit(**ENTITY_MODEL_CONFIG)


if __name__ == '__main__':
    cli()
