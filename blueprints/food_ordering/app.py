# -*- coding: utf-8 -*-
"""This module contains the Food Ordering workbench demo application"""
from __future__ import unicode_literals
import random
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
    """
    This is where we would call an external API to place the order, and acknowledge transaction
    completion to the user.
    For now, displays a fixed response to indicate that an order has been placed.
    """
    restaurant_name = context['frame'].get('restaurant_name')
    dishes = context['frame'].get('dishes', [])
    if not restaurant_name:
        prompts = ["I'm sorry, you need to specify a restaurant before placing an order."]
    elif len(dishes) < 1:
        prompts = ["I don't have any dishes in the basket yet. What would you like to order "
                   "from {}?".format(restaurant_name)]
    else:
        prompts = ["Great, your order from {} will be delivered in 30-45 minutes."
                   .format(restaurant_name)]
    responder.prompt(prompts)


@app.handle(intent='start_over')
def start_over(context, slots, responder):
    # Clear dialogue frame and respond with the welcome info
    context_to_preserve = ['name']
    for key in context['frame'].keys():
        if key not in context_to_preserve:
            context['frame'].pop(key)
    prompts = ["Sure, let's start over! What restaurant would you like to order from?"]
    responder.prompt(prompts)


@app.handle(intent='build_order')
def order_dish(context, slots, responder):
    """
    Simplified ordering logic which requires the user to specify a restaurant by name first.
    TODO: resolve options and quantities
    """
    def get_restaurant_details(restaurant):
        return app.question_answerer.get(index='restaurant', id=restaurant['id'])[0]

    def get_dish_details(dish):
        return app.question_answerer.get(index='menu_items', id=dish['id'])[0]

    def resolve_restaurant(text, values):
        """
        Given the user's original text and possible restaurants from the entity resolver,
        selects the one(s) that the user is most likely asking for.
        """
        if len(values) < 1 or text == values:
            responder.reply("Sorry, I could not find a restaurant called {}".format(
                            text))
            return None, None
        else:
            # For now just selects one restaurant at random. TODO: get restaurant details
            # from kb and use location, edit distance, popularity, etc to select the top one
            restaurant = random.choice(values)
            return restaurant['id'], restaurant['cname']

    def resolve_dish(dishes, restaurant_id):
        """
        Given the selected restaurant and the possible dishes from the entity resolver,
        selects the one(s) that the user is most likely asking for.
        """
        # Remove dishes not available from the selected restaurant
        restaurant_dishes = []
        for dish in dishes:
            if dish['restaurant_id'] == restaurant_id:
                restaurant_dishes.append(dish)
        if len(restaurant_dishes) < 1:
            return None
        # For now just select one dish at random. TODO: use other methods
        return random.choice(restaurant_dishes)

    dish_entities = [e for e in context['entities'] if e['type'] == 'dish']
    restaurant_entities = [e for e in context['entities'] if e['type'] == 'restaurant']

    if len(restaurant_entities) == 1:
        restaurant = restaurant_entities[0]
        restaurant_id, restaurant_name = resolve_restaurant(restaurant['text'], restaurant['value'])
        if not restaurant_id or not restaurant_name:
            return
        context['frame']['restaurant_id'] = restaurant_id
        context['frame']['restaurant_name'] = restaurant_name

    if len(restaurant_entities) > 1:
        responder.prompt('Sorry, we can only order from one restaurant at a time. Which one would '
                         'you like to order from?')

    if not context['frame'].get('restaurant_id'):
        responder.reply('What restaurant would you like to order from?')
        return

    if len(dish_entities) < 1:
        # TODO: respond with some popular restaurant dishes as suggestions
        responder.prompt("Great, ordering from {}. What would you like to eat?".format(
                         context['frame'].get('restaurant_name')))

    current_dishes = context['frame'].get('dishes', [])
    for dish in dish_entities:
        if len(dish['value']) < 1 or dish['value'] == dish['text']:
            responder.reply('Sorry, I could not find a dish with the name {}'.format(dish['text']))
            continue
        possible_dishes = []
        for cdish in dish['value']:
            possible_dishes.append(get_dish_details(cdish))
        selected_dish = resolve_dish(possible_dishes, context['frame'].get('restaurant_id'))
        if not selected_dish:
            responder.reply("Sorry, I couldn't find anything called {} at "
                            "{}".format(dish['text'], context['frame']['restaurant_name']))
            continue
        current_dishes.append(selected_dish)

    context['frame']['dishes'] = current_dishes

    if len(current_dishes) > 0:
        current_dish_names = [dish['name'].lower() for dish in current_dishes]
        current_prices = [dish['price'] for dish in current_dishes]
        prompt_msg = ("Sure I got {} from {} for a total price of ${:.2f}. Would you like to place "
                      "the order?").format(', '.join(current_dish_names),
                                           context['frame'].get('restaurant_name'),
                                           sum(current_prices))
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
