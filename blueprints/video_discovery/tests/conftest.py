import os

from mmworkbench import NaturalLanguageProcessor, Conversation
import pytest


APP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(scope='session')
def nlp():
    the_nlp = NaturalLanguageProcessor(APP_PATH)
    the_nlp.load()
    return the_nlp


@pytest.fixture
def convo(nlp):
    the_convo = Conversation(nlp=nlp, app_path=APP_PATH)
    return the_convo
