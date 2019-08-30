import os

from mindmeld import NaturalLanguageProcessor
from mindmeld.exceptions import ClassifierLoadError
from mindmeld.test import TestConversation
from mindmeld.path import get_app
import pytest
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning,
                        module="sklearn.preprocessing.label")


APP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(scope='session')
def nlp():
    the_nlp = NaturalLanguageProcessor(APP_PATH)
    try:
        the_nlp.load()
    except ClassifierLoadError as exc:
        raise ClassifierLoadError(
            "Could not load app. Have you built the models? "
            "Run 'python -m {} build' to do so.".format(os.path.split(APP_PATH[1]))
        ) from exc
    return the_nlp


@pytest.fixture(scope='session')
def app(nlp):
    the_app = get_app(APP_PATH)
    the_app.lazy_init(nlp)
    return the_app


@pytest.fixture
def convo(app):
    the_convo = TestConversation(app=app)
    return the_convo
