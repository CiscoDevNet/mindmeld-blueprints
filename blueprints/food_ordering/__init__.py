"""This module contains the MindMeld food ordering blueprint application"""
from mindmeld import Application

app = Application(__name__)

__all__ = ['app']


@app.handle(default=True)
@app.handle(intent='unsupported')
def default(request, responder):
    """
    When the user asks an unrelated question, convey the lack of understanding for the requested
    information and prompt to return to food ordering.
    """
    replies = ["Sorry, not sure what you meant there. I can help you order food from your local "
               "restaurants. Try something like 'I'll have a veggie pizza from firetrail'"]
    responder.reply(replies)


@app.handle(intent='greet')
def welcome(request, responder):
    """
    When the user starts a conversation, say hi and give some restaurant suggestions to explore.
    """
    try:
        # Get user's name from session information in a request to personalize the greeting.
        responder.slots['name'] = request.context['name']
        prefix = 'Hello, {name}. '
    except KeyError:
        prefix = 'Hello. '

    # Get suggestions for three restaurants from the knowledge base.
    # Ideally, these should be selected using factors like popularity, proximity, etc.
    restaurants = app.question_answerer.get(index='restaurants')
    suggestions = ', '.join([r['name'] for r in restaurants[0:3]])

    # Build up the final natural language response and reply to the user.
    responder.reply(prefix + 'Some nearby popular restaurants you can order delivery from are '
                    + suggestions)


@app.handle(intent='exit')
def say_goodbye(request, responder):
    """
    When the user ends a conversation, clear the dialogue frame and say goodbye.
    """
    # Clear the dialogue frame to start afresh for the next user request.
    responder.frame = {}

    # Respond with a random selection from one of the canned "goodbye" responses.
    responder.reply(['Bye!', 'Goodbye!', 'Have a nice day.', 'See you later.'])


@app.handle(intent='help')
def provide_help(request, responder):
    """
    When the user asks for help, provide some sample queries they can try.
    """
    # Respond with examples demonstrating how the user can order food from different restaurants.
    # For simplicity, we have a fixed set of demonstrative queries here, but they could also be
    # randomly sampled from a pool of example queries each time.
    replies = ["I can help you order food delivery from your local restaurants. For example, "
               "you can say 'I would like a pad see ew from Modern Thai' or 'I feel like "
               "having a burrito.'"]
    responder.reply(replies)


@app.handle(intent='start_over')
def start_over(request, responder):
    """
    When the user wants to start over, clear the dialogue frame and reply for the next request.
    """
    # Clear the dialogue frame and respond with a variation of the welcome message.
    responder.frame = {}
    replies = ["Ok, let's start over! What restaurant would you like to order from?"]
    responder.reply(replies)
    responder.listen()


@app.handle(intent='place_order')
def place_order(request, responder):
    """
    When the user wants to place the order, call an external API to process the transaction and
    acknowledge the order completion status to the user.

    For this demo app, we just display a fixed response to indicate that an order has been placed.
    """
    # Get the user's restaurant selection from the dialogue frame.
    selected_restaurant = request.frame.get('restaurant')

    if selected_restaurant:
        # If a restaurant has been selected, set its name in the natural language response.
        responder.slots['restaurant_name'] = selected_restaurant['name']

        if len(request.frame.get('dishes', [])) > 0:
            # If the user has already made his dish selections from the menu, proceed to place the
            # order. In a real application, this would be done by calling an external API to
            # process the transaction. Here, we just reply with a canned response confirming that
            # the order has been placed.
            replies = ['Great, your order from {restaurant_name} will be delivered in 30-45 '
                       'minutes.']

            # Clear the dialogue frame to start afresh for the next user request.
            responder.frame = {}
        else:
            # If no dishes have been requested, prompt the user to order something from the menu.
            replies = ["I don't have any dishes in the basket yet. What would you like to order "
                       "from {restaurant_name}?"]
    else:
        # If no restaurant has been selected, prompt the user to make a selection.
        replies = ["I'm sorry, you need to select a restaurant before placing an order."]

    responder.reply(replies)


