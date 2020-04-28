# -*- coding: utf-8 -*-
"""This module contains a MindMeld application"""
from mindmeld import Application
from mindmeld.models import entity_features
from mindmeld.markup import process_markup
from mindmeld.core import FormEntity

app = Application(__name__)

__all__ = ['app']


sample_user = {
    'savings' : 500,
    'checking' : 100,
    'credit' : 60,
    'autoPay' : False,
}


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



entity_form = [

    FormEntity(
        entity='account_type',
        role='origin',
        responses=['Sure. Transfer from which account?']),
    FormEntity(
        entity='account_type',
        role='dest',
        responses=['To which account?']),
    FormEntity(
        entity='sys_amount-of-money',
        responses=['And, how much do you want to transfer?'])
    ]
                       

@app.auto_fill(intent='transfer_balances', entity_form=entity_form)
def transfer_balances_handler(request, responder):
	
    for entity in request.entities:
        if entity['type'] == 'account_type':
            if entity['role'] == 'origin':
                responder.slots['origin'] = entity['value'][0]['cname'] or entity['text']
            elif entity['role'] == 'dest':
                responder.slots['dest'] = entity['value'][0]['cname'] or entity['text']
        else:
            print(entity)
            responder.slots['amount'] = entity['text']

    replies = ["All right. So, you're transferring {amount} from your "
               "{origin} to a {dest}. Is that right?"]
    responder.reply(replies)


pay_form = [
    FormEntity(
        entity='credit_amount',
        responses=['Would you like to pay off the minimum or full balance?']),            
    FormEntity(
        entity='sys_amount-of-money',
        responses=['And, how much do you want to transfer?'])
]

@app.handle(intent='pay_creditcard')
def pay_creditcard_handler(request, responder):
    if request.entities:
        for entity in request.entities:
            if entity['type'] == 'credit_amount':
                responder.slots['payment'] = entity['value'][0]['cname'] or entity['text']
                print(entity)
                responder.reply(['Ok we have scheduled your credit card payment for your {payment}'])
                return
            else:
                responder.slots['amount'] = entity['text']    
                responder.reply(['Ok we have scheduled your credit card payment for {amount}]'])
    else:
        responder.params.target_dialogue_state = 'pay_creditcard_handler'
        responder.slots['min'] = round(sample_user['credit'] * .05)
        responder.slots['total_balance'] = sample_user['credit']
        responder.reply(['What amount do you want to pay off? '
            'You can choose to make a minimum payment of ${min} up to the total balance of ${total_balance}'])



@app.handle(intent='setup_autopay')
def setup_autpay_handler(request, responder):
    replies = ['AutoPay has been turned on']
    responder.reply(replies)


balance_form = [
    FormEntity(
        entity='account_type',
        responses=['Sure. for which account?'])
]


@app.auto_fill(intent='check_balances', entity_form=balance_form)
def check_balances_handler(request, responder):
    if request.entities:
        for entity in request.entities:
            if entity['type'] == 'account_type':
                print(entity)
                responder.slots['account'] = entity['text']
                responder.slots['amount'] = sample_user[entity['value'][0]['cname']]
                responder.reply('Balance for {account} account is {amount}')
    






