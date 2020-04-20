# -*- coding: utf-8 -*-
"""This module contains a MindMeld application"""
from mindmeld import Application
from mindmeld.models import entity_features
from mindmeld.markup import process_markup

app = Application(__name__)

__all__ = ['app']


@app.handle(intent='greet')
def greet(request, responder):
    replies = ['Hello there! Welcome to MindMeld Bank', 'Hello, thanks for choosing MindMeld Bank.']
    responder.reply(replies)

@app.handle(intent='lost_creditcard')
def faq_lost_creditcard_handler(request, responder):
    replies = ['If your card is lost or stolen, or you think someone used your account without permission, tell us immediately by calling 1-800-432-3117.']
    responder.reply(replies)

@app.handle(intent='new_creditcard')
def faq_new_creditcard_handler(request, responder):
    replies = ['In order to open a new credit card you must visit our website MindMeldBank.com or visit a local branch.']
    responder.reply(replies)

@app.handle(intent='order_checks')
def faq_order_checks_handler(request, responder):
    replies = ['We have placed an order for a checkbook. To confirm, change quanity of checks, or any other questions please view confirmation email.']
    responder.reply(replies)

@app.handle(intent='routing_number')
def faq_routing_number_handler(request, responder):
    replies = ['Your routing number is 121122676.']
    responder.reply(replies)

@app.handle(intent='fraud_charge')
def faq_fraud_charge_handler(request, responder):
    replies = ['If you think someone used your account without your permission or notice any charge errors, tell us immediately by calling 1-800-MindMeld.']
    responder.reply(replies)

@app.handle(intent='forgot_pin')
def faq_forgot_pin_handler(request, responder):
    replies = ['If you\'ve forgotten your PIN or don\'t have one, please visit your local branch or contact customer service at 1-800-MindMeld to have a new PIN mailed to you.']
    responder.reply(replies)

@app.handle(intent='apply_loan')
def faq_apply_loan_handler(request, responder):
    replies = ['To apply for a loan or any further questions you will need to visit our website MindMeld.com/loans']
    responder.reply(replies)  

@app.handle(intent='activate_creditcard')
def faq_activate_creditcard_handler(request, responder):
    replies = ['You can activate your card by logging into our website and also over the phone. Just call the MindMeld card activation number 1-800-MindMeld. Follow the prompts that will trigger the activation of your card.']
    responder.reply(replies)

@app.handle(default=True)
def default(request, responder):
    replies = ['Sorry, I didn’t get that.', "I'm afraid I don't understand.",
               'Sorry, say that again?', 'Sorry, can you say that again?',
               "I didn't get that. Can you say it again?",
               'Sorry, could you say that again?', 'Sorry, can you tell me again?',
               'Sorry, tell me one more time?', 'Sorry, can you say that again?']
    responder.reply(replies)

def validation(text, entity_type):
    resource_loader = app.app_manager.nlp.resource_loader
    query = process_markup(text, resource_loader.query_factory, {})[1]
    formatted_payload = (query, [query], 0)

    if 'sys_' in entity_type:
        # duckling validation
        extracted_feature = entity_features.extract_numeric_candidate_features()(formatted_payload, {})
    else:
        # gazetteer validation
        gazetter = {'gazetteers': {entity_type: app.app_manager.nlp.resource_loader.get_gazetteer(entity_type)}}
        extracted_feature = entity_features.extract_in_gaz_features()(formatted_payload, gazetter)

    return extracted_feature != {}

@app.handle(targeted_only=True)
def form_fill(request, responder, nlr_form=None):
    nlr = nlr_form or request.frame['slots']
    slot_already_filled = nlr_form is not None

    for elem in nlr:
        entity_type = elem['entity']
        value = elem['value']
        response = elem['response']
        if not value:
            if slot_already_filled:
                responder.params.target_dialogue_state = 'form_fill'
                responder.frame['slots'] = nlr
                responder.reply([response])
                responder.listen()
                return
            else:
                if validation(request.text, entity_type):
                    elem['value'] = request.text
                    slot_already_filled = True
                else:
                    # retry logic
                    app.app_manager.dialogue_manager.reprocess()
    kwargs = {}
    for elem in nlr:
        value = elem['value']
        role = elem['role'] if 'role' in elem else '*'
        entity = elem['entity']

        if entity == 'account_type' and role == 'origin':
            kwargs['origin'] = value
        elif entity == 'account_type' and role == 'dest':
            kwargs['dest'] = value
        elif entity == 'sys_amount-of-money':
            kwargs['amount'] = value

    replies = ["All right. A transfer has been initiated of {amount} from your "
               "{origin} to a {dest}.".format(**kwargs), ]
    responder.reply(replies)
    return
                       

@app.handle(intent='transfer_balances')
def transfer_balances_handler(request, responder):
    nlr_form = [
        {'entity': 'account_type',
         'role': 'origin',
         'response': 'Sure. Transfer from which account?',
         'constraint': 'closed',
         'value': None},
        {'entity': 'account_type',
         'role': 'dest',
         'response': 'To which account?',
         'constraint': 'closed',
         'value': None},
        {'entity': 'sys_amount-of-money',
         'response': 'And, how much do you want to transfer?',
         'constraint': 'closed',
         'value': None}
    ]

    for entity in request.entities:
        entity_type = entity['type']
        role = entity['role']
        value = entity['text']

        for elem in nlr_form:
            if entity_type == elem['entity']:
                if ('role' not in elem) or (role == elem['role']):
                    elem['value'] = value

    form_fill(request, responder, nlr_form)

@app.handle(intent='pay_creditcard')
def pay_creditcard_handler(request, responder):
	    nlr_form = [
        {'entity': 'credit_amount',
         'response': 'Sure. Would you like to pay the minimum or full balance?',
         'value': None},
        {'entity': 'sys_amount-of-money',
         'response': 'And, how much do you want to pay off?',
         'constraint': 'closed',
         'value': None}
    ]

@app.handle(intent='setup_autopay')
def setup_autpay_handler(request, responder):
    replies = ['AutoPay has been turned on']
    responder.reply(replies)

@app.handle(intent='check_balances')
def check_balances_handler(request, responder):
	current_account = next((e for e in request.entities if e['type'] == 'account_type'), None)
	if current_account:
		responder.reply('Balance for' + current_account['account_type'] + ' is 10k')
	else:
		responder.reply('Sure, for which account?')
		responder.listen()






