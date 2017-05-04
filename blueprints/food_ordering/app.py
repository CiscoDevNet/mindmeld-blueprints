# -*- coding: utf-8 -*-
"""This module contains the Food Ordering workbench demo application"""
from __future__ import unicode_literals
import random
from mmworkbench import Application


app = Application(__name__)


@app.handle(intent='greet')
def welcome(context, slots, responder):
    """
    When a user is starting a conversation, says hi and gives some restaurant suggestions
    to explore.
    """
    try:
        slots['name'] = context['request']['session']['name']
        prefix = 'Hello, {name}. '
    except KeyError:
        prefix = 'Hello. '
    # TODO: get some restaurants at random
    responder.prompt(prefix + 'Here are some nearby popular restaurants '
                              'you can order delivery from.')


@app.handle(intent='exit')
def say_goodbye(context, slots, responder):
    """
    When a user is trying to exit, says goodbye and clears the context frame.
    """
    responder.reply(['Bye', 'Goodbye', 'Have a nice day.'])
    context['frame'] = {}


@app.handle(intent='help')
def provide_help(context, slots, responder):
    """
    If the user asks for help, provides some sample queries they can try.
    """
    prompts = ["I can help you order food from your local restaurants. For example, you can "
               "say 'I would like a chicken soup from Taqueria Mana' or 'I feel like having "
               "a burrito.'"]
    responder.prompt(prompts)


@app.handle(intent='place_order')
def place_order(context, slots, responder):
    """
    This is where we would call an external API to place the order, and acknowledge transaction
    completion to the user.
    For now, displays a fixed response to indicate that an order has been placed.
    """
    slots['restaurant_name'] = context['frame'].get('restaurant_name')
    dishes = context['frame'].get('dishes', [])
    if not slots['restaurant_name']:
        prompts = ["I'm sorry, you need to specify a restaurant before placing an order."]
    elif len(dishes) < 1:
        prompts = ["I don't have any dishes in the basket yet. What would you like to order "
                   "from {restaurant_name}?"]
    else:
        prompts = ["Great, your order from {restaurant_name} will be delivered in 30-45 minutes."]
        context['frame'] = {}

    responder.prompt(prompts)


@app.handle(intent='start_over')
def start_over(context, slots, responder):
    """
    When the user is trying to start over, clears the context frame to start on a clean slate.
    """
    # Clear dialogue frame and respond with the welcome info
    context['frame'] = {}
    prompts = ["Sure, let's start over! What restaurant would you like to order from?"]
    responder.prompt(prompts)


@app.handle(intent='build_order')
def order_dish(context, slots, responder):
    """
    This method handles all logic for when a user is trying to specify a restaurant or build an
    order.
    For simplification, we require the user to specify a restaurant by name before adding dishes
    to their basket.
    TODO: resolve options and quantities
    """
    def get_restaurant_details(restaurant):
        """
        Gets the full restaurant information from the knowledge base
        """
        return app.question_answerer.get(index='restaurants', id=restaurant['id'])[0]

    def get_dish_details(dish):
        """
        Gets the full dish details from the knowledge base
        """
        return app.question_answerer.get(index='menu_items', id=dish['id'])[0]

    def resolve_restaurant(text, values):
        """
        Given the user's original text, possible restaurants from the entity resolver, and
        additional restaurant information from the knowledge base, selects the one that the user
        is most likely asking for.
        """
        if len(values) < 1 or text == values:
            return None, None
        else:
            # For now just selects one restaurant at random. TODO: get restaurant details
            # from kb and use location, edit distance, popularity, etc to select the top one
            restaurant = random.choice(values)
            return restaurant['id'], restaurant['cname']

    def resolve_dish(dishes, restaurant_id):
        """
        Given the selected restaurant and the possible dishes from the entity resolver,
        selects the one that the user is most likely asking for.
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

    # Store the restaurant information if a restaurant is specified in the query
    if len(restaurant_entities) > 1:
        responder.prompt('Sorry, we can only order from one restaurant at a time. Which one would '
                         'you like to order from?')

    if len(restaurant_entities) == 1:
        restaurant = restaurant_entities[0]
        restaurant_id, restaurant_name = resolve_restaurant(restaurant['text'], restaurant['value'])
        if not restaurant_id or not restaurant_name:
            slots['restaurant_name'] = restaurant['text']
            responder.reply("Sorry, I could not find a restaurant called {restaurant_name}. Is "
                            "there another restaurant you would like to order from?")
            return
        context['frame']['restaurant_id'] = restaurant_id
        context['frame']['restaurant_name'] = restaurant_name

    # If the user hasn't indicated a restaurant, prompt to select one
    if not context['frame'].get('restaurant_id'):
        if len(dish_entities) > 0:
            # Give the user some restaurant options for one of the dishes they asked for
            for dish in dish_entities:
                dishes = [get_dish_details(dish) for dish in dish['value']]
                restaurant_ids = [dish_option['restaurant_id'] for dish_option in dishes]
                if len(restaurant_ids) > 0:
                    restaurant_names = list(set([get_restaurant_details({'id': rid})['name']
                                                 for rid in restaurant_ids]))
                    slots['restaurant_options'] = ', '.join(restaurant_names[0:3])
                    slots['dish_name'] = dish['text']
                    responder.reply("I found {dish_name} at restaurants {restaurant_options}. Where"
                                    " would you like to order from?")
                    return
            responder.reply("Sorry, I didn't find what you were looking for at a nearby restaurant."
                            " What restaurant would you like to order from?")
        else:
            responder.reply('What restaurant would you like to order from?')
        return

    # Now add dishes to the cart for the selected restaurant
    slots['restaurant_name'] = context['frame']['restaurant_name']
    if len(dish_entities) < 1:
        # TODO: respond with some popular restaurant dishes as suggestions
        responder.prompt("Great, what would you like to order from {restaurant_name}?")
        return

    current_dishes = context['frame'].get('dishes', [])
    for dish in dish_entities:
        slots['dish_name'] = dish['text']
        if len(dish['value']) < 1 or dish['value'] == dish['text']:
            responder.reply('Sorry, I could not find a dish with the name {dish_name}')
            continue
        possible_dishes = []
        for cdish in dish['value']:
            possible_dishes.append(get_dish_details(cdish))
        selected_dish = resolve_dish(possible_dishes, context['frame'].get('restaurant_id'))
        if not selected_dish:
            responder.reply("Sorry, I couldn't find anything called {dish_name} at "
                            "{restaurant_name}")
            continue
        current_dishes.append(selected_dish)

    context['frame']['dishes'] = current_dishes

    if len(current_dishes) > 0:
        current_dish_names = [dish['name'].lower() for dish in current_dishes]
        current_prices = [dish['price'] for dish in current_dishes]
        slots['dish_names'] = ', '.join(current_dish_names)
        slots['price'] = sum(current_prices)
        prompt_msg = ("Sure I got {dish_names} from {restaurant_name} for a total price of "
                      "${price:.2f}. Would you like to place the order?")
        responder.prompt(prompt_msg)
    else:
        responder.prompt('What dish would you like to eat?')


@app.handle(intent='unsupported')
@app.handle()
def default(context, slots, responder):
    """
    If the user is asking an unrelated questions, responds with an acknowledgment and prompt to
    return to ordering.
    """
    prompts = ["Sorry, not sure what you meant there."
               "I can help you order food from your local restaurants."]
    responder.prompt(prompts)


if __name__ == '__main__':
    app.cli()
