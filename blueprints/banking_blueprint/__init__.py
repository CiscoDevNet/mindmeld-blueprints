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

user_data = {}

sample_users = {
    "johndoe123" : 0,
    "larry_l12" : 1,
    "splashbro30" : 2,
}

def pull_data(request):
    with open('banking_blueprint/data/sample_user_data.json') as f:
        global user_data 
        data = json.load(f)
        if request.context.get('user_name'):
            user_name = request.context.get('user_name')
            user = sample_users[user_name]
        else:
            user = random.choice([0, 1, 2])

        user_data = data[user]
        print(user_data)

def get(key):
    print(key)
    return user_data[key]

def put(key, value):
    global user_data
    user_data[key] = value

@app.handle(intent='greet')
def greet(request, responder):
    if not user_data: 
        pull_data(request)
    responder.slots['name'] = get('first_name')
    replies = ['Hi {name}, How can I help with your banking tasks? You can try transferring money between accounts or paying a bill.',
     'Hello {name}, thanks for choosing MindMeld Bank. You can do things like, ask for your routing number, order checks, and check bill due dates.',
     'Welome to MindMeld Bank {name}, How can I help with your banking tasks? You can try reporting a fraud charge or a lost credit card.',
     'Thanks for using MindMeld Bank {name}! What would you like to do today? A few things I can help with are, checking balances, paying off your credit card, and setting up a new card.']
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
    responder.slots['routing'] = get('routing')
    replies = ['Your routing number is {routing}.']
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
    replies = ['Sorry, I didn’t get that. Try asking about account balances or ordering checks', 
            "I'm afraid I don't understand. You can try to ask to check your balance or pay a bill",
            'Sorry, I do not know what that is. Try asking about card activation or reporting a stolen card', 
            "I'm afraid I dont't understand. A few banking tasks you can try are, transferring balances and paying bills"]
    responder.reply(replies)

@app.handle(intent='credit_due_date')
def check_due_date_handler(request, responder):
    replies = ['Your credit card bill is due on the 15th of every month, late payments will result in a $25 fee']
    responder.reply(replies)


def check_amount(amount):
    pass
    #logic for checking if amount is available to be transferred 


entity_form = {
    'entities':[
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
            #custom_eval=check_amount
        ],
}

def check_value(responder):
    return get(responder.slots['origin']) >= responder.slots['amount']

@app.auto_fill(intent='transfer_balances', form=entity_form)
def transfer_balances_handler(request, responder):
	
    for entity in request.entities:
        if entity['type'] == 'account_type':
            if entity['role'] == 'origin':
                print(entity)
                responder.slots['origin'] = entity['value'][0]['cname'] or entity['text']
            elif entity['role'] == 'dest':
                print(entity)
                responder.slots['dest'] = entity['value'][0]['cname'] or entity['text']
        else:
            print(entity)
            responder.slots['amount'] = entity['value'][0]['value']


    if check_value(responder):
        responder.reply(["All right. A transfer of {amount} dollars from your "
               "{origin} to your {dest} has been intiated."])
        put(responder.slots['origin'], get(responder.slots['origin']) - responder.slots['amount'])
        put(responder.slots['dest'], get(responder.slots['dest']) + responder.slots['amount'])
    else:
        responder.reply(['You do not have ${amount} in your {origin} account. ' 
            'The max you can transfer from your {origin} is $' + str(get(responder.slots['origin'])) + '.'])


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
    responder.slots['min'] = round(get('credit') * .05)
    responder.slots['total_balance'] = get('credit')
    if get('credit') > 0:
        if request.entities:
            for entity in request.entities:
                print(entity)
                if entity['type'] == 'credit_amount':
                    responder.slots['payment'] = entity['value'][0]['cname'] or entity['text']
                    if(responder.slots['payment'] == 'minimum'):
                        responder.reply(['Ok we have scheduled your credit card payment for your {payment} balance of ${min}'])
                        put('credit', get('credit') - responder.slots['min'])
                    else:
                        responder.reply(['Ok we have scheduled your credit card payment for your {payment} of ${total_balance}'])
                        put('credit', 0)
                else:
                    if entity['value'][0]['value'] <= responder.slots['total_balance']:
                        responder.slots['amount'] = entity['value'][0]['value'] 
                        responder.reply(['Ok we have scheduled your credit card payment for {amount}'])
                        put('credit', get('credit') - entity['value'][0]['value'])
                    else:
                        responder.reply(['The amount you have specified is greater than your credit balance of ${total_balance}'])
        else:
            responder.params.allowed_intents = ("accounts_creditcards.pay_creditcard", "greeting.*")
            print(request.domain)
            print(request.intent)
            responder.reply(['What amount do you want to pay off? '
                'You can choose to make a minimum payment of ${min} up to the total balance of ${total_balance}'])
    else:
        responder.reply(['Looks like your credit balance is $0, no need to make a payment at this time.'])



@app.handle(intent='setup_autopay')
def setup_autpay_handler(request, responder):
    if(get('auto_pay') != 0):
        replies = ['AutoPay is already turned on']
    else:
        replies = ['AutoPay has been turned on']
        put('auto_pay', 1)
    responder.reply(replies)


balance_form = {
    'entities':[
    FormEntity(
        entity='account_type',
        responses=['Sure. for which account?'])
    ],
}


@app.auto_fill(intent='check_balances', form=balance_form)
def check_balances_handler(request, responder):
    if request.entities:
        for entity in request.entities:
            if entity['type'] == 'account_type':
                print(entity)
                responder.slots['account'] = entity['text']
                responder.slots['amount'] = get(entity['value'][0]['cname'])
                responder.reply('Your {account} account balance is {amount}')

        






