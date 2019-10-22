# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'faq' domain in
the MindMeld HR assistant blueprint application
"""

from .root import app


@app.handle(intent='generic')
def generic(request, responder):
    responder.reply("Sure, what do you want to know?")
    responder.params.target_dialogue_state = 'all_topics'
    responder.listen()


@app.handle(intent='all_topics')
def all_topics(request, responder):
    query = request.text
    answers = app.question_answerer.get(index='hr_faq_data', query_type='text', question=query,
                                        answer=query)
    if answers:
        reply = ['Here is the top result:', answers[0]['question'], answers[0]['answer']]
        responder.reply('\n'.join(reply))
    else:
        responder.reply("I'm sorry, I couldn't find an answer to your question")
