# -*- coding: utf-8 -*-
"""This module contains a MindMeld application"""
from mindmeld import Application
from mindmeld.models import entity_features
from mindmeld.markup import process_markup
from mindmeld.core import FormEntity
import random
import json

app = Application(__name__)

__all__ = ['app']

#User data and helper functions

user_data = {}

sample_users = {
    "johndoe123" : 0,
    "larry_l12" : 1,
    "splashbro30" : 2,
}

def _pull_data(request):
    with open('banking_blueprint/data/sample_user_data.json') as f:
        global user_data 
        data = json.load(f)
        if request.context.get('user_name'):
            user_name = request.context.get('user_name')
            user = sample_users[user_name]
        else:
            user = random.choice([0, 1, 2])

        user_data = data[user]

def _get(key):
    return user_data[key]

def _put(key, value):
    global user_data
    user_data[key] = value

def check_value(responder):
    return _get(responder.slots['origin']) >= responder.slots['amount']

#Slot filling forms 

entity_form = {
    'entities':[
        FormEntity(
            entity='account_type',
            role='origin',
            responses=['Sure. Transfer from which account - checking or savings?']),
        FormEntity(
            entity='account_type',
            role='dest',
            responses=['To which account - checking or savings?']),
        FormEntity(
            entity='sys_amount-of-money',
            responses=['And, how much do you want to transfer?'])

        ],
        'exit_keys' : ['cancel', 'restart', 'exit', 'reset', 'no', 'nevermind', 'stop', 'back', 'help', 'stpo it', 'go back'
            'new task', 'other', 'return'],
        'exit_msg' : 'A few other banking tasks you can try are, reporting a fraudelent charge and setting up AutoPay',
        'max_retries' : 1
}

balance_form = {
    'entities':[
    FormEntity(
        entity='account_type',
        responses=['Sure. for which account - checkings, savings, or credit?'])
    ],
    'exit_keys' : ['cancel', 'restart', 'exit', 'reset', 'no', 'nevermind', 'stop', 'back', 'help', 'stop it', 'go back'
            'new task', 'other', 'return'],
    'exit_msg' : 'A few other banking tasks you can try are, ordering checks and paying bills',
    'max_retries' : 1
}

#Dialogue state handlers 

@app.handle(intent='greet')
def greet(request, responder):
    if not user_data: 
        _pull_data(request)
    responder.slots['name'] = _get('first_name')
    replies = ['Hi {name}, How can I help with your banking tasks? You can try transferring money between accounts or paying a bill.',
     'Hello {name}, thanks for choosing MindMeld Bank. You can do things like, ask for your routing number, order checks, and check bill due dates.',
     'Welome to MindMeld Bank {name}, How can I help with your banking tasks? You can try reporting a fraud charge or a lost credit card.',
     'Thanks for using MindMeld Bank {name}! What would you like to do today? A few things I can help with are, checking balances, paying off your credit card, and setting up a new card.']
    responder.reply(replies)

@app.handle(intent='exit')
def exit(request, responder):
    responder.reply(['Bye', 'Goodbye', 'Have a nice day.'])

@app.handle(intent='help')
def help(request, responder):
    responder.reply(['A few things I can help you with are, checking balances, paying off your credit card, and setting up a new card.', 'Looks like you need help have you tried, ask for your routing number, ordering checks, and checking bill due dates.', 
        'You can try reporting a fraud charge or a lost credit card.', 'Need some suggestions, try ordering some checks by saying \'order checks\', or check your balance for savings, checking, or credit account by saying \'check balance\' and then the account name',
        'A few of things you can ask me are, \'how to apply for a loan\', \'what is my routing number\', and \'can you pay my credit card bill\'', 
        'Try asking about card activation or reporting a stolen card', 
        'A few things I can help with are, reporting a fraudelent charge, paying off your credit card, and resetting your pin.', 
        'Have you tried asking for your routing number yet, you can do that by saying \'what is my routing number\'.', 
        'Have you tried making a transfer, you can do that by saying \'transfer money\'.',
        'Need some suggestions?, you can ask me something like \'lost my pin\', \'card is stolen\', or \'setup a new card\'.'])

@app.handle(intent='lost_creditcard')
def faq_lost_creditcard_handler(request, responder):
    if not user_data: 
        _pull_data(request)
    responder.slots['email'] = _get('email')
    replies = ['I\'ve noted that your card may have been lost or stolen. Please follow up immediately by calling 1-800-432-3117 or clicking the link in the email sent to {email}']
    responder.reply(replies)


@app.handle(intent='new_creditcard')
def faq_new_creditcard_handler(request, responder):
    if not user_data: 
        _pull_data(request)
    responder.slots['email'] = _get('email')
    replies = ['An email has been sent to {email} with the available credit card offers for you. You may also visit a local branch and talk to a MindMeld teller.']
    responder.reply(replies)


@app.handle(intent='order_checks')
def faq_order_checks_handler(request, responder):
    if not user_data: 
        _pull_data(request)
    responder.slots['email'] = _get('email')
    replies = ['We have placed an order for a checkbook, which contain 50 checks. To confirm, change quanity of checks, or any other questions please view the link in the email sent to {email}.']
    responder.reply(replies)


@app.handle(intent='routing_number')
def faq_routing_number_handler(request, responder):
    if not user_data: 
        _pull_data(request)
    responder.slots['routing'] = _get('routing')
    replies = ['Your routing number is {routing}.']
    responder.reply(replies)


