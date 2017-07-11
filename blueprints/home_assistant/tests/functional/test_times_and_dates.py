import pytest
from conversational_test import ConversationalTest, load_conversation


class TestTimesAndDates(ConversationalTest):

    # start_timer intent
    start_timer_data = [
        ('set a timer for 5 minutes', '5 minutes'),
        ('start a timer for 5 mins', '5 minutes'),
        ('start a timer for 40 seconds', '40 seconds'),
        ('start a timer for 40 secs', '40 seconds')
    ]

    @pytest.mark.parametrize("query, duration", start_timer_data)
    def test_start_timer(self, query, duration):
        conv = load_conversation()
        texts = conv.say(query)
        assert duration in texts[0].lower()
        self.assert_intent(conv, 'start_timer')
