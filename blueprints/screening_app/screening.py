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
    previous_question_number = responder.frame['previous_question_number']
    age_question = prediabetes_questions[pd.Q_AGE]

    if pd.Q_AGE == previous_question_number:
        number_entity = next((e for e in request.entities if e['type'] == 'sys_number'), None)
        if number_entity:
            responder.params.allowed_intents = ('prediabetes_screening.answer_gender',
                                                'greetings.exit')
            set_answer_send_next(request, responder, number_entity['value'][0]['value'])
            return
        else:
            # No age was provided. Re-ask question.
            question_text = age_question['text']
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


@screen_prediabetes.handle(intent='answer_gender')
def set_gender_send_next(request, responder):
    """
    When the user provides their gender, save the answer and move to the next question.
    """
    previous_question_number = responder.frame['previous_question_number']
    gender_question = prediabetes_questions[pd.Q_GENDER]

    if pd.Q_GENDER == previous_question_number:
        gender_entity = next((e for e in request.entities if e['type'] == 'gender'), None)
        if gender_entity:
            responder.params.allowed_intents = (
                'prediabetes_screening.answer_yes',
                'prediabetes_screening.answer_no',
                'prediabetes_screening.answer_yes_gestational',
                'greetings.exit'
            )
            set_answer_send_next(request, responder, gender_entity['value'][0]['cname'])
            return
        else:
            # No gender was provided. Re-ask question.
            question_text = gender_question['text']
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


@screen_prediabetes.handle(intent='answer_yes_gestational')
def confirm_gestational_send_next(request, responder):
    """
    When the user implicitly confirms having had gestational diabetes,
    save the answer and move to the next question.
    """
    previous_question_number = responder.frame['previous_question_number']

    if pd.Q_GEST == previous_question_number:
        responder.params.allowed_intents = (
            'prediabetes_screening.answer_yes',
            'prediabetes_screening.answer_no',
            'prediabetes_screening.answer_yes_family',
            'greetings.exit'
        )
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


@screen_prediabetes.handle(intent='answer_yes_family')
def confirm_family_send_next(request, responder):
    """
    When the user implicitly confirms having family with diabetes,
    save the answer and move to the next question.
    """
    previous_question_number = responder.frame['previous_question_number']

    if pd.Q_FAM == previous_question_number:
        responder.params.allowed_intents = (
            'prediabetes_screening.answer_yes',
            'prediabetes_screening.answer_no',
            'prediabetes_screening.answer_yes_hbp',
            'greetings.exit'
        )
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


@screen_prediabetes.handle(intent='answer_yes_hbp')
def confirm_hbp_send_next(request, responder):
    """
    When the user implicitly confirms having high blood pressure,
    save the answer and move to the next question.
    """
    previous_question_number = responder.frame['previous_question_number']

    if pd.Q_BP == previous_question_number:
        responder.params.allowed_intents = (
            'prediabetes_screening.answer_yes',
            'prediabetes_screening.answer_no',
            'prediabetes_screening.answer_yes_active',
            'greetings.exit'
        )
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


@screen_prediabetes.handle(intent='answer_yes_active')
def confirm_active_send_next(request, responder):
    """
    When the user implicitly confirms being physically active,
    save the answer and move to the next question.
    """
    previous_question_number = responder.frame['previous_question_number']

    if pd.Q_ACT == previous_question_number:
        responder.params.allowed_intents = ('prediabetes_screening.answer_height', 'greetings.exit')
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


@screen_prediabetes.handle(intent='answer_height')
def set_height_send_next(request, responder):
    """
    When the user provides their height, save the answer and move to the next question.
    """
    previous_question_number = responder.frame['previous_question_number']
    height_question = prediabetes_questions[pd.Q_HEIGHT]

    if pd.Q_HEIGHT == previous_question_number:
        height = pd.height_converter(request)
        if height:
            responder.params.allowed_intents = ('prediabetes_screening.answer_weight',
                                                'greetings.exit')
            set_answer_send_next(request, responder, height)
            return
        else:
            # No height was provided. Re-ask question.
            question_text = height_question['text']
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


@screen_prediabetes.handle(intent='answer_weight')
def set_weight_send_next(request, responder):
    """
    When the user provides their weight, save the answer and move to the next question.
    """
    previous_question_number = responder.frame['previous_question_number']
    weight_question = prediabetes_questions[pd.Q_WEIGHT]

    if pd.Q_WEIGHT == previous_question_number:
        weight = pd.weight_converter(request)
        if weight:
            set_answer_send_next(request, responder, weight)
            return
        else:
            # No age was provided. Re-ask question.
            question_text = weight_question['text']
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

    previous_question_number = responder.frame['previous_question_number']
    question = prediabetes_questions[previous_question_number]

    question_type = question['type']

    if question_type == 'Binary':
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

    previous_question_number = responder.frame['previous_question_number']
    question = prediabetes_questions[previous_question_number]

    question_type = question['type']

    if question_type == 'Binary':
        set_answer_send_next(request, responder, False)
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

        responder.exit_flow()
        return