@app.handle(intent='fraud_charge')
def faq_fraud_charge_handler(request, responder):
    if not user_data: 
        _pull_data(request)
    responder.slots['email'] = _get('email')
    replies = ['We have placed a hold on your card to avoid any further fraudelent activity. An email has been sent to {email} on how to reactivate your card']
    responder.reply(replies)


@app.handle(intent='forgot_pin')
def faq_forgot_pin_handler(request, responder):
    if not user_data: 
        _pull_data(request)
    responder.slots['email'] = _get('email')
    replies = ['We have sent you an email at {email} with the steps on how to resest or recover your pin.']
    responder.reply(replies)


@app.handle(intent='apply_loan')
def faq_apply_loan_handler(request, responder):
    if not user_data: 
        _pull_data(request)
    responder.slots['email'] = _get('email')
    replies = ['We have sent you an email with a loan eligilbty form at {email}. For any further questions regarding loans you will need to visit our website MindMeld.com/loans.']
    responder.reply(replies)  


@app.handle(intent='activate_creditcard')
def faq_activate_creditcard_handler(request, responder):
    if not user_data: 
        _pull_data(request)
    responder.slots['email'] = _get('email')
    replies = ['You can activate your card by logging clicking on the link sent to your email at {email} or you can call us at 1-800-432-3117.']
    responder.reply(replies)


@app.handle(default=True)
def default(request, responder):
    replies = ['I\'m not sure how to help with that. Try asking about account balances or ordering checks', 
            "I'm afraid I don't know how to help with that. You can try to ask to check your balance or pay a bill",
            'Sorry, I do not know what that is. Try asking about card activation or reporting a stolen card', 
            "I'm afraid I can not help with that. A few banking tasks you can try are, transferring balances and paying bills"]
    responder.reply(replies)


@app.handle(intent='credit_due_date')
def check_due_date_handler(request, responder):
    replies = ['Your credit card bill is due on the 15th of every month, late payments will result in a $25 fee. Say \'pay my credit card bill\' to pay the due balance.']
    responder.reply(replies)


@app.auto_fill(intent='transfer_balances', form=entity_form)
def transfer_balances_handler(request, responder):
    if not user_data: 
        _pull_data(request)
    for entity in request.entities:
        if entity['type'] == 'account_type':
            if entity['role'] == 'origin':
                responder.slots['origin'] = entity['value'][0]['cname'] or entity['text']
            elif entity['role'] == 'dest':
                responder.slots['dest'] = entity['value'][0]['cname'] or entity['text']
        else:
            responder.slots['amount'] = entity['value'][0]['value'] or entity['text']
    if check_value(responder):
        responder.reply(["All right. A transfer of {amount} dollars from your "
               "{origin} to your {dest} has been intiated."])
        _put(responder.slots['origin'], _get(responder.slots['origin']) - responder.slots['amount'])
        _put(responder.slots['dest'], _get(responder.slots['dest']) + responder.slots['amount'])
    else:
        responder.reply(['You do not have ${amount} in your {origin} account. ' 
            'The max you can transfer from your {origin} is $' + str(_get(responder.slots['origin'])) + '.'])


@app.handle(intent='pay_creditcard')
def pay_creditcard_handler(request, responder):
    if not user_data: 
        _pull_data(request)
    responder.slots['min'] = round(_get('credit') * .05)
    responder.slots['total_balance'] = _get('credit')
    if _get('credit') > 0:
        if request.entities:
            for entity in request.entities:
                if entity['type'] == 'credit_amount':
                    responder.slots['payment'] = entity['value'][0]['cname'] or entity['text']
                    if(responder.slots['payment'] == 'minimum'):
                        responder.reply(['Ok we have scheduled your credit card payment for your {payment} balance of ${min}'])
                        _put('credit', _get('credit') - responder.slots['min'])
                        _put('checking', _get('checking') - responder.slots['min'])
                    else:
                        responder.reply(['Ok we have scheduled your credit card payment for your {payment} of ${total_balance}'])
                        _put('credit', 0)
                        _put('checking', _get('checking') - responder.slots['total_balance'])
                else:
                    if entity['value'][0]['value'] <= responder.slots['total_balance']:
                        responder.slots['amount'] = entity['value'][0]['value']
                        responder.reply(['Ok we have scheduled your credit card payment for {amount}'])
                        _put('credit', _get('credit') - entity['value'][0]['value'])
                        _put('checking', _get('checking') - responder.slots['amount'])
                    else:
                        responder.reply(['The amount you have specified is greater than your credit balance of ${total_balance}'])
        else:
            responder.params.allowed_intents = ("accounts_creditcards.pay_creditcard", "greeting.*")
            responder.reply(['What amount do you want to pay off? '
                'You can choose to make a minimum payment of ${min} up to the total balance of ${total_balance}'])
    else:
        responder.reply(['Looks like your credit balance is $0, no need to make a payment at this time.'])


@app.handle(intent='setup_autopay')
def setup_autpay_handler(request, responder):
    if not user_data: 
        _pull_data(request)
    if(_get('auto_pay') != 0):
        replies = ['AutoPay is already turned on']
    else:
        replies = ['AutoPay has been turned on']
        _put('auto_pay', 1)
    responder.reply(replies)


@app.auto_fill(intent='check_balances', form=balance_form)
def check_balances_handler(request, responder):
    if not user_data: 
        _pull_data(request)
    if request.entities:
        for entity in request.entities:
            if entity['type'] == 'account_type':
                responder.slots['account'] = entity['value'][0]['cname'] or entity['text']
                responder.slots['amount'] = _get(entity['value'][0]['cname'] or entity['text'])
                responder.reply('Your {account} account balance is {amount}')

