#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning,
                        module="sklearn.preprocessing.label")


def test_greet(convo):
    convo.process('hi')
    convo.assert_domain('video_content')
    convo.assert_intent('greet')


def test_ask_content_single(convo):
    convo.process('Can I see some movies with Tom Hanks?')
    convo.assert_domain('video_content')
    convo.assert_intent('browse')


@pytest.mark.skip(reason='Accuracy instability')
def test_ask_content_multiple(convo):
    convo.process('Can I see some movies with Tom Hanks?')
    convo.assert_domain('video_content')
    convo.assert_intent('browse')

    # TODO: hook up with context
    convo.process('The ones in 2004?')
    convo.assert_domain('video_content')
    convo.assert_intent('browse')


def test_start_over(convo):
    convo.process('start over')
    convo.assert_domain('video_content')
    convo.assert_intent('start_over')


def test_exit(convo):
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
