# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the screening questions
that come inside a dialogue flow in the MindMeld screening app blueprint
"""
from .root import app

import screening_app.prediabetes as pd
from screening_app.prediabetes_questions import prediabetes_questions


@app.dialogue_flow(domain='prediabetes_screening', intent='opt_in')
def screen_prediabetes(request, responder):
    """
    If the user accepts the sceening, begin a dialogue flow.
    """
    # Clear the dialogue frame to start fresh
    responder.frame = {}

    first_question = prediabetes_questions[pd.Q_AGE]

    responder.frame['previous_question'] = first_question['text']
    responder.frame['previous_question_number'] = pd.Q_AGE
    responder.frame['screening'] = dict()

    responder.params.allowed_intents = ('prediabetes_screening.answer_age', 'greetings.exit')

    responder.reply(first_question['text'])
    responder.listen()


@screen_prediabetes.handle(intent='answer_age')
def set_age_send_next(request, responder):
    """
    When the user provides their age, save the answer and move to the next question.
    """
    allowed_intents = ('prediabetes_screening.answer_gender', 'greetings.exit')
    process_answer_with_entity(request, responder, pd.Q_AGE, allowed_intents)


@screen_prediabetes.handle(intent='answer_gender')
def set_gender_send_next(request, responder):
    """
    When the user provides their gender, save the answer and move to the next question.
    """
    allowed_intents = (
        'prediabetes_screening.answer_yes',
        'prediabetes_screening.answer_no',
        'prediabetes_screening.answer_yes_gestational',
        'greetings.exit'
        )
    process_answer_with_entity(request, responder, pd.Q_GENDER, allowed_intents)


@screen_prediabetes.handle(intent='answer_yes_gestational')
def confirm_gestational_send_next(request, responder):
    """
    When the user implicitly confirms having had gestational diabetes,
    save the answer and move to the next question.
    """
    allowed_intents = (
            'prediabetes_screening.answer_yes',
            'prediabetes_screening.answer_no',
            'prediabetes_screening.answer_yes_family',
            'greetings.exit'
        )
    process_implied_confirmation(request, responder, pd.Q_GEST, allowed_intents)


@screen_prediabetes.handle(intent='answer_yes_family')
def confirm_family_send_next(request, responder):
    """
    When the user implicitly confirms having family with diabetes,
    save the answer and move to the next question.
    """
    allowed_intents = (
            'prediabetes_screening.answer_yes',
            'prediabetes_screening.answer_no',
            'prediabetes_screening.answer_yes_hbp',
            'greetings.exit'
        )
    process_implied_confirmation(request, responder, pd.Q_FAM, allowed_intents)


@screen_prediabetes.handle(intent='answer_yes_hbp')
def confirm_hbp_send_next(request, responder):
    """
    When the user implicitly confirms having high blood pressure,
    save the answer and move to the next question.
    """
    allowed_intents = (
            'prediabetes_screening.answer_yes',
            'prediabetes_screening.answer_no',
            'prediabetes_screening.answer_yes_active',
            'greetings.exit'
        )
    process_implied_confirmation(request, responder, pd.Q_BP, allowed_intents)


@screen_prediabetes.handle(intent='answer_yes_active')
def confirm_active_send_next(request, responder):
    """
    When the user implicitly confirms being physically active,
    save the answer and move to the next question.
    """
    allowed_intents = ('prediabetes_screening.answer_height', 'greetings.exit')
    process_implied_confirmation(request, responder, pd.Q_ACT, allowed_intents)


@screen_prediabetes.handle(intent='answer_height')
def set_height_send_next(request, responder):
    """
    When the user provides their height, save the answer and move to the next question.
    """
    allowed_intents = ('prediabetes_screening.answer_weight', 'greetings.exit')
    process_answer_with_entity(request, responder, pd.Q_HEIGHT, allowed_intents)


@screen_prediabetes.handle(intent='answer_weight')
def set_weight_send_next(request, responder):
    """
    When the user provides their weight, save the answer and move to the next question.
    """
    process_answer_with_entity(request, responder, pd.Q_WEIGHT)


@app.handle(intent='answer_yes')
@screen_prediabetes.handle(intent='answer_yes')
def confirm_send_next(request, responder):
    """
    If the user accepts the sceening, begin a dialogue flow, or if the user
    answers with an explicit yes to a question, save the answer and move to the next question.
    """
    if 'previous_question_number' not in responder.frame:
        # Start questionnaire
        screen_prediabetes(request, responder)
        return

    process_binary(request, responder, True)


@app.handle(intent='answer_no')
@screen_prediabetes.handle(intent='answer_no')
def negate_send_next(request, responder):
    """
    If the user rejects the screening, gracefully exit the conversation, or if the
    user answers no to a question, save the answer and move to the next question.
    """
    if 'previous_question_number' not in responder.frame:
        # Clear the dialogue frame to start afresh for the next user request.
        responder.frame = {}
        responder.reply(['Estamos para servirle. Gracias por su visita.'])
        return

    process_binary(request, responder, False)


@screen_prediabetes.handle(intent='opt_in')
def screen_prediabetes_in_flow_handler(request, responder):
    screen_prediabetes(request, responder)


@screen_prediabetes.handle(default=True)
def default_handler(request, responder):
    responder.frame['count'] = responder.frame.get('count', 0) + 1
    if responder.frame['count'] <= 3:
        question_text = responder.frame['previous_question']
        responder.reply(question_text)
        responder.listen()
    else:
        responder.reply('Disculpe, no le he podido entender. Por favor intente de nuevo.')
        responder.exit_flow()


def process_answer_with_entity(request, responder, question_number, allowed_intents=()):
    previous_question_number = responder.frame['previous_question_number']
    question = prediabetes_questions[question_number]

    if question_number == previous_question_number:
        if question_number == pd.Q_AGE:
            entity = next((e for e in request.entities if e['type'] == 'sys_number'), None)
            answer = entity['value'][0]['value'] if entity else None
        elif question_number == pd.Q_GENDER:
            entity = next((e for e in request.entities if e['type'] == 'gender'), None)
            answer = entity['value'][0]['cname'] if entity else None
        elif question_number == pd.Q_HEIGHT:
            answer = pd.height_converter(request)
        elif question_number == pd.Q_WEIGHT:
            answer = pd.weight_converter(request)
        else:
            answer = None

        if answer:
            responder.params.allowed_intents = allowed_intents
            set_answer_send_next(request, responder, answer)
            return
        else:
            # No sys_number entity was provided. Re-ask question.
            question_text = question['text']
    else:
        # Answer is out of questionnaire flow. Re-ask question.
        question_text = responder.frame['previous_question']

    responder.frame['count'] = responder.frame.get('count', 0) + 1

    if responder.frame['count'] <= 3:
        responder.reply(question_text)
        responder.listen()
    else:
        responder.reply('Disculpe, no le he podido entender. Por favor intente de nuevo.')
        responder.exit_flow()


def process_implied_confirmation(request, responder, question_number, allowed_intents=()):
    previous_question_number = responder.frame['previous_question_number']

    if question_number == previous_question_number:
        responder.params.allowed_intents = allowed_intents
        set_answer_send_next(request, responder, True)
        return
    else:
        # Answer is out of questionnaire flow. Re-ask question.
        question_text = responder.frame['previous_question']

        responder.frame['count'] = responder.frame.get('count', 0) + 1

        if responder.frame['count'] <= 3:
            responder.reply(question_text)
            responder.listen()
        else:
            responder.reply('Disculpe, no le he podido entender. Por favor intente de nuevo.')
            responder.exit_flow()


def process_binary(request, responder, answer):
    previous_question_number = responder.frame['previous_question_number']
    question = prediabetes_questions[previous_question_number]

    question_type = question['type']

    if question_type == 'Binary':
        set_answer_send_next(request, responder, answer)
        return
    else:
        # Answer is out of questionnaire flow. Re-ask question.
        question_text = responder.frame['previous_question']

        responder.frame['count'] = responder.frame.get('count', 0) + 1

        if responder.frame['count'] <= 3:
            responder.reply(question_text)
            responder.listen()
        else:
            responder.reply('Disculpe, no le he podido entender. Por favor intente de nuevo.')
            responder.exit_flow()


def set_answer_send_next(request, responder, answer):
    previous_question_number = responder.frame['previous_question_number']
    responder.frame['screening'][previous_question_number] = answer
    responder.frame['count'] = 0

    try:
        if responder.frame['screening'][previous_question_number] == 'Hombre':
            # Skip the next question
            question_number = previous_question_number + 2
        else:
            question_number = previous_question_number + 1

        question = prediabetes_questions[question_number]

        responder.frame['previous_question'] = question['text']
        responder.frame['previous_question_number'] = question_number
        responder.reply(question['text'])
        responder.listen()

        return
    except IndexError:
        # No more questions. Reply with results.
        if pd.calculate_risk_score(responder.frame['screening']):
            responder.reply(pd.HIGH_RISK_MSG)
        else:
            responder.reply(pd.LOW_RISK_MSG)

        responder.frame = {}
        responder.exit_flow()
        return
