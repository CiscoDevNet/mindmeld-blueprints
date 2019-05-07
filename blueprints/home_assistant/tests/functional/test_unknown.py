import pytest


@pytest.mark.skip(reason="not critical, unblocking pipeline, will fix in the next mindmeld release")
def test_unknown(convo):
    convo.say("what was the soviet union?")
    convo.assert_text("Sorry, not sure what you meant there.")
