import pytest


class TestBuildOrder:

    order_data = [
        ('I want pizza', 'from firetrail', 'Sure, I have 1 order of Margherita Pizza '
                                           '(Gluten Free) from Firetrail Pizza for a '
                                           'total price of $11.00. Would you like to '
                                           'place the order?')
    ]

    @pytest.mark.parametrize("dish, restaurant, response", order_data)
    def test_build_order(self, convo, dish, restaurant, response):
        convo.say(dish)
        texts = convo.say(restaurant)
        assert texts[0] == response
