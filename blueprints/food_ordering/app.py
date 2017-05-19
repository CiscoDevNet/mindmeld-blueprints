# -*- coding: utf-8 -*-
"""This module contains the Workbench food ordering blueprint application"""
from __future__ import unicode_literals
from mmworkbench import Application

app = Application(__name__)


@app.handle(intent='greet')
def welcome(context, slots, responder):
    """
    When the user starts a conversation, say hi and give some restaurant suggestions to explore.
    """
    try:
        # Get user's name from session information in request context to personalize the greeting
        slots['name'] = context['request']['session']['name']
        prefix = 'Hello, {name}. '
    except KeyError:
        prefix = 'Hello. '

    # Get suggestions for three restaurants from the knowledge base.
    # Ideally, these should be selected using factors like popularity, proximity, etc.
    restaurants = app.question_answerer.get(index='restaurants')
    suggestions = ', '.join([r['name'] for r in restaurants[0:3]])

    # Build up the final natural language response and reply to the user
    responder.prompt(prefix + 'Some nearby popular restaurants you can order delivery from are '
                     + suggestions)


@app.handle(intent='exit')
def say_goodbye(context, slots, responder):
    """
    When the user ends a conversation, clear the dialogue frame and say goodbye.
    """
    # Clear the dialogue frame to start afresh for the next user request
    context['frame'] = {}

    # Respond with a random selection from one of the canned "goodbye" responses.
    responder.reply(['Bye!', 'Goodbye!', 'Have a nice day.', 'See you later.'])


@app.handle(intent='help')
def provide_help(context, slots, responder):
    """
    When the user asks for help, provide some sample queries they can try.
    """
    # Respond with examples demonstrating how the user can order food from different restaurants.
    # For simplicity, we have a fixed set of demonstrative queries here, but they could also be
    # randomly sampled from a pool of example queries each time.
    prompts = ["I can help you order food delivery from your local restaurants. For example, "
               "you can say 'I would like a chicken soup from Taqueria Mana' or 'I feel like "
               "having a burrito.'"]
    responder.prompt(prompts)


@app.handle(intent='start_over')
def start_over(context, slots, responder):
    """
    When the user wants to start over, clear the dialogue frame and prompt for the next request.
    """
    # Clear the dialogue frame and respond with a variation of the welcome message.
    context['frame'] = {}
    prompts = ["Sure, let's start over! What restaurant would you like to order from?"]
    responder.prompt(prompts)


@app.handle(intent='place_order')
def place_order(context, slots, responder):
    """
    When the user wants to place the order, call an external API to process the transaction and
    acknowledge the order completion status to the user.

    For this demo app, we just display a fixed response to indicate that an order has been placed.
    """
    # Get the user's restaurant selection from the dialogue frame
    selected_restaurant = context['frame'].get('restaurant')

    if selected_restaurant:
        # If a restaurant has been selected, set its name in the natural language response
        slots['restaurant_name'] = selected_restaurant['name']

        # Get the user's requested dishes from the frame
        dishes = context['frame'].get('dishes', [])

        if len(dishes) > 0:
            # If all the necessary information (selection of dishes and the restaurant) is
            # available, proceed to place the order. In a real application, this would be done by
            # calling an external API to process the transaction. Here, we just reply with a canned
            # response confirming that the order has been placed.
            prompts = ['Great, your order from {restaurant_name} will be delivered in 30-45 '
                       'minutes.']

            # Clear the dialogue frame to start afresh for the next user request
            context['frame'] = {}
        else:
            # If no dishes have been requested, prompt the user to order something from the menu.
            prompts = ["I don't have any dishes in the basket yet. What would you like to order "
                       "from {restaurant_name}?"]
    else:
        # If no restaurant has been selected, prompt the user to make a selection.
        prompts = ["I'm sorry, you need to select a restaurant before placing an order."]

    responder.prompt(prompts)