@app.handle(intent='build_order')
def build_order(request, responder):
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
    selected_restaurant = request.frame.get('restaurant')

    # Next, check for any new restaurant requests the user has made in this turn. If the user
    # mentions more than one restaurant (i.e. more than one restaurant entity is recognized in
    # the query), choose the first one by default. Alternatively, one could present the user with
    # multiple restaurant results and prompt to select one.
    restaurant_entity = next((e for e in request.entities if e['type'] == 'restaurant'), None)

    if restaurant_entity:
        if len(restaurant_entity['value']) > 0:
            # If the recognized restaurant entity has multiple resolved values (i.e. it can
            # potentially be linked to more than one restaurant entry in the knowledge base),
            # pick the first KB entry. In a real application, this choice can be made in a more
            # informed manner, taking into account factors such as the restaurant's proximity to
            # the user's current location, the restaurant's popularity and reviews, the user's
            # personal preferences, etc.
            selected_restaurant = _kb_fetch('restaurants', restaurant_entity['value'][0]['id'])

            # Overwrite the restaurant information in the dialogue frame and clear any dish
            # selections made so far. Ideally, this should be done after verifying that the
            # restaurant entity detected in this turn is different from the existing user
            # selection in the dialogue frame (to ensure that this is not a continuation of the
            # order at the same location).
            responder.frame['restaurant'] = selected_restaurant
            responder.frame['dishes'] = []
        else:
            # If the restaurant entity couldn't be successfully linked to any entry in the
            # knowledge base (i.e. there are no candidate resolved values to choose from),
            # prompt the user to select a different restaurant.
            responder.slots['restaurant_name'] = restaurant_entity['text']
            responder.reply("Sorry, I could not find a restaurant called {restaurant_name}. Is "
                            "there another restaurant you would like to order from?")
            responder.listen()
            return

    # Store the selected restaurant's name for later use in natural language responses.
    if selected_restaurant:
        responder.slots['restaurant_name'] = selected_restaurant['name']

    # Now that the restaurant details are available, we next look for information about the
    # dishes ordered by the user.

    # First, get details on dish selections already made in previous turns from the dialogue frame.
    selected_dishes = responder.frame.get('dishes', [])

    # Next, get all the recognized dish entities in the current user query.
    dish_entities = [e for e in request.entities if e['type'] == 'dish']

    # If we cannot find any dish entities in the current query, check the frame to see
    # if the there were any dish entities stored previously
    dish_entities = dish_entities if dish_entities else responder.frame.pop('dish_entities', [])

    if len(dish_entities) > 0:
        responder.frame['dish_entities'] = dish_entities

        if selected_restaurant:
            # If the user has requested one or more dishes and also selected a specific
            # restaurant, add the requested dishes to the "check-out" basket. The basket contents
            # are stored in the responder frame.

            for dish_entity in dish_entities:
                # Store the user-specified dish name for use in natural language responses.
                responder.slots['dish_name'] = dish_entity['text']

                # Resolve the dish entity to a knowledge base entry using restaurant information.
                selected_dish = _resolve_dish(dish_entity, selected_restaurant)

                if selected_dish:
                    # If the dish entity could be successfully mapped to a specific entry on
                    # the restaurant's menu, add it to our current list of dishes.
                    selected_dishes.append(selected_dish)
                else:
                    # If the requested dish isn't available at the selected restaurant, or couldn't
                    # be linked to a specific KB entry, notify the user and prompt to make a
                    # different selection. In a real app, it would be useful to provide
                    # recommendations for dishes similar to the originally requested one,
                    # to assist the user.
                    responder.reply("Sorry, I couldn't find anything called {dish_name} at "
                                    "{restaurant_name}. Would you like to order something "
                                    "else?")
                    responder.listen()
                    return

            # Update the basket information in the dialogue frame after all the dish entities
            # have been processed and mapped to their respective KB entries.
            responder.frame['dishes'] = selected_dishes
        else:
            # If the user has requested one or more dishes, but not selected a restaurant yet,
            # prompt him to pick a restaurant from a list of suggestions. This suggestion list can
            # be generated in a number of ways. Here, we just take the first requested dish and
            # provide a list of (up to) three restaurants which have that item on their menu.

            # Get the first dish entity that has non-zero resolved values.
            dish_entity = next((de for de in dish_entities if 'value' in de), None)

            if dish_entity:
                # Get up to three possible resolved values for the dish entity.
                dish_candidates = [value for value in dish_entity['value']][0:3]

                # Get the knowledge base entry for each of the dishes.
                dish_entries = [_kb_fetch('menu_items', dc['id']) for dc in dish_candidates]

                # Get the restaurant info for each dish from their respective KB entries.
                restaurant_ids = set([entry['restaurant_id'] for entry in dish_entries])
                restaurant_names = [_kb_fetch('restaurants', rid)['name'] for rid in restaurant_ids]

                # Compose the response with the restaurant suggestions and reply to the user.
                responder.slots['suggestions'] = ', '.join(restaurant_names)
                responder.slots['dish_name'] = dish_entity['text']
                responder.reply('I found {dish_name} at {suggestions}. Where would you like '
                                'to order from?')
                responder.listen()
            else:
                # If none of the user-requested dishes could be resolved to entries in the
                # knowledge base, notify the user and prompt to choose a restaurant by name.
                responder.reply("Sorry, I didn't find what you were looking for at a nearby "
                                "restaurant. What restaurant would you like to order from?")
                responder.listen()

            return

    # We should now have all user-requested information up to this point (i.e. from this turn and
    # previous turns) reconciled into selected_restaurant and selected_dishes.

    if len(selected_dishes) > 0:
        # If dish selections have been made (which also implicitly implies that a restaurant has
        # been selected), respond with a preview of the current basket and prompt for order
        # confirmation.
        dish_quantities = {}
        for dish in selected_dishes:
            dish_quantities[dish['name']] = dish_quantities.get(dish['name'], 0) + dish['quantity']
        dish_names = [(str(dish_quantities[dish]) + ' order of ' + dish)
                      if dish_quantities[dish] == 1
                      else (str(dish_quantities[dish]) + ' orders of ' + dish)
                      for dish in dish_quantities.keys()]
        dish_prices = [_price_dish(dish) for dish in selected_dishes]
        if len(dish_names) > 1:
            dish_names[-1] = 'and ' + dish_names[-1]
        if len(dish_names) > 2:
            responder.slots['dish_names'] = ', '.join(dish_names)
        else:
            responder.slots['dish_names'] = ' '.join(dish_names)
        responder.slots['price'] = sum(dish_prices)
        responder.reply('Sure, I have {dish_names} from {restaurant_name} for a total price of '
                        '${price:.2f}. Would you like to place the order?')
        responder.listen()
    else:
        # If the user hasn't selected any dishes yet, prompt the user to make a selection based
        # on the information that is available so far.
        if selected_restaurant:
            # If the user has chosen a restaurant, prompt to order dishes from that restaurant.
            responder.reply('Great, what would you like to order from {restaurant_name}?')
            responder.listen()
        else:
            # If the user has not chosen a restaurant, prompt to do so.
            responder.reply('What restaurant would you like to order from?')
            responder.listen()


