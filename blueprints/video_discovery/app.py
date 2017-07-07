# -*- coding: utf-8 -*-
"""This module contains the Workbench video discovery blueprint application"""
from __future__ import unicode_literals
import datetime
import logging
import random

from mmworkbench import Application
from mmworkbench.components._elasticsearch_helpers import get_scoped_index_name


app = Application(__name__)


APP_NAME = 'video_discovery'
KB_INDEX_NAME = '20170706'

GENERAL_PROMPTS = ['I can help you find movies and tv shows. What do you feel like watching today?',
                   'Tell me what you would like to watch today.',
                   'Talk to me to browse movies and tv shows.']

GENERAL_SUGGESTIONS = [{'text': 'Most popular', 'type': 'text'},
                       {'text': 'Most recent', 'type': 'text'},
                       {'text': 'Movies', 'type': 'text'},
                       {'text': 'TV Shows', 'type': 'text'},
                       {'text': 'Action', 'type': 'text'},
                       {'text': 'Dramas', 'type': 'text'},
                       {'text': 'Sci-Fi', 'type': 'text'}]

# A hack to convert Mallard value to str
# Convert from mallard format like '2002-01-01T00:00:00.000-07:00'
MALLARD_YEAR_INDEX = 10


@app.handle(intent='greet')
def welcome(context, slots, responder):
    """
    When the user starts a conversation, say hi.
    """
    greetings = ['Hello', 'Hi', 'Hey']
    try:
        # Get user's name from session information in request context to personalize the greeting.
        slots['name'] = context['request']['session']['name']
        greetings = [greeting + ', {name}.' for greeting in greetings] + \
            [greeting + ', {name}!' for greeting in greetings]
    except KeyError:
        greetings = [greeting + '.' for greeting in greetings] + \
            [greeting + '!' for greeting in greetings]

    responder.reply(greetings)

    responder.prompt(GENERAL_PROMPTS)

    # Get default videos
    responder.respond(get_default_videos_action())
    responder.suggest(GENERAL_SUGGESTIONS)


@app.handle(intent='browse')
def show_content(context, slots, responder):
    # Show the video content based on the entities found.

    results = []

    # 1) Update the frame with the new entities extracted.
    # TODO: Update frame logic here.
    context['frame'] = update_frame(context['entities'], context['frame'])

    # 2) Call the KB filtering by the entities in the frame
    # TODO: Get results from the knowledgebase using all entities in frame as filters.
    results = get_video_content(context['frame'])

    # 3.1) Fill reply slots.
    # TODO: Fill the slots with the frame.
    slots = fill_browse_slots(context['frame'], slots)

    # 3.2) Build response based on available slots and results.
    # TODO: Have a set of response templates, and select one based on the slots.
    # Finally reply to the user, including the results and any prompts.
    reply, videos_client_action, prompt = build_browse_response(context, slots, results)

    # Send the reply
    responder.reply(reply)

    # Build and return the client action
    videos_client_action = video_results_to_action(results)
    responder.respond(videos_client_action)


def update_frame(entities, frame):
    """
    Update the entities in the frame with the new entities in the 'entities' dict.
    For now, I think we should accumulate all entities.
    That is, if we already have a 'title' and we receive another one, keep both in the frame.

    Args:
        entities (list of dict): current entities
        frame (dict): current frame
    Returns:
        dict: updated frame
    """
    for entity in entities:
        entity_type = entity.get('type', '')
        existing_entities = frame.get(entity_type, [])
        entity_values = entity.get('value', [])
        cname = None
        if entity_values:
            cname = entity_values[0].get('cname', None)
        new_entity = {
            'type': entity_type,
            'text': entity.get('text', ''),
            'cname': cname
        }
        if entity_type in {'sys_time', 'sys_interval'}:
            new_entity['value'] = entity_values[0]
        existing_entities.append(new_entity)

        frame[entity_type] = existing_entities
    return frame


ENTITY_TO_FIELD = {
    'type': 'doc_type',
    'genre': 'genres',
    'director': 'directors',
    'country': 'countries',
}


