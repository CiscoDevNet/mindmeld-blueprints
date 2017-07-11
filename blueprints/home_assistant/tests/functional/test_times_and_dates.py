import pytest
from conversational_test import ConversationalTest


class TestTimesAndDates(ConversationalTest):
    test_set_alarm_data = [
        ('set alarm for 6:15am this morning', '06:15:00'),
        ('wake me up tomorrow night at 9:32pm', '21:32:00'),
        ('begin an alarm', 'specific time'),
    ]

    @pytest.mark.parametrize("set_query, expected_response",
                             test_set_alarm_data)
    def test_set_alarm(self, set_query, expected_response):
        texts = self.conv.say(set_query)
        assert expected_response in texts[0]
        self.assert_intent(self.conv, 'set_alarm')

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
    def test_change_alarm(self, set_query, change_query, expected_response):
        self.conv.say(set_query)
        texts = self.conv.say(change_query)
        assert expected_response in texts[0]
        self.assert_intent(self.conv, 'change_alarm')

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
    def test_check_alarm(self, set_query, check_query, expected_response):
        self.conv.say(set_query)
        texts = self.conv.say(check_query)
        assert expected_response in texts[0]
        self.assert_intent(self.conv, 'check_alarm')

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
         'list all alarms')
    ]

    @pytest.mark.parametrize("set_query_1, "
                             "set_query_2, "
                             "cancel_query, "
                             "expected_deleted_token, "
                             "expected_retained_token, "
                             "list_remaining_alarms",
                             test_remove_alarm_data)
    def test_cancel_only_one_alarm(self, set_query_1,
                                   set_query_2,
                                   cancel_query,
                                   expected_deleted_token,
                                   expected_retained_token,
                                   list_remaining_alarms):
        self.conv.say(set_query_1)
        self.conv.say(set_query_2)
        texts = self.conv.say(cancel_query)
        assert expected_deleted_token in texts[0] and "removed" in texts[0]
        self.assert_intent(self.conv, 'remove_alarm')

        texts = self.conv.say(list_remaining_alarms)
        assert expected_retained_token in texts[0] and "removed" \
                                                       not in texts[0]
        self.assert_intent(self.conv, 'check_alarm')

    test_start_timer_data = [
        ('remind me in 5 minutes', '5 minutes'),
        ('activate a new timer', '60 seconds'),
        ('let the timer begin', '60 seconds'),
        ('set a timer for 5 minutes', '5 minutes'),
        ('start a timer for 5 mins', '5 minutes'),
        ('start a timer for 40 seconds', '40 seconds'),
        ('start a timer for 40 secs', '40 seconds')
    ]

    @pytest.mark.parametrize("set_query, expected_response",
                             test_start_timer_data)
    def test_start_timer(self, set_query, expected_response):
        texts = self.conv.say(set_query)
        assert expected_response in texts[0]
        self.assert_intent(self.conv, 'start_timer')
        self.conv.say("clear timers")

    test_clear_time_data = ['clear timer', 'stop my timers', 'pause the timer']

    @pytest.mark.parametrize("clear_query", test_clear_time_data)
    def test_clear_timer(self, clear_query):
        self.conv.say('activate a new timer')
        texts = self.conv.say(clear_query)
        expected_response = 'The current timer has been cancelled'
        assert expected_response in texts[0]
