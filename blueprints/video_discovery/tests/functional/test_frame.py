#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

pytestmark = pytest.mark.frame


def test_action_movie(convo):
    convo.say('action movies')
    expected = {
        'type': [{'type': 'type', 'text': 'movies', 'cname': 'movie'}],
        'genre': [{'type': 'genre', 'text': 'action', 'cname': 'Action'}]
    }
    convo.assert_frame(expected)


def test_comedy_tv(convo):
    convo.say('i want to watch a funny show')
    expected = {
        'type': [{'type': 'type', 'text': 'show', 'cname': 'tv-show'}],
        'genre': [{'type': 'genre', 'text': 'funny', 'cname': 'Comedy'}]
    }
    convo.assert_frame(expected)


def test_jennifer_aniston_movie(convo):
    convo.say('i want to watch a movie starring Jennifer Aniston')
    expected = {
        'type': [{'type': 'type', 'text': 'movie', 'cname': 'movie'}],
        'cast': [{'type': 'cast', 'text': 'Jennifer Aniston', 'cname': None}]
    }
    convo.assert_frame(expected)


def test_canadian_movie(convo):
    convo.say('i want to watch a Canadian movie')
    expected = {
        'type': [{'type': 'type', 'text': 'movie', 'cname': 'movie'}],
        # 'country': [{'type': 'country', 'text': 'Canadian'}]
    }
    convo.assert_frame(expected)


def test_best_action_movie(convo):
    convo.say('best action movies at 2002')
    expected = {
        'genre': [{'cname': 'Action', 'text': 'action', 'type': 'genre'}],
        'sort': [{'cname': 'popular', 'text': 'best', 'type': 'sort'}],
        'sys_time': [{
            'cname': None, 'text': '2002', 'type': 'sys_time',
            'value': {'grain': 'year', 'value': '2002-01-01T00:00:00.000-07:00'}
        }],
        'type': [{'cname': 'movie', 'text': 'movies', 'type': 'type'}]
    }
    convo.assert_frame(expected)


def test_tv_range(convo):
    convo.say('tv shows from the 90s')
    expected = {
        'sys_interval': [{'cname': None,
                          'text': '90s',
                          'type': 'sys_interval',
                          'value': {'grain': 'year',
                                    'value': ['1990-01-01T00:00:00.000-07:00',
                                              '2000-01-01T00:00:00.000-07:00']}}],
        'type': [{'cname': 'tv-show', 'text': 'tv shows', 'type': 'type'}]
    }
    convo.assert_frame(expected)