def get_video_content(frame):
    # TODO: Using all entities in the frame, get docs from ES. If we have multiple entities of the
    # same type, decide if we want to 'or' or 'and' them together. This might depend on entity type.

    index_name = get_scoped_index_name(APP_NAME, KB_INDEX_NAME)
    search = app.question_answerer.build_search(index_name, {'query_clauses_operator': 'and'})

    search_entities = {'title'}
    filter_entities = {'cast', 'director', 'genre', 'type', 'country'}

    for entity in get_next_entity(frame, search_entities):
        search = search.query(**entity)

    for entity in get_next_entity(frame, filter_entities):
        search = search.filter(**entity)

    # Sort entity
    sort_entities = {
        'latest': ('release_date', 'desc'),
        'oldest': ('release_date', 'asc'),
        'popular': ('popularity', 'desc'),
        'worst': ('popularity', 'asc'),
    }
    for entity in get_next_entity(frame, {'sort'}):
        field_name = list(entity.values())[0]
        sort_entity = sort_entities.get(field_name)
        if not sort_entity:
            continue
        search = search.sort(field=sort_entity[0], sort_type=sort_entity[1], location=None)
    # Handle sys_time
    if 'sys_time' in frame:
        entity_value = frame['sys_time'][0]['value']
        release_year = get_release_year(entity_value['value'][:MALLARD_YEAR_INDEX])
        search = search.filter(filter_type='range', field='release_year',
                               gte=release_year, lte=release_year)

    # Handle sys_interval
    if 'sys_interval' in frame:
        interval_start, interval_end = frame['sys_interval'][0]['value']['value']
        interval_start = get_release_year(interval_start[:MALLARD_YEAR_INDEX])
        interval_end = get_release_year(interval_end[:MALLARD_YEAR_INDEX])
        search = search.filter(filter_type='range', field='release_year',
                               gte=interval_start, lte=interval_end)

    results = search.execute()
    logging.info('Got {} results from KB.'.format(len(results)))

    return results


def fill_browse_slots(frame, slots):
    # TODO: Using all entities in the current frame, fill the slots dict.

    for entity_type, entity_set in frame.items():
        entities = []
        for entity in entity_set:
            entity_text = entity['cname'] if entity['cname'] else entity['text']

            # Choose the proper casing
            if entity_type == 'cast' or entity_type == 'director' or entity_type == 'title':
                entity_text = entity_text.title()
            else:
                entity_text = entity_text.lower()

            entities.append(entity_text)

        if len(entities) > 1:
            last_entity = entities.pop()
            entities_string = ', '.join(entities)
            entities_string += ' and ' + last_entity
            slots[entity_type] = entities_string

        else:
            slots[entity_type] = entities[0]

    return slots


def build_browse_response(context, slots, results):
    # Return the given template based on the available slots. Also build a client action
    # with the results, and show any prompts if necesary.

    reply = ''
    videos_client_action = {}
    prompt = ''

    # If no results match, respond accordingly.
    if len(results) == 0:
        reply = 'Sorry, no results match your search criteria. Please try again.'

        # Since user reached dead-end here, clear the frame.
        context['frame'] = {}

        return reply, videos_client_action, prompt

    else:
        # Build the language response based on the slots available.
        reply = ''

        # Add default aknowledgment.
        aknowledgments = ['Done.', 'Ok.', 'Perfect.']
        reply += random.choice(aknowledgments)
        reply += ' Here are'

        # Now add the different slots
        if 'sort' in slots:
            if slots['sort'] == 'popular':
                reply += ' {sort}'
            else:
                reply += ' the {sort}'
        else:
            reply += ' some'

        if 'genre' in slots:
            reply += ' {genre}'

        if 'type' in slots:
            reply += ' {type}s'
        else:
            reply += ' results'

        if 'title' in slots:
            reply += ' titled "{title}"'

        if 'cast' in slots:
            cast = [' with {cast}', ' starring {cast}']
            reply += random.choice(cast)

        if 'director' in slots:
            director = [' directed by {director}', ' by {director}']
            reply += random.choice(director)

        if 'country' in slots:
            country = [' from {country}', ' made in {country}']
            reply += random.choice(country)

        if 'sys_time' in slots:
            release = [' from {sys_time}', ' released in {sys_time}']
            reply += random.choice(release)

        reply += ':'

        # Build and return the client action
        videos_client_action = video_results_to_action(results)

        return reply, videos_client_action, prompt


@app.handle(intent='start_over')
def start_over(context, slots, responder):
    """
    When the user wants to start over, clear the dialogue frame and prompt for the next request.
    """
    context['frame'] = {}
    prompts = ['Sure, what do you want to watch?',
               'Let\'s start over, what would you like to watch?',
               'Okay, starting over, tell me what you want to watch.']
    responder.prompt(prompts)

    # Get default videos
    responder.respond(get_default_videos_action())
    responder.suggest(GENERAL_SUGGESTIONS)


@app.handle(intent='exit')
def say_goodbye(context, slots, responder):
    """
    When the user ends a conversation, clear the dialogue frame and say goodbye.
    """
    context['frame'] = {}
    goodbyes = ['Bye!', 'Goodbye!', 'Have a nice day.', 'See you later.']

    responder.reply(goodbyes)


