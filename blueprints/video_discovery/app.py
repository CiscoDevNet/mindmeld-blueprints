# -*- coding: utf-8 -*-
"""This module contains the Workbench video discovery blueprint application"""
from __future__ import unicode_literals

import datetime
import logging
import random

from mmworkbench import Application

app = Application(__name__)


KB_INDEX_NAME = 'videos'

GENERAL_REPLIES = ['I can help you find movies and TV shows. What do you feel like watching today?',
                   'Tell me what you would like to watch today.',
                   'Talk to me to browse movies and TV shows.']

GENERAL_SUGGESTIONS = [{'text': 'Most popular', 'type': 'text'},
                       {'text': 'Most recent', 'type': 'text'},
                       {'text': 'Movies', 'type': 'text'},
                       {'text': 'TV Shows', 'type': 'text'},
                       {'text': 'Action', 'type': 'text'},
                       {'text': 'Dramas', 'type': 'text'},
                       {'text': 'Sci-Fi', 'type': 'text'}]

# Convert timestamps from mallard format to date
# Example: '2002-01-01T00:00:00.000-07:00' to '2002-01-01'
MALLARD_DATE_SPLIT_INDEX = 10

# Map entity names to field names in knowledge base
ENTITY_TO_FIELD = {
    'type': 'doc_type',
    'genre': 'genres',
    'director': 'directors',
    'country': 'countries',
}


@app.handle(intent='greet')
def welcome(context, responder):
    """
    When the user starts a conversation, say hi.
    """
    # Provide some randomness by choosing greeting from a list randomly
    greetings = ['Hello', 'Hi', 'Hey']
    try:
        # Get user's name from session information in request context to personalize the greeting.
        responder.slots['name'] = context['request']['session']['name']
        greetings = [greeting + ', {name}.' for greeting in greetings] + \
            [greeting + ', {name}!' for greeting in greetings]
    except KeyError:
        greetings = [greeting + '.' for greeting in greetings] + \
            [greeting + '!' for greeting in greetings]

    responder.reply(greetings)
    responder.reply(GENERAL_REPLIES)

    # Get default videos
    responder.list(get_default_video_payload())
    responder.suggest(GENERAL_SUGGESTIONS)


@app.handle(intent='browse')
def show_content(context, responder):
    """
    When the user looks for a movie or TV show, fetch the documents from the knowledge base
    with all entities we have so far.
    """
    # Update the frame with the new entities extracted.
    context['frame'] = update_frame(context['entities'], context['frame'])

    # Fetch results from the knowledge base using all entities in frame as filters.
    results = get_video_content(context['frame'])

    # Fill the slots with the frame.
    responder.slots.update(browse_slots_for_frame(context['frame']))

    # Build response based on available slots and results.
    reply, video_payload = build_browse_response(context, responder.slots, results)

    responder.reply(reply)

    # Build and return the directive
    responder.list(video_payload)


def update_frame(entities, frame):
    """
    Update the entities in the frame with the new entities in the 'entities' dict.

    Args:
        entities (list of dict): current entities
        frame (dict): current frame
    Returns:
        dict: updated frame
    """
    for entity in entities:
        entity_type = entity.get('type', '')
        entity_values = entity.get('value', [])

        # Extract entities which already exists in the frame
        # from previous interactions.
        existing_entities = frame.get(entity_type, [])

        # Store the first canonical name if available,
        # which could be used later as a filter if necessary.
        cname = None
        if entity_values:
            cname = entity_values[0].get('cname', None)

        # We also store 'text' info which could be used when generating
        # natural language responses.
        new_entity = {
            'type': entity_type,
            'text': entity.get('text', ''),
            'cname': cname
        }
        # When the entity type is a system entity, we store its value which could be
        # used for filtering with range if necessary.
        if entity_type in {'sys_time', 'sys_interval'}:
            new_entity['value'] = entity_values[0]

        # In this blueprint, we accumulate all entities.
        # That is, if we already have a 'title' and we receive another one, keep both in the frame.
        existing_entities = update_existing_entities(new_entity, existing_entities)

        frame[entity_type] = existing_entities
    return frame


def update_existing_entities(new_entity, existing_entities):
    """
    This method decides if we add the new entity to the frame or not. The rules are the following:

    1) Only add it if it's not already there.
    2) For 'type' and 'sort' entities, we keep only the newest one.

    Returns:
        list: the new list of entities
    """
    entity_type = new_entity.get('type', '')
    entity_text = new_entity.get('text')
    cname = new_entity.get('cname', None)

    if len(existing_entities) == 0:
        existing_entities.append(new_entity)
    elif entity_type == 'type' or entity_type == 'sort':
        existing_entities = [new_entity]
    else:
        entity_exists = False
        for existing_entity in existing_entities:

            # First get all info we need to compare the entities
            existing_entity_values = existing_entity.get('value', [])
            existing_cname = None
            if existing_entity_values:
                existing_cname = existing_entity_values[0].get('cname', None)

            existing_entity_text = existing_entity.get('text')

            # Now make the comparisons
            if cname and existing_cname and (cname == existing_cname):
                entity_exists = True

            if entity_text.lower() == existing_entity_text.lower():
                entity_exists = True

        if not entity_exists:
            existing_entities.append(new_entity)

    return existing_entities