# Helper methods for the build_order dialogue state

def _kb_fetch(kb_index, kb_id):
    """
    Retrieve the detailed knowledge base entry for a given ID from the specified index.

    Args:
        index (str): The knowledge base index to query
        id (str): Identifier for a specific entry in the index

    Returns:
        dict: The full knowledge base entry corresponding to the given ID.
    """
    return app.question_answerer.get(index=kb_index, id=kb_id)[0]


def _resolve_dish(dish_entity, selected_restaurant):
    """
    Given a dish entity that could have many potential resolved values (each representing a
    unique item on a specific restaurant's menu), pick the most likely knowledge base entry for
    the dish. The logic for this selection could be arbitrarily complex and take into account
    factors like a dish's popularity, time of the day, user preferences, etc. Here, we simply
    pick the first candidate that is available on the given restaurant's menu.

    Args:
        dish_entity (dict): A dish entity with potentially many candidate resolved values.
        selected_restaurant (dict): Knowledge base entry for the selected restaurant.

    Returns:
        dict: The resolved knowledge base entry corresponding to the given dish entity, augmented
              with additional attribute information like quantity and options.
    """
    # Can't do anything if there are no candidate values to choose from (i.e. if the NLP Entity
    # Resolver couldn't find any potential KB entries that matched with this entity).
    if 'value' not in dish_entity:
        return None

    # Get all the potential resolved values for this dish entity. Each candidate represents a
    # different entry in the knowledge base, corresponding to a specific food item on a specific
    # restaurant's menu. We use information about the selected restaurant to identify the
    # correct dish from this candidate list.
    dish_candidates = [value for value in dish_entity['value']]

    # Get the full knowledge base entry for each of the dish candidates.
    dish_entries = [_kb_fetch('menu_items', dc['id']) for dc in dish_candidates]

    # Choose the first candidate whose restaurant information matches with the provided restaurant.
    dish = next((d for d in dish_entries if d['restaurant_id'] == selected_restaurant['id']), None)

    # Finally, augment the dish entry with any additional information from its child entities.
    if dish and 'children' in dish_entity:
        # Add quantity information. Set to 1 if the entity value can't be resolved.
        dish['quantity'] = next((child['value'][0]['value'] for child in dish_entity['children']
                                if child['type'] == 'sys_number'), 1)
        # Add information about all successfully resolved options.
        options = [_resolve_option(child, dish, selected_restaurant)
                   for child in dish_entity['children'] if child['type'] == 'option']
        dish['options'] = list(filter(None, options))

    # Set default quantity of 1 for the order, if it hasn't been explicitly specified by the user.
    if dish and'quantity' not in dish:
        dish['quantity'] = 1

    return dish