@app.handle(intent='build_order')
def build_order(context, slots, responder):
    """
    When the user expresses an intent to start or continue ordering food, provide the 
    appropriate guidance at each step for sequentially building up the order. This involves 
    providing restaurant and dish suggestions, availability and pricing details, and in general, 
    any information that's helpful for the user to successfully place an order for delivery. 
    
    To keep the illustration simple, in our demo app, we guide the user to select a restaurant 
    first, before adding any dishes to their "check-out" basket.
    """
    # Get information about the user's requested restaurant from the dialogue frame, in case a
    # selection has been already made in a previous turn.
    selected_restaurant = context['frame'].get('restaurant')

    # Next, check for any new restaurant requests the user has made in this turn. If the user
    # mentions more than one restaurant (i.e. more than one restaurant entity is recognized in
    # the query), choose the first one by default. Alternatively, one could present the user with
    # multiple restaurant results and prompt to select one.
    restaurant_entity = next((e for e in context['entities'] if e['type'] == 'restaurant'), None)

    if restaurant_entity:
        if len(restaurant_entity['value']) > 0:
            # If the recognized restaurant entity has multiple resolved values (i.e. it can
            # potentially be linked to more than one restaurant entry in the knowledge base),
            # pick the first KB entry. In a real application, this choice can be made in a more
            # informed manner, taking into account factors such as the restaurant's proximity to
            # the user's current location, the restaurant's popularity and reviews, the user's
            # personal preferences, etc.
            selected_restaurant = _get_restaurant_from_kb(restaurant_entity['value'][0])

            # Overwrite the restaurant information in the dialogue frame and clear any dish
            # selections made so far. Ideally, this should be done after verifying that the
            # restaurant entity detected in this turn is different from the existing user
            # selection in the dialogue frame (to ensure that this is not a continuation of the
            # order at the same location).
            context['frame']['restaurant'] = selected_restaurant
            context['frame']['dishes'] = []
        else:
            # If the restaurant entity couldn't be successfully linked to any entry in the
            # knowledge base (i.e. there are no candidate resolved values to choose from),
            # prompt the user to select a different restaurant.
            slots['restaurant_name'] = selected_restaurant['name']
            responder.reply("Sorry, I could not find a restaurant called {restaurant_name}. Is "
                            "there another restaurant you would like to order from?")
            return

    # Use the selected restaurant's name in natural language responses.
    if selected_restaurant:
        slots['restaurant_name'] = selected_restaurant['name']

    # Now that the restaurant details are available, we next look for information about the
    # dishes ordered by the user.

    # First, get details on dish selections already made in previous turns from the dialogue frame.
    selected_dishes = context['frame'].get('dishes', [])

    # Next, get all the recognized dish entities in the current user query.
    dish_entities = [e for e in context['entities'] if e['type'] == 'dish']

    if len(dish_entities) > 0:
        if selected_restaurant:
            # If the user has requested one or more dishes and also selected a specific
            # restaurant, add the requested dishes to the "check-out" basket. The basket contents
            # are stored in the dialogue frame (context['frame']['dishes']).

            for dish_entity in dish_entities:
                # Use the user-specified alias for the dish in the app's natural language responses
                slots['dish_name'] = dish_entity['text']

                if len(dish_entity['value']) > 0:
                    # Get all the potential resolved values for this dish entity. Each candidate
                    # represents a different entry in the knowledge base, corresponding to a
                    # specific food item on a specific restaurant's menu. We will use information
                    # about the selected restaurant to identify the correct dish from this
                    # candidate list.
                    dish_candidates = [value for value in dish_entity['value']]

                    # Get the full knowledge base entry for each of the dish candidates.
                    dish_entries = [_get_dish_from_kb(dc) for dc in dish_candidates]

                    # Resolve to the correct knowledge base entry using the restaurant information.
                    selected_dish = _resolve_dish(selected_restaurant['id'], dish_entries)

                    if selected_dish:
                        # If the dish entity could be successfully mapped to a specific entry on
                        # the restaurant's menu, add it to our current list of dishes.
                        selected_dishes.append(selected_dish)
                    else:
                        # If the requested dish isn't available at the selected restaurant,
                        # notify the user and prompt to make a different selection. In a real
                        # app, it would be useful to provide recommendations for dishes similar
                        # to the originally requested one, to assist the user.
                        responder.reply("Sorry, I couldn't find anything called {dish_name} at "
                                        "{restaurant_name}. Would you like to order something "
                                        "else?")
                else:
                    # If the dish couldn't be successfully linked to any entry in our knowledge
                    # base, notify the user.
                    responder.reply('Sorry, I could not find a dish with the name {dish_name}')

            # Update the basket information in the dialogue frame
            context['frame']['dishes'] = selected_dishes
        else:
            # If the user has requested one or more dishes, but not selected a restaurant yet,
            # prompt him to pick a restaurant from a list of suggestions. This suggestion list can
            # be generated in a number of ways. Here, we just take the first requested dish and
            # provide a list of (up to) three restaurants that have that item on their menu.

            # Get the first dish entity that has non-zero resolved values.
            dish_entity = next((de for de in dish_entities if len(de['value']) > 0), None)

            if dish_entity:
                # Get up to three possible resolved values for the dish entity
                dish_candidates = [value for value in dish_entity['value']][0:3]

                # Get the knowledge base entry for each of the dishes
                dish_entries = [_get_dish_from_kb(dc) for dc in dish_candidates]

                # Get the restaurant info for each dish from their respective KB entries
                restaurant_ids = set([entry['restaurant_id'] for entry in dish_entries])
                restaurant_names = [_get_restaurant_from_kb({'id': rid})['name'] for
                                    rid in restaurant_ids]

                slots['suggestions'] = ', '.join(restaurant_names)
                slots['dish_name'] = dish_entity['text']
                responder.reply('I found {dish_name} at {suggestions}. Where would you like '
                                'to order from?')
            else:
                # If none of the user-requested dishes could be resolved to entries in the
                # knowledge base, notify the user and prompt to choose a restaurant by name.
                responder.reply("Sorry, I didn't find what you were looking for at a nearby "
                                "restaurant. What restaurant would you like to order from?")
    elif len(selected_dishes) == 0:
        # If the user hasn't selected any dishes so far, prompt the user to make a selection based
        # on the information that is already available.
        if selected_restaurant:
            # If the user has chosen a restaurant, prompt to order dishes from that restaurant.
            responder.prompt('Great, what would you like to order from {restaurant_name}?')
        else:
            # If the user has not chosen a restaurant, prompt to do so.
            responder.prompt('What restaurant would you like to order from?')

    if selected_restaurant and len(selected_dishes) > 0:
        # If information on both the restaurant and requested dishes is available, respond with a
        # preview of the current basket details and prompt for order confirmation.
        selected_dish_names = [dish['name'].lower() for dish in selected_dishes]
        dish_prices = [dish['price'] for dish in selected_dishes]
        slots['dish_names'] = ', '.join(selected_dish_names)
        slots['price'] = sum(dish_prices)
        prompt_msg = ('Sure I got {dish_names} from {restaurant_name} for a total price of '
                      '${price:.2f}. Would you like to place the order?')
        responder.prompt(prompt_msg)


