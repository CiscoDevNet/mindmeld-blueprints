import pytest


class TestSmartHome:

    # close_door intent
    close_door_data = [
        ('close the door', ''),
        ('close the front door', 'front'),
        ('shut the garage door', 'garage'),
        ('shut back door', 'back'),
        ('close all doors', 'all')
    ]

    @pytest.mark.parametrize("query, location", close_door_data)
    def test_close_door(self, convo, query, location):
        texts = convo.say(query)
        assert location in texts[0].lower()
        convo.assert_intent('close_door')

    # open_door intent
    open_door_data = [
        ('open the door', ''),
        ('open the back door', 'back'),
        ('open basement door', 'basement'),
        ('please open the bedroom door', 'bedroom'),
        ('open all the doors', 'all')
    ]

    @pytest.mark.parametrize("query, location", open_door_data)
    def test_open_door(self, convo, query, location):
        texts = convo.say(query)
        assert location in texts[0].lower()
        convo.assert_intent('open_door')

    # lock_door intent
    lock_door_data = [
        ('lock the door', ''),
        ('lock the front door', 'front'),
        ('lock garage door', 'garage'),
        ('please lock the back door', 'back'),
        ('lock all the doors', 'all')
    ]

    @pytest.mark.parametrize("query, location", lock_door_data)
    def test_lock_door(self, convo, query, location):
        texts = convo.say(query)
        assert location in texts[0].lower()
        convo.assert_intent('lock_door')

    # unlock_door intent
    unlock_door_data = [
        ('unlock the door', ''),
        ('unlock the front door', 'front'),
        ('unlock garage door', 'garage'),
        ('please unlock the back door', 'back'),
        ('unlock all the doors', 'all')
    ]

    @pytest.mark.parametrize("query, location", unlock_door_data)
    def test_unlock_door(self, convo, query, location):
        texts = convo.say(query)
        assert location in texts[0].lower()
        convo.assert_intent('unlock_door')

    # check_door intent
    check_door_data = [
        ("please check the door", ""),
        ("is the front door open", "front"),
        ("what's the status of the garage door", "garage"),
        ("is the back door closed", "back"),
    ]

    @pytest.mark.parametrize("query, location", check_door_data)
    def test_check_door_thermostat(self, convo, query, location):
        texts = convo.say(query)
        assert location in texts[0].lower()
        convo.assert_intent('check_door')

    # check_thermostat intent
    check_thermostat_data = [
        ("check thermostat", ''),
        ("what's the thermostat at", ''),
        ("check bedroom thermostat", 'bedroom'),
        ("tell me the kitchen temperature", 'kitchen')
    ]

    @pytest.mark.parametrize("query, location", check_thermostat_data)
    def test_check_thermostat(self, convo, query, location):
        texts = convo.say(query)
        assert location in texts[0].lower()
        convo.assert_intent('check_thermostat')

    # set_thermostat intent
    set_thermostat_data = [
        ("Set the thermostat to 73", "home", "73"),
        ("Make the living room 68 degrees", "living room", "68"),
        ("Change the temperature to 78 degrees", "home", "78"),
        ("Adjust the kitchen thermostat to 66 degrees", "kitchen", "66")
    ]

    @pytest.mark.parametrize("query, location, temperature", set_thermostat_data)
    def test_set_thermostat(self, convo, query, location, temperature):
        texts = convo.say(query)
        assert location in texts[0].lower()
        assert temperature in texts[0].lower()
        convo.assert_intent('set_thermostat')

    # turn_down_thermostat intent
    turn_down_thermostat_data = [
        ("Turn down the thermostat by 2", "home"),
        ("Lower the temperature in the kitchen by 5", "kitchen"),
        ("Make it cooler in here", "home"),
        ("Decrease bedroom thermostat by 3", "bedroom")
    ]

    @pytest.mark.parametrize("query, location", turn_down_thermostat_data)
    def test_turn_down_thermostat(self, convo, query, location):
        texts = convo.say(query)
        assert location in texts[0].lower()
        convo.assert_intent('turn_down_thermostat')

    # turn_up_thermostat intent
    turn_up_thermostat_data = [
        ("Turn up the thermostat by 2", "home"),
        ("Raise the temperature in the kitchen by 5", "kitchen"),
        ("Make it hotter in here", "home"),
        ("Increase bedroom thermostat by 3", "bedroom")
    ]

    @pytest.mark.parametrize("query, location", turn_up_thermostat_data)
    def test_turn_up_thermostat(self, convo, query, location):
        texts = convo.say(query)
        assert location in texts[0].lower()
        convo.assert_intent('turn_up_thermostat')

    # turn_on_thermostat intent
    turn_on_thermostat_data = [
        ("thermostat on", ''),
        ("turn on the thermostat", ''),
        ("can you turn on the bedroom thermostat", 'bedroom'),
        ("turn on the kitchen ac", 'kitchen')
    ]

    @pytest.mark.parametrize("query, location", turn_on_thermostat_data)
    def test_turn_on_thermostat(self, convo, query, location):
        texts = convo.say(query)
        assert location in texts[0].lower()
        convo.assert_intent('turn_on_thermostat')

    # turn_off_thermostat intent
    turn_off_thermostat_data = [
        ("thermostat off", ''),
        ("turn off the thermostat", ''),
        ("can you turn off the bedroom thermostat", 'bedroom'),
        ("turn off the kitchen ac", 'kitchen')
    ]

    @pytest.mark.parametrize("query, location", turn_off_thermostat_data)
    def test_turn_off_thermostat(self, convo, query, location):
        texts = convo.say(query)
        assert location in texts[0].lower()
        convo.assert_intent('turn_off_thermostat')

    # check_lights intent
    check_lights_data = [
        ("what lights are on", ""),
        ("is the bedroom light on", "bedroom"),
        ("are any lights on in the kitchen", "kitchen"),
        ("check the back lights please", "back"),
    ]

    @pytest.mark.parametrize("query, location", check_lights_data)
    def test_check_lights(self, convo, query, location):
        texts = convo.say(query)
        assert location in texts[0].lower()
        convo.assert_intent('check_lights')

    #
    # turn_lights_on intent
    turn_lights_on_data = [
        ("lights on", ''),
        ("turn on the living room lights", ''),
        ("switch on the kitchen lights", 'kitchen'),
        ("turn on all the lights", 'all')
    ]

    @pytest.mark.parametrize("query, location", turn_lights_on_data)
    def test_turn_on_lights(self, convo, query, location):
        texts = convo.say(query)
        assert location in texts[0].lower()
        convo.assert_intent('turn_lights_on')

    # turn_lights_off intent
    turn_lights_off_data = [
        ("lights off", ''),
        ("turn off the living room lights", ''),
        ("switch off the kitchen lights", 'kitchen'),
        ("turn off all the lights", 'all')
    ]

    @pytest.mark.parametrize("query, location", turn_lights_off_data)
    def test_turn_off_lights(self, convo, query, location):
        texts = convo.say(query)
        assert location in texts[0].lower()
        convo.assert_intent('turn_lights_off')

    # turn_appliance_on intent
    turn_appliance_on_data = [
        ("toaster on", 'toaster', ''),
        ("turn on the living room tv", 'tv', 'living room'),
        ("start the dishwasher", 'dishwasher', ''),
        ("turn on the kitchen oven", 'oven', 'kitchen')
    ]

    @pytest.mark.parametrize("query, appliance, location", turn_appliance_on_data)
    def test_turn_appliance_on(self, convo, query, appliance, location):
        texts = convo.say(query)
        assert appliance in texts[0].lower()
        assert location in texts[0].lower()
        convo.assert_intent('turn_appliance_on')

    # turn_appliance_off intent
    turn_appliance_off_data = [
        ("toaster off", 'toaster', ''),
        ("turn off the living room tv", 'tv', 'living room'),
        ("stop the dishwasher", 'dishwasher', ''),
        ("turn off the kitchen oven", 'oven', 'kitchen')
    ]

    @pytest.mark.parametrize("query, appliance, location", turn_appliance_off_data)
    def test_turn_appliance_off(self, convo, query, appliance, location):
        texts = convo.say(query)
        assert appliance in texts[0].lower()
        assert location in texts[0].lower()
        convo.assert_intent('turn_appliance_off')

    # specify_location_intent
    specify_location_data = [
        ("preheat the oven", "in the kitchen", "Ok. The kitchen oven has been turned on."),
        ("preheat the oven", "the only one", "I'm sorry, I wasn't able to recognize that location, could you try again?")  # noqa: E501
    ]

    @pytest.mark.parametrize("query1, query2, expected", specify_location_data)
    def test_specify_location(self, convo, query1, query2, expected):
        convo.say(query1)
        texts = convo.say(query2)
        assert texts[0] == expected

    # close_door intent
    close_door_data = [
        ('close the door', 'kitchen', 'Ok. The kitchen door has been closed.')
    ]

    @pytest.mark.parametrize("query, location, response", close_door_data)
    def test_close_door_followup(self, convo, query, location, response):
        convo.say(query)
        texts = convo.say(location)
        assert texts[0] == response