def _resolve_option(option_entity, selected_dish, selected_restaurant):
    """
    Given an option entity that could have many potential resolved values (each representing a
    unique customization option for a specific restaurant's dish), pick the most likely knowledge
    base entry for the option. Here, we choose the first option candidate that is compatible with
    the given dish.

    Args:
        option_entity (dict): An option entity with potentially many candidate resolved values.
        selected_dish (dict): Knowledge base entry for the selected dish.
        selected_restaurant (dict): Knowledge base entry for the selected restaurant.

    Returns:
        dict: The resolved knowledge base entry corresponding to the given option entity.
    """
    # Can't do anything if there are no candidate values to choose from (i.e. if the NLP Entity
    # Resolver couldn't find any potential KB entries that matched with this entity).
    if 'value' not in option_entity:
        return None

    # Get all the potential resolved values for the given option entity. Each candidate represents
    # a different entry in the knowledge base, corresponding to a specific option for a specific
    # restaurant's dish. We use information about the selected dish to identify the correct
    # option from this candidate list.
    option_candidates = [value for value in option_entity['value']]

    # Next, get all the options that are listed for the selected dish on the restaurant's menus.
    all_option_groups = [groups for menu in selected_restaurant['menus']
                         for groups in menu['option_groups']]
    dish_option_groups = [group for group in all_option_groups if group['id'] in
                          set(group_ids for group_ids in selected_dish['option_groups'])]
    dish_options = {option['id']: option for group in dish_option_groups
                    for option in group['options']}

    # Finally, choose the first candidate that's a valid dish option listed on the menu.
    return next((dish_options[oc['id']] for oc in option_candidates if oc['id'] in dish_options),
                None)


def _price_dish(dish):
    """
    Computes the final price for ordering the given dish, taking into account the requested
    quantity and options.

    Args:
        dish (dict): KB entry for a dish, augmented with quantity and options information.

    Returns:
        float: Total price for ordering the requested quantity of this dish with options included.
    """
    total_price = dish['price']
    if 'options' in dish:
        total_price += sum([option.get('price', 0) for option in dish['options']])
    return total_price * dish['quantity']