@app.handle(intent='unsupported')
@app.handle()
def default(context, slots, responder):
    """
    When the user asks an unrelated question, convey the lack of understanding for the requested 
    information and prompt to return to food ordering.
    """
    prompts = ['Sorry, not sure what you meant there. I can help you order food from your local '
               'restaurants.']
    responder.prompt(prompts)


# Helper methods for build order

def _get_restaurant_from_kb(restaurant):
    """
    Retrieves the detailed knowledge base entry for a given restaurant 
    """
    return app.question_answerer.get(index='restaurants', id=restaurant['id'])[0]


def _get_dish_from_kb(dish):
    """
    Retrieves the detailed knowledge base entry for a given dish
    """
    return app.question_answerer.get(index='menu_items', id=dish['id'])[0]


def _resolve_dish(restaurant_id, dishes):
    """
    Given a selected restaurant and a list of candidate dish entries from the knowledge base, 
    selects the one that the user is most likely asking for. The logic for this selection 
    could be arbitrarily complex and take into account factors like a dish's popularity, 
    time of the day, the user's preferences, etc. Here, we simply pick the first candidate that is 
    available on the given restaurant's menu.
    """
    return next((d for d in dishes if d['restaurant_id'] == restaurant_id), None)


if __name__ == '__main__':
    app.cli()
