#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from mmworkbench.components import Conversation

from conversation_test import ConversationTest

APP_PATH = '../..'


class TestFrame(ConversationTest):
    @pytest.mark.frame
    def test_action_movie(self):
        convo = Conversation(app_path=APP_PATH)
        convo.say('action movies')
        expected = {
            'type': [{'type': 'type', 'text': 'movies'}],
            'genre': [{'type': 'genre', 'text': 'action'}]
        }
        self.assert_frame(convo, expected)