@app.handle(intent='help')
def provide_help(context, slots, responder):
    """
    When the user asks for help, provide some sample queries they can try.
    """
    help_replies = ["I can help you find movies and tv shows based on your preferences."
                    " Just say want you feel like watching and I can find great options for you."]
    responder.reply(help_replies)

    help_prompts = "Here's some content for you."
    responder.prompt(help_prompts)

    # Get default videos
    responder.respond(get_default_videos_action())
    responder.suggest(GENERAL_SUGGESTIONS)


@app.handle(intent='unsupported')
def handle_unsupported(context, slots, responder):
    # Respond with a message explaining the app does not support that # query.
    unsupported = ['Sorry, I can\'t help you with that information.',
                   'Sorry, I don\'t have that information.',
                   'Sorry, I can\'t help you with that.',
                   'Sorry, I can only help you browse movies and tv shows.',
                   'Sorry, I don\'t have that information, would you like to try something else?']

    responder.reply(unsupported)

    responder.prompt(GENERAL_PROMPTS)

    # Get default videos
    responder.respond(get_default_videos_action())
    responder.suggest(GENERAL_SUGGESTIONS)


@app.handle(intent='unrelated')
def handle_unrelated(context, slots, responder):
    # Respond with a message explaining the app does not support that # query.
    responder.reply("unrelated placeholder.")


@app.handle(intent='compliment')
def say_something_nice(context, slots, responder):
    # Respond with a compliment or something nice.
    compliments = ['Thank you, you rock!',
                   'You\'re too kind.',
                   'Thanks, I try my best!',
                   'Thanks, you\'re quite amazing yourself.',
                   'Thanks, hope you\'re having a good day!']

    responder.reply(compliments)

    responder.prompt(GENERAL_PROMPTS)
    # Get default videos
    responder.respond(get_default_videos_action())
    responder.suggest(GENERAL_SUGGESTIONS)


@app.handle(intent='insult')
def handle_insult(context, slots, responder):
    # Evade the insult and come back to the app usage.
    insult_replies = ['Sorry, I do my  best!',
                      'Someone needs to watch a romantic movie.',
                      'Sorry I\'m trying!',
                      'Nobody\'s perfect!',
                      'Sorry, I\'ll try to do better next time.']

    responder.reply(insult_replies)

    responder.prompt(GENERAL_PROMPTS)

    # Get default videos
    responder.respond(get_default_videos_action())
    responder.suggest(GENERAL_SUGGESTIONS)


@app.handle()
def default(context, slots, responder):
    """
    When the user asks an unrelated question, convey the lack of understanding for the requested
    information and prompt to return to video discovery.
    """
    unrelated = ['Sorry, I didn\'t understand your request.',
                 'I\'m sorry, I\'m not sure what you mean.',
                 'Sorry, could you try a different request?',
                 'I\'m sorry, could you ask me something else related to movies or tv shows?',
                 'Sorry, I was programmed to only serve your movie and tv show requests.']

    responder.reply(unrelated)

    responder.prompt(GENERAL_PROMPTS)

    # Get default videos
    responder.respond(get_default_videos_action())
    responder.suggest(GENERAL_SUGGESTIONS)


def get_default_videos_action():
    """
    Get a client action with the most recent and popular videos.
    """
    default_videos = get_default_videos()

    videos_client_action = video_results_to_action(default_videos)

    return videos_client_action


def video_results_to_action(results):
    videos_client_action = {'videos': []}

    for video in results:
        release_year = get_release_year(video['release_date'])
        video_summary = {'title': video['title'], 'release_year': release_year, 'type': video['doc_type']}
        videos_client_action['videos'].append(video_summary)

    return videos_client_action


def get_default_videos():
    """
    Retrieve the most popular and recent videos in the knowledge base.


    Returns:
        list: The list of movies.
    """
    results = app.question_answerer.get(index=KB_INDEX_NAME)
    return results


def get_next_entity(frame, entities):
    for entity in entities:
        if entity not in frame:
            continue
        entity_name = ENTITY_TO_FIELD.get(entity, entity)
        for entity_value in frame[entity]:
            clause_value = entity_value.get('cname')
            if not clause_value:
                clause_value = entity_value['text']
            yield {entity_name: clause_value}


def get_release_year(release_date):
    if not release_date:
        return
    release_date_obj = datetime.datetime.strptime(release_date, '%Y-%m-%d')
    return release_date_obj.year


if __name__ == '__main__':
    app.cli()
