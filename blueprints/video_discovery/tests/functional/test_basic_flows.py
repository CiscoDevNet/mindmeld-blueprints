#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pytest
from conversation_test import ConversationTest

from mmworkbench import NaturalLanguageProcessor

# Load the app
app_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))[:-6]  # Remove tests dir
nlp = NaturalLanguageProcessor(app_path)
nlp.load()


class TestBasicFlows(ConversationTest):
    def test_greet(self):
        response = nlp.process('hi')
        self.assert_domain(response, 'video_content')
        self.assert_intent(response, 'greet')

    def test_ask_content_single(self):
        # TODO: complete the flow from doc
        response = nlp.process('Can I see some movies with Tom Hanks?')
        self.assert_domain(response, 'video_content')
        self.assert_intent(response, 'browse')

    def test_ask_content_multiple(self):
        # TODO: complete the flow from doc
        response = nlp.process('Can I see some movies with Tom Hanks?')
        self.assert_domain(response, 'video_content')
        self.assert_intent(response, 'browse')

        # TODO: hook up with context
        response = nlp.process('Which ones were released in 2004?')
        self.assert_domain(response, 'video_content')
        self.assert_intent(response, 'browse')

    def test_start_over(self):
        # TODO: complete the flow from doc
        response = nlp.process('start over')
        self.assert_domain(response, 'video_content')
        self.assert_intent(response, 'start_over')

    def test_exit(self):
        # TODO: complete the flow from doc
        response = nlp.process('bye')
        self.assert_domain(response, 'video_content')
        self.assert_intent(response, 'exit')

    def test_help(self):
        response = nlp.process('help me please')
        self.assert_domain(response, 'video_content')
        self.assert_intent(response, 'help')

    def test_epg_time(self):
        response = nlp.process('What time is The Big Bang Theory on?')
        self.assert_domain(response, 'video_content')
        self.assert_intent(response, 'unsupported')

    def test_epg_channel(self):
        response = nlp.process('What channel is Games of Thrones on?')
        self.assert_domain(response, 'video_content')
        self.assert_intent(response, 'unsupported')

    def test_insults(self):
        response = nlp.process('You suck.')
        self.assert_domain(response, 'unrelated')
        self.assert_intent(response, 'insult')

    def test_compliments(self):
        response = nlp.process('You are great!')
        self.assert_domain(response, 'unrelated')
        self.assert_intent(response, 'compliment')

    @pytest.mark.skip(reason='Not implemented yet.')
    def test_unrelated_general(self):
        response = nlp.process('Get me a big mac')
        self.assert_domain(response, 'unrelated')
        self.assert_intent(response, 'insult')