def get_video_content(frame):
    """
    Get video content given the info in current frame.
    Using all entities in the frame, get docs from ES.

    Args:
        frame (dict): current frame
    Returns:
        (list of dict): documents from QuestionAsnwer
    """
    # Initialize Search object with index name, to achieve better
    # accuracy, we use 'and' as 'query_clauses_operator' here.
    # If the recall matters for a blueprint, we could also use 'or'.
    search = app.question_answerer.build_search(KB_INDEX_NAME, {'query_clauses_operator': 'and'})

    # We divide our entities into two categories:
    # 'search_entities' are for general text search.
    # 'filter_entities' would try to find exact match.
    search_entities = {'title'}
    filter_entities = {'cast', 'director', 'genre', 'type', 'country'}

    # Building corresponding clauses in Search object.
    for entity in get_next_entity(frame, search_entities):
        search = search.query(**entity)

    for entity in get_next_entity(frame, filter_entities):
        search = search.filter(**entity)

    # For entities about sorting, we map the entity names to field name in KB
    # and also the direction of sorting.
    sort_entities = {
        'latest': ('release_date', 'desc'),
        'oldest': ('release_date', 'asc'),
        'popular': ('popularity', 'desc'),
        'worst': ('popularity', 'asc'),
    }
    sorted_by_popularity = False
    for entity in get_next_entity(frame, {'sort'}):
        field_name = list(entity.values())[0]
        sort_entity = sort_entities.get(field_name)
        if not sort_entity:
            logging.warning('Sort field not found: {}'.format(field_name))
            continue
        if sort_entity[0] == 'popularity':
            sorted_by_popularity = True
        search = search.sort(field=sort_entity[0], sort_type=sort_entity[1])

    # If there is no sort entity for popularity field, we should add this default
    # sort for showing popular movies/tv shows.
    if not sorted_by_popularity:
        search = search.sort(field='popularity', sort_type='desc')

    # Handle sys_time, we only handle `release_year` in this blueprint.
    # For example, when user says 'action movies from 1998.'. We would
    # filter out all movies which are not released in 1998.
    if 'sys_time' in frame:
        entity_value = frame['sys_time'][0]['value']
        release_year = get_release_year(entity_value['value'][:MALLARD_DATE_SPLIT_INDEX])
        search = search.filter(field='release_year',
                               gte=release_year, lte=release_year)

    # Handle sys_interval, similar to sys_time, user can say
    # 'Action movies in 90s.' and we would filter movies by a range of time.
    if 'sys_interval' in frame:
        interval_start, interval_end = frame['sys_interval'][0]['value']['value']
        interval_start = get_release_year(interval_start[:MALLARD_DATE_SPLIT_INDEX])
        interval_end = get_release_year(interval_end[:MALLARD_DATE_SPLIT_INDEX])
        search = search.filter(field='release_year',
                               gte=interval_start, lte=interval_end)
    # We've got all we need for the Search object and it's ready to fetch documents
    # from KB. Developer should be careful here since the KB instances could be hosted
    # remotely and it's possible to get some kind of issues like Network Connections.
    try:
        results = search.execute()
        logging.info('Got {} results from KB.'.format(len(results)))
    except Exception as e:
        # When something bad happens, we should log the exception and decide what
        # would be a reasonable response to user. Here we just return an empty list.
        logging.info(e)
        results = []

    return results


def browse_slots_for_frame(frame):
    """
    Fill slots from current frame and slots.

    Args:
        frame (dict): current frame
    Returns:
        dict: slots for current frame
    """
    new_slots = {}
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
            new_slots[entity_type] = entities_string

        else:
            new_slots[entity_type] = entities[0]

    return new_slots


def build_browse_response(context, slots, results):
    """
    Return the given template based on the available slots & a payload containing video data

    Args:
        context (dict): current context
        slots (dict): current slots
        results (list of dict): documents from QuestionAnswerer
    Returns:
       reply (string): the reply to be shown to the user
       video_payload (dict): the payload containing the video results
    """
    reply = ''
    video_payload = []

    # If no results match, respond accordingly.
    if not results or len(results) == 0:
        reply = 'Sorry, no results match your search criteria. Please try again.'

        # Since user reached a dead-end here, clear the frame.
        context['frame'] = {}

        return reply, video_payload

    else:
        # Build the language response based on the slots available.
        reply = ''

        # Add a default acknowledgment.
        acknowledgments = ['Done.', 'Ok.', 'Perfect.']
        reply += random.choice(acknowledgments)
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

        # Build and return the video payload
        video_payload = build_video_payload(results)

        return reply, video_payload


@app.handle(intent='start_over')
def start_over(context, responder):
    """
    When the user wants to start over, clear the dialogue frame and prompt for the next request.
    """
    context['frame'] = {}
    replies = ['Sure, what do you want to watch?',
               'Let\'s start over, what would you like to watch?',
               'Okay, starting over, tell me what you want to watch.']
    responder.reply(replies)

    # Get default videos
    responder.list(get_default_video_payload())
    responder.suggest(GENERAL_SUGGESTIONS)


