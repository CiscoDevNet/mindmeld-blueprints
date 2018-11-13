def test_unknown(convo):
    convo.say("what was the soviet union?")
    convo.assert_text("Sorry, not sure what you meant there.")
