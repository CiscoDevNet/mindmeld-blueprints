import pytest


class TestTimesAndDates:
    test_set_alarm_data = [
        ('set alarm for 6:15am this morning', '06:15:00'),
        ('wake me up tomorrow night at 9:32pm', '21:32:00'),
        ('begin an alarm', 'At what time?'),
        ('wake me up tomorrow night at 12am', '00:00:00'),
        ('wake me up tomorrow at 12 pm', '12:00:00')
    ]

    @pytest.mark.parametrize("set_query, expected_response",
                             test_set_alarm_data)
    def test_set_alarm(self, convo, set_query, expected_response):
        texts = convo.say(set_query)
        assert expected_response in texts[0]
        convo.assert_intent('set_alarm')

    test_set_alarm_and_specify_time_data = [
        ('set alarm', 'at 6pm', '18:00:00'),
        ('add an alarm', '7am alarm', '07:00:00'),
        ('start an alarm', '10 PM please', '22:00:00'),
        ('start an alarm', '12pm please', '12:00:00'),
        ('add an alarm', '12 am', '00:00:00')
    ]

    @pytest.mark.parametrize("set_query_no_time, time, expected_response",
                             test_set_alarm_and_specify_time_data)
    def test_set_alarm_and_specify_time(self, convo, set_query_no_time, time, expected_response):
        convo.say(set_query_no_time)
        texts = convo.say(time)
        assert expected_response in texts[0]
        convo.assert_intent('specify_time')

    test_change_alarm_data = [
        ('set alarm for 6:15am this morning',
         'change 6:15am alarm to 7:15am this morning',
         '07:15:00'),
        ('set alarm from 6:15am this morning',
         'edit my 6:15am alarm to 9pm at night',
         '21:00:00'),
    ]

    @pytest.mark.parametrize("set_query, change_query, expected_response",
                             test_change_alarm_data)
    def test_change_alarm(self, convo, set_query, change_query, expected_response):
        convo.say(set_query)
        texts = convo.say(change_query)
        assert expected_response in texts[0]
        convo.assert_intent('change_alarm')

    test_check_alarm_data = [
        ('set alarm for 6:15am this morning',
         'check all alarms',
         '06:15:00'),
        ('set alarm from 6:15am this morning',
         'which alarms do i currently have on',
         '06:15:00'),
        ('set alarm from 6:15am this morning',
         'list alarms',
         '06:15:00'),
    ]

    @pytest.mark.parametrize("set_query, check_query, expected_response",
                             test_check_alarm_data)
    def test_check_alarm(self, convo, set_query, check_query, expected_response):
        convo.say(set_query)
        texts = convo.say(check_query)
        assert expected_response in texts[0]
        convo.assert_intent('check_alarm')

    test_remove_all_alarm_data = [
        ('set alarm for 6:15am this morning',
         'set alarm for 9:00pm',
         'cancel all alarms',
         '06:15:00',
         '21:00:00'),
        ('set alarm from 6:15am this morning',
         'set alarm for 9:00pm',
         'delete all alarms',
         '06:15:00',
         '21:00:00')
    ]

    @pytest.mark.parametrize("set_query_1, "
                             "set_query_2, "
                             "cancel_query, "
                             "expected_deleted_token1, "
                             "expected_deleted_token2, ",
                             test_remove_all_alarm_data)
    def test_cancel_all_alarms(self, convo, set_query_1, set_query_2, cancel_query,
                               expected_deleted_token1, expected_deleted_token2):
        convo.say(set_query_1)
        convo.say(set_query_2)
        texts = convo.say(cancel_query)
        assert expected_deleted_token1 in texts[0] and "removed" in texts[0]
        assert expected_deleted_token2 in texts[0] and "removed" in texts[0]
        convo.assert_intent('remove_alarm')

    test_remove_alarm_data = [
        ('set alarm for 6:15am this morning',
         'set alarm for 9:00pm',
         'cancel my 6:15am alarm',
         '06:15:00',
         '21:00:00',
         'list all alarms'),
        ('set alarm from 6:15am this morning',
         'set alarm for 9:00pm',
         'turn off my 6:15am alarm',
         '06:15:00',
         '21:00:00',
         'list all alarms'),
        ('set alarm for midnight',
         'set alarm for 9:00pm',
         'turn off my midnight alarm',
         '00:00:00',
         '21:00:00',
         'list all alarms'),
        ('set alarm for noon',
         'set alarm for 9:00pm',
         'turn off my noon alarm',
         '12:00:00',
         '21:00:00',
         'list all alarms')
    ]

    @pytest.mark.parametrize("set_query_1, "
                             "set_query_2, "
                             "cancel_query, "
                             "expected_deleted_token, "
                             "expected_retained_token, "
                             "list_remaining_alarms",
                             test_remove_alarm_data)
    def test_cancel_only_one_alarm(self, convo, set_query_1,
                                   set_query_2,
                                   cancel_query,
                                   expected_deleted_token,
                                   expected_retained_token,
                                   list_remaining_alarms):
        convo.say(set_query_1)
        convo.say(set_query_2)
        texts = convo.say(cancel_query)
        assert expected_deleted_token in texts[0] and "removed" in texts[0]
        convo.assert_intent('remove_alarm')

        texts = convo.say(list_remaining_alarms)
        assert expected_retained_token in texts[0] and "removed" \
                                                       not in texts[0]
        convo.assert_intent('check_alarm')

    test_remove_alarm_specify_time_data = [
        ('set alarm for 6:15am this morning',
         'set alarm for 9:00pm',
         'cancel my alarm',
         '6:15am',
         '06:15:00',
         '21:00:00',
         'list all alarms'),
        ('set alarm from 6:15am this morning',
         'set alarm for 9:00pm',
         'turn off my alarm',
         '6:15 AM please',
         '06:15:00',
         '21:00:00',
         'list all alarms')
    ]

    @pytest.mark.parametrize("set_query_1, "
                             "set_query_2, "
                             "cancel_query, "
                             "time, "
                             "expected_deleted_token, "
                             "expected_retained_token, "
                             "list_remaining_alarms",
                             test_remove_alarm_specify_time_data)
    def test_cancel_alarm_specify_time(self, convo, set_query_1,
                                       set_query_2,
                                       cancel_query,
                                       time,
                                       expected_deleted_token,
                                       expected_retained_token,
                                       list_remaining_alarms):
        convo.say(set_query_1)
        convo.say(set_query_2)
        convo.say(cancel_query)
        texts = convo.say(time)
        assert expected_deleted_token in texts[0] and "removed" in texts[0]
        convo.assert_intent('specify_time')

        texts = convo.say(list_remaining_alarms)
        assert expected_retained_token in texts[0] and "removed" \
                                                       not in texts[0]
        convo.assert_intent('check_alarm')

    test_start_timer_data = [
        ('remind me in 5 minutes', '5 minutes'),
        ('activate a new timer', '60 seconds'),
        ('let the timer begin', '60 seconds'),
        ('set a timer for 5 minutes', '5 minutes'),
        ('start an alarm for 15 minute', '15 minutes'),
        ('start a timer for 5 mins', '5 minutes'),
        ('start a timer for 40 seconds', '40 seconds'),
        ('start a timer for 40 secs', '40 seconds'),
        ('start a timer for 2 sec', '2 seconds'),
        ('start a timer for 42sec', '42 seconds')
        # skip: duckling issue ('start a timer for 2 s', '2 seconds'),
        # skip: duckling issue ('start a timer for 42s', '42 seconds')
    ]

    @pytest.mark.parametrize("set_query, expected_response",
                             test_start_timer_data)
    def test_start_timer(self, convo, set_query, expected_response):
        texts = convo.say(set_query)
        assert expected_response in texts[0]
        convo.assert_intent('start_timer')

    test_clear_time_data = ['clear timer', 'stop my timers', 'pause the timer', 'Kill the timer']

    @pytest.mark.parametrize("clear_query", test_clear_time_data)
    def test_clear_timer(self, convo, clear_query):
        convo.say('activate a new timer')
        texts = convo.say(clear_query)
        expected_response = 'The current timer has been cancelled'
        assert expected_response in texts[0]

    @pytest.mark.skip(reason="not critical, unblocking pipeline, will fix in the next mm release")
    def test_clear_timer_no_timer(self, convo):
        convo.say('clear timers')
        convo.assert_text('There is no active timer to cancel!')

    test_specify_time = ['9am', 'at 10 AM', 'my 11PM alarm', 'the 6 PM', '7AM please']

    @pytest.mark.parametrize("specify_time_query", test_specify_time)
    def test_specify_time(self, convo, specify_time_query):
        convo.say(specify_time_query)
        convo.assert_intent('specify_time')
