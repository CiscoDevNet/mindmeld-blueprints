# -*- coding: utf-8 -*-
"""This module contains the Food Ordering workbench demo application"""
from __future__ import unicode_literals

from mmworkbench import Application


app = Application(__name__)


@app.handle(intent='greet')
def welcome(context, slots, responder):
    try:
        slots['name'] = context['request']['session']['name']
        prefix = 'Hello, {name}. '
    except KeyError:
        prefix = 'Hello. '
    responder.prompt(prefix + 'Here are some nearby popular restaurants '
                              'you can order delivery from.')


@app.handle(intent='exit')
def say_goodbye(context, slots, responder):
    responder.reply(['Bye', 'Goodbye', 'Have a nice day.'])


@app.handle(intent='help')
def provide_help(context, slots, responder):
    prompts = ["I can help you order food from your local restaurants. For example, you can "
               "say 'What are some good pizza places nearby?' or 'I feeling having a burrito.'"]
    responder.prompt(prompts)


@app.handle(intent='place_order')
def place_order(context, slots, responder):
    # Call external/mock API to place the order.
    # Acknowledge transaction completion to user.
    pass


@app.handle(intent='start_over')
def start_over(context, slots, responder):
    # Clear dialogue frame and respond with the welcome info
    slots_to_preserve = ['name']
    for key in slots.keys():
        if key not in slots_to_preserve:
            slots.pop(key)
    prompts = ["Sure, let's start over! What would you like to eat?"]
    responder.prompt(prompts)


@app.handle(intent='build_order')
def order_dish(context, slots, responder):
    # TODO:
    # - resolve options
    # - link options to dish names
    # - ensure that dish is available at the specified restaurant
    # - display images of the top n choices
    # - resolve dishes/options/restaurants in a more sophisticated way
    def get_dish_details(dish):
        # TODO: make a call to the KB to get the restaurant the dish is from, and
        # any required options that need to be populated
        return dish

    def resolve_restaurant(text, values):
        # For now just selects one restaurant at random. TODO: use ngram/glove vectors
        if len(values) < 1 or text == values:
            responder.reply("Sorry, I could not find a restaurant called {}".format(
                            restaurant['text']))
            return None, None
        else:
            return values[0]['id'], values[0]['cname']

    def resolve_dish(dishes, restaurant_id):
        # For now just select one dish at random. TODO: use other methods
        return dishes[0]

    dish_entities = [e for e in context['entities'] if e['type'] == 'dish']
    restaurant_entities = [e for e in context['entities'] if e['type'] == 'restaurant']

    if len(restaurant_entities) == 1:
        restaurant = restaurant_entities[0]
        restaurant_id, restaurant_name = resolve_restaurant(restaurant['text'], restaurant['value'])
        slots['restaurant_id'] = restaurant_id
        slots['restaurant_name'] = restaurant_name

    if len(restaurant_entities) > 1:
        responder.prompt('Sorry, we can only order from one restaurant at a time. Which one would '
                         'you like to order from?')

    if len(dish_entities) < 1:
        responder.prompt("Sure, let's order from {}. What would you like?".format(
                         slots.get('restaurant_name')))

    current_dish_ids = slots.get('dish_ids', [])
    current_dish_names = slots.get('dish_names', [])
    for dish in dish_entities:
        if len(dish['value']) < 1 or dish['value'] == dish['text']:
            responder.reply('Sorry, I could not find a dish with the name {}'.format(dish['text']))
            continue
        possible_dishes = []
        for cdish in dish['value']:
            possible_dishes.append(get_dish_details(cdish))
        selected_dish = resolve_dish(possible_dishes, slots.get('restaurant_id'))
        current_dish_ids.append(selected_dish['id'])
        current_dish_names.append(selected_dish['cname'])

    slots['dish_ids'] = current_dish_ids
    slots['dish_names'] = current_dish_names

    if len(current_dish_names) > 0:
        prompt_msg = 'Sure, I got ' + ', '.join(current_dish_names)
        if slots.get('restaurant_name'):
            prompt_msg += ' from {}'.format(slots.get('restaurant_name'))
        prompt_msg += '. Would you like to place the order?'
        responder.prompt(prompt_msg)
    else:
        responder.prompt('What dish would you like to eat?')


@app.handle(intent='unsupported')
@app.handle()
def default(context, slots, responder):
    prompts = ["Sorry, not sure what you meant there."
               "I can help you order food from your local restaurants."]
    responder.prompt(prompts)


if __name__ == '__main__':
    app.cli()