@app.handle(intent='exit')
def say_goodbye(context, responder):
    """
    When the user ends a conversation, clear the dialogue frame and say goodbye.
    """
    context['frame'] = {}
    goodbyes = ['Bye!', 'Goodbye!', 'Have a nice day.', 'See you later.']

    responder.reply(goodbyes)


@app.handle(intent='help')
def provide_help(context, responder):
    """
    When the user asks for help, provide a message explaining what to do.
    """
    help_replies = ["I can help you find movies and TV shows based on your preferences."
                    " Just say want you feel like watching and I can find great options for you."]
    responder.reply(help_replies)

    help_replies = "Here's some content for you."
    responder.reply(help_replies)

    # Get default videos
    responder.list(get_default_video_payload())
    responder.suggest(GENERAL_SUGGESTIONS)


@app.handle(intent='unsupported')
def handle_unsupported(context, responder):
    # Respond with a message explaining the app does not support that type of query.
    unsupported = ['Sorry, I can\'t help you with that information.',
                   'Sorry, I don\'t have that information.',
                   'Sorry, I can\'t help you with that.',
                   'Sorry, I can only help you browse movies and TV shows.',
                   'Sorry, I don\'t have that information, would you like to try something else?']
    responder.reply(unsupported)
    responder.reply(GENERAL_REPLIES)
    # Get default videos
    responder.list(get_default_video_payload())
    responder.suggest(GENERAL_SUGGESTIONS)


@app.handle(intent='compliment')
def say_something_nice(context, responder):
    # Respond with a compliment or something nice.
    compliments = ['Thank you, you rock!',
                   'You\'re too kind.',
                   'Thanks, I try my best!',
                   'Thanks, you\'re quite amazing yourself.',
                   'Thanks, hope you\'re having a good day!']
    responder.reply(compliments)
    responder.reply(GENERAL_REPLIES)
    # Get default videos
    responder.list(get_default_video_payload())
    responder.suggest(GENERAL_SUGGESTIONS)


@app.handle(intent='insult')
def handle_insult(context, responder):
    # Evade the insult and come back to app usage.
    insult_replies = ['Sorry, I do my  best!',
                      'Someone needs to watch a romantic movie.',
                      'Sorry I\'m trying!',
                      'Nobody\'s perfect!',
                      'Sorry, I\'ll try to do better next time.']
    responder.reply(insult_replies)
    responder.reply(GENERAL_REPLIES)
    # Get default videos
    responder.list(get_default_video_payload())
    responder.suggest(GENERAL_SUGGESTIONS)


@app.handle()
def default(context, responder):
    """
    When the user asks an unrelated question, convey the lack of understanding for the requested
    information and prompt to return to video discovery.
    """
    unrelated = ['Sorry, I didn\'t understand your request.',
                 'I\'m sorry, I\'m not sure what you mean.',
                 'Sorry, could you try a different request?',
                 'I\'m sorry, could you ask me something else related to movies or TV shows?',
                 'Sorry, I was programmed to only serve your movie and TV show requests.']
    responder.reply(unrelated)
    responder.reply(GENERAL_REPLIES)
    # Get default videos
    responder.list(get_default_video_payload())
    responder.suggest(GENERAL_SUGGESTIONS)


def get_default_video_payload():
    """
    Get a directive with the most recent and popular videos.

    Returns:
        dict: the payload containing the video results
    """
    default_videos = get_default_videos()
    return build_video_payload(default_videos)


def build_video_payload(videos):
    video_payload = []

    for video in videos:
        release_year = get_release_year(video['release_date'])
        video_summary = {
            'title': video['title'],
            'release_year': release_year,
            'type': video['doc_type'],
            'popularity': video['popularity']
        }
        video_payload.append(video_summary)
    return video_payload


def get_default_videos():
    """
    Retrieve the most popular and recent videos in the knowledge base.

    Returns:
        list: a list of default popular video documents.
    """
    try:
        results = app.question_answerer.get(index=KB_INDEX_NAME,
                                            _sort='popularity', _sort_type='desc')
    except Exception as e:
        logging.info(e)
        results = []
    return results


def get_next_entity(frame, entities):
    """
    Yield the next entity in a frame if this entity is in the list of given entities.

    Args:
        frame (dict): current frame
        entities (dict): entities we are interested
    Yields:
        dict: {field name: clause value}
    """
    for entity_name in entities:
        if entity_name not in frame:
            continue
        field_name = ENTITY_TO_FIELD.get(entity_name, entity_name)
        for entity_value in frame[entity_name]:
            clause_value = entity_value.get('cname')
            if not clause_value:
                clause_value = entity_value['text']
            yield {field_name: clause_value}


def get_release_year(release_date):
    """
    Get the year from release date.

    Args:
        release_date (str): date in the form 'YYYY-mm-dd'

    Returns:
        int: year
    """
    if not release_date:
        return
    release_date_obj = datetime.datetime.strptime(release_date, '%Y-%m-%d')
    return release_date_obj.year


if __name__ == '__main__':
    app.cli()
