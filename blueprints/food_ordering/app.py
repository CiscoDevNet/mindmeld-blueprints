# -*- coding: utf-8 -*-
"""This module contains the Kwik-E-Mart workbench demo application"""
from __future__ import unicode_literals
from builtins import next

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
    pass


@app.handle(intent='build_order')
def order_dish(context, slots, responder):
    # if restaurant entity is present:
    #   search for dish within that restaurant’s menu
    # elif target_restaurant is present in dialogue frame:
    #   search for dish within that restaurant’s menu
    #
    # if matching dish is found:
    #   add specified quantity of item to basket

    slots['dish_name'] = ''
    slots['restaurant_name'] = ''

    dish_entity = next((e for e in context['entities'] if e['type'] == 'dish'), None)
    restaurant_entity = next((e for e in context['entities'] if e['type'] == 'restaurant'), None)

    if dish_entity is not None:
        slots['dish_name'] = dish_entity['text']
    
    if restaurant_entity is not None:
        slots['restaurant_name'] = restaurant_entity['text']
    
    responder.reply('Dish: {dish_name}, Restaurant: {restaurant_name}')


@app.handle(intent='unsupported')
@app.handle()
def default(context, slots, responder):
    prompts = ["Sorry, not sure what you meant there."
               "I can help you order food from your local restaurants."]
    responder.prompt(prompts)


if __name__ == '__main__':
    app.cli()
