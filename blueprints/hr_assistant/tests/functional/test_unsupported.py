import pytest


class TestUnsupported:

    hr_query = [
        ("Do you like pie?", "Hmmm, I don't quite understand, you can ask me something like")
    ]

    @pytest.mark.parametrize("query, response", hr_query)
    def test_unsupported(self, convo, query, response):
        texts = convo.say(query)
        assert response in texts[0]
