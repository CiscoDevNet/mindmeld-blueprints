#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pytest


def test_greet(convo):
    convo.process('hi')
    convo.assert_domain('video_content')
    convo.assert_intent('greet')


def test_ask_content_single(convo):
    # TODO: complete the flow from doc
    convo.process('Can I see some movies with Tom Hanks?')
    convo.assert_domain('video_content')
    convo.assert_intent('browse')


def test_ask_content_multiple(convo):
    # TODO: complete the flow from doc
    convo.process('Can I see some movies with Tom Hanks?')
    convo.assert_domain('video_content')
    convo.assert_intent('browse')

    # TODO: hook up with context
    convo.process('Which ones were released in 2004?')
    convo.assert_domain('video_content')
    convo.assert_intent('browse')


def test_start_over(convo):
    # TODO: complete the flow from doc
    convo.process('start over')
    convo.assert_domain('video_content')
    convo.assert_intent('start_over')


def test_exit(convo):
    # TODO: complete the flow from doc
    convo.process('bye')
    convo.assert_domain('video_content')
    convo.assert_intent('exit')


def test_help(convo):
    convo.process('help me please')
    convo.assert_domain('video_content')
    convo.assert_intent('help')


def test_epg_time(convo):
    convo.process('What time is The Big Bang Theory on?')
    convo.assert_domain('video_content')
    convo.assert_intent('unsupported')


def test_epg_channel(convo):
    convo.process('What channel is Games of Thrones on?')
    convo.assert_domain('video_content')
    convo.assert_intent('unsupported')


def test_insults(convo):
    convo.process('You suck.')
    convo.assert_domain('unrelated')
    convo.assert_intent('insult')


def test_compliments(convo):
    convo.process('You are great!')
    convo.assert_domain('unrelated')
    convo.assert_intent('compliment')


@pytest.mark.skip(reason='Not implemented yet.')
def test_unrelated_general(convo):
    convo.process('Get me a big mac')
    convo.assert_domain('unrelated')
    convo.assert_intent('insult')
