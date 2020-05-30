# -*- coding: utf-8 -*-
"""This module contains a MindMeld application"""
from mindmeld import Application
from mindmeld.core import FormEntity
import random
import json
import re

app = Application(__name__)

__all__ = ["app"]

# User data and helper functions

user_data = {}

sample_users = {
    "johndoe123": 0,
    "larry_l12": 1,
    "splashbro30": 2,
}


def _pull_data(request):
    with open("banking_blueprint/data/sample_user_data.json") as f:
        global user_data
        data = json.load(f)
        if request.context.get("user_name"):
            user_name = request.context.get("user_name")
            user = sample_users[user_name]
        else:
            user = random.choice([0, 1, 2])

        user_data = data[user]


def _get(key):
    return user_data[key]


def _put(key, value):
    global user_data
    user_data[key] = value


def _check_value(responder):
    return _get(responder.slots["origin"]) >= responder.slots["amount"]


def _parseSentenceForNumber(sentence):
    sen = sentence.replace(",", "")
    result = re.findall("[-+]?\d*\.\d+|\d+", sen)
    return result[0]


def _credit_amount_helper(request, responder, entity):
    responder.slots["payment"] = (
        entity["value"][0]["cname"] if len(entity["value"]) > 0 else entity["text"]
    )
    if responder.slots["payment"] == "minimum":
        responder.reply(
            "Ok we have scheduled your credit card payment for your {payment} balance of $"
            + format(responder.slots["min"], ".2f")
        )
        _put("credit", _get("credit") - responder.slots["min"])
        _put("checking", _get("checking") - responder.slots["min"])
    else:
        responder.reply(
            "Ok we have scheduled your credit card payment for your {payment} of $"
            + format(responder.slots["total_balance"], ".2f")
        )
        _put("credit", 0)
        _put("checking", _get("checking") - responder.slots["total_balance"])


def _exact_amount_helper(request, responder, entity):
    try:
        responder.slots["amount"] = entity["value"][0]["value"]
    except KeyError as e:
        responder.reply(
            "Unable to recognize the amount of money you have provided, try "
            "formatting the value like this '$40.50'"
        )
        return
    if (responder.slots["amount"] <= _get("credit")) & (responder.slots["amount"] > 0):
        responder.slots["amount"] = entity["value"][0]["value"]
        responder.reply(
            "Ok we have scheduled your credit card payment for $"
            + format(responder.slots["amount"], ".2f")
        )
        _put("credit", round(_get("credit") - entity["value"][0]["value"], 2))
        _put("checking", round((_get("checking") - responder.slots["amount"]), 2))
    else:
        if responder.slots["amount"] > 0:
            responder.reply(
                "The amount you have specified is greater than your credit balance of $"
                + format(responder.slots["total_balance"], ".2f")
            )
        else:
            responder.reply("Please input an amount greater than zero.")


def _credit_check(request, responder, entity):
    account_name = (
        entity["value"][0]["cname"] if len(entity["value"]) > 0 else entity["text"]
    )
    if account_name == "credit":
        responder.reply(
            "You may not transfer money to or from your credit account. If you"
            " would like to pay your credit bill please "
            "try saying 'Pay my credit bill'."
        )
        return True


# Slot filling forms

entity_form = {
    "entities": [
        FormEntity(
            entity="account_type",
            role="origin",
            responses=["Sure. Transfer from which account - checking or savings?"],
        ),
        FormEntity(
            entity="account_type",
            role="dest",
            responses=["To which account - checking or savings?"],
        ),
        FormEntity(
            entity="sys_amount-of-money",
            responses=["And, how much do you want to transfer?"],
        ),
    ],
    "exit_keys": [
        "cancel",
        "restart",
        "exit",
        "reset",
        "no",
        "nevermind",
        "stop",
        "back",
        "help",
        "stpo it",
        "go back" "new task",
        "other",
        "return",
        "end",
    ],
    "exit_msg": "A few other banking tasks you can try are, reporting a"
    " fraudelent charge and setting up AutoPay",
    "max_retries": 1,
}

balance_form = {
    "entities": [
        FormEntity(
            entity="account_type",
            responses=["Sure. for which account - checkings, savings, or credit?"],
        )
    ],
    "exit_keys": [
        "cancel",
        "restart",
        "exit",
        "reset",
        "no",
        "nevermind",
        "stop",
        "back",
        "help",
        "stop it",
        "go back" "new task",
        "other",
        "return",
        "end",
    ],
    "exit_msg": "A few other banking tasks you can try are, ordering checks and paying bills",
    "max_retries": 1,
}

# Dialogue state handlers


@app.handle(intent="greet")
def greet(request, responder):
    if not user_data:
        _pull_data(request)
    responder.slots["name"] = _get("first_name")
    replies = [
        "Hi {name}, how can I help with your banking tasks? You can try transferring "
        "money between accounts or paying a bill.",
        "Hello {name}, thanks for choosing MindMeld Bank. You can do things "
        "like, ask for your routing number, order "
        "checks, and check bill due dates.",
        "Welome to MindMeld Bank {name}, How can I help with your banking tasks? "
        "You can try reporting a fraud charge or a lost credit card.",
        "Thanks for using MindMeld Bank {name}! What would you like to do today? "
        "A few things I can help with are, "
        "checking balances, paying off your credit card, and setting up a new card.",
    ]
    responder.reply(replies)


@app.handle(intent="exit")
def exit(request, responder):
    responder.reply(["Bye", "Goodbye", "Have a nice day."])


@app.handle(intent="help")
def help(request, responder):
    responder.reply(
        [
            "A few things I can help you with are, checking balances,"
            " paying off your credit card, and setting up a new card.",
            "Looks like you need help have you tried, ask for your routing"
            " number, ordering checks, and checking bill due dates.",
            "You can try reporting a fraud charge or a lost credit card.",
            "Need some suggestions, try ordering some "
            "checks by saying 'order checks', or check your balance for savings,"
            " checking, or credit account by saying 'check balance' and then the account name",
            "A few of things you can ask me are, 'how to apply for a loan', 'what is my routing "
            "number', and 'can you pay my credit card bill'",
            "Try asking about card activation or reporting a stolen card",
            "A few things I can help with are, reporting a fraudulent charge,"
            " paying off your credit card, and resetting your pin.",
            "Have you tried asking for your routing number yet, you can do that by saying 'what "
            "is my routing number'.",
            "Have you tried making a transfer, you can do that by saying 'transfer money'.",
            "Need some suggestions?, you can ask me something like 'lost my pin', 'card is "
            "stolen', or 'setup a new card'.",
        ]
    )


@app.handle(intent="lost_creditcard")
def faq_lost_creditcard_handler(request, responder):
    if not user_data:
        _pull_data(request)
    responder.slots["email"] = _get("email")
    replies = [
        "I've noted that your card may have been lost or stolen. Please follow up "
        "immediately by calling 1-800-432-3117 or clicking the link in the email sent to {email}"
    ]
    responder.reply(replies)


@app.handle(intent="new_creditcard")
def faq_new_creditcard_handler(request, responder):
    if not user_data:
        _pull_data(request)
    responder.slots["email"] = _get("email")
    replies = [
        "An email has been sent to {email} with the available credit card offers for you. You may "
        "also visit a local branch and talk to a MindMeld teller."
    ]
    responder.reply(replies)


@app.handle(intent="order_checks")
def faq_order_checks_handler(request, responder):
    if not user_data:
        _pull_data(request)
    responder.slots["email"] = _get("email")
    replies = [
        "We have placed an order for a checkbook, which contain 50 checks. To confirm, change "
        "quanity of checks, or any other questions please view the link in"
        " the email sent to {email}."
    ]
    responder.reply(replies)


@app.handle(intent="routing_number")
def faq_routing_number_handler(request, responder):
    if not user_data:
        _pull_data(request)
    responder.slots["routing"] = _get("routing")
    replies = ["Your routing number is {routing}."]
    responder.reply(replies)


@app.handle(intent="fraud_charge")
def faq_fraud_charge_handler(request, responder):
    if not user_data:
        _pull_data(request)
    responder.slots["email"] = _get("email")
    replies = [
        "We have placed a hold on your card to avoid any further fraudelent activity. An email "
        "has been sent to {email} on how to reactivate your card"
    ]
    responder.reply(replies)


@app.handle(intent="forgot_pin")
def faq_forgot_pin_handler(request, responder):
    if not user_data:
        _pull_data(request)
    responder.slots["email"] = _get("email")
    replies = [
        "We have sent you an email at {email} with the steps on how to reset or recover your pin."
    ]
    responder.reply(replies)


@app.handle(intent="apply_loan")
def faq_apply_loan_handler(request, responder):
    if not user_data:
        _pull_data(request)
    responder.slots["email"] = _get("email")
    replies = [
        "We have sent you an email with a loan eligilbty form at {email}. For any further"
        " questions regarding loans you will need to visit our website MindMeld.com/loans."
    ]
    responder.reply(replies)


@app.handle(intent="activate_creditcard")
def faq_activate_creditcard_handler(request, responder):
    if not user_data:
        _pull_data(request)
    responder.slots["email"] = _get("email")
    replies = [
        "You can activate your card by logging clicking on the link sent to your email"
        " at {email} or you can call us at 1-800-432-3117."
    ]
    responder.reply(replies)


@app.handle(default=True)
def default(request, responder):
    replies = [
        "I'm not sure how to help with that. Try asking about account"
        " balances or ordering checks",
        "I'm afraid I don't know how to help with that."
        " You can try to ask to check your balance or pay a bill",
        "Sorry, I do not know what that is. Try asking about"
        " card activation or reporting a stolen card",
        "I'm afraid I can not help with that. A few banking tasks"
        " you can try are, transferring "
        "balances and paying bills",
    ]
    responder.reply(replies)


@app.handle(intent="credit_due_date")
def check_due_date_handler(request, responder):
    replies = [
        "Your credit card bill is due on the 15th of every month,"
        " late payments will result in a $25 fee."
        " Say 'pay my credit card bill' to pay the due balance."
    ]
    responder.reply(replies)


@app.auto_fill(intent="transfer_balances", form=entity_form)
def transfer_balances_handler(request, responder):
    if not user_data:
        _pull_data(request)
    for entity in request.entities:
        if entity["type"] == "account_type":
            if _credit_check(request, responder, entity):
                return
            if entity["role"] == "origin":
                responder.slots["origin"] = (
                    entity["value"][0]["cname"]
                    if len(entity["value"]) > 0
                    else entity["text"]
                )
            elif entity["role"] == "dest":
                responder.slots["dest"] = (
                    entity["value"][0]["cname"]
                    if len(entity["value"]) > 0
                    else entity["text"]
                )
        else:
            responder.slots["amount"] = (
                entity["value"][0]["value"]
                if len(entity["value"]) > 0
                else entity["text"]
            )
    if _check_value(responder):
        responder.reply(
            [
                "All right. A transfer of $"
                + format(responder.slots["amount"], ".2f")
                + " dollars from your "
                "{origin} to your {dest} has been intiated."
            ]
        )
        _put(
            responder.slots["origin"],
            _get(responder.slots["origin"]) - responder.slots["amount"],
        )
        _put(
            responder.slots["dest"],
            _get(responder.slots["dest"]) + responder.slots["amount"],
        )
    else:
        responder.reply(
            [
                "You do not have $"
                + format(responder.slots["amount"], ".2f")
                + " in your {origin} account. "
                "The max you can transfer from your {origin} is $"
                + format(_get(responder.slots["origin"]), ".2f")
            ]
        )


@app.handle(intent="pay_creditcard")
def pay_creditcard_handler(request, responder):
    if not user_data:
        _pull_data(request)
    responder.slots["min"] = round(_get("credit") * 0.05)
    responder.slots["total_balance"] = _get("credit")
    if _get("credit") > 0:
        if request.entities:
            for entity in request.entities:
                if entity["type"] == "credit_amount":
                    _credit_amount_helper(request, responder, entity)
                else:
                    _exact_amount_helper(request, responder, entity)
        else:
            responder.params.allowed_intents = (
                "accounts_creditcards.pay_creditcard",
                "faq.help",
            )
            responder.reply(
                "What amount do you want to pay off? "
                "You can choose to make a minimum payment of ${min} up"
                " to the total balance of ${total_balance}"
            )
    else:
        responder.reply(
            "Looks like your credit balance is $0, no need to make a payment at this time."
        )


@app.handle(intent="setup_autopay")
def setup_autpay_handler(request, responder):
    if not user_data:
        _pull_data(request)
    if request.entities:
        if _get("auto_pay") == 0:
            replies = ["Autopay is already off. To turn back on just say 'autopay on'."]
        else:
            replies = [
                "Autopay has been turned off. To turn back on just say 'autopay on'."
            ]
            _put("auto_pay", 0)
    else:
        if _get("auto_pay") != 0:
            replies = [
                "AutoPay is already turned on. To turn off just say 'autopay off'."
            ]
        else:
            replies = [
                "AutoPay has been turned on. To turn off just say 'autopay off'."
            ]
            _put("auto_pay", 1)
    responder.reply(replies)


@app.auto_fill(intent="check_balances", form=balance_form)
def check_balances_handler(request, responder):
    if not user_data:
        _pull_data(request)
    if request.entities:
        for entity in request.entities:
            if entity["type"] == "account_type":
                responder.slots["account"] = (
                    entity["value"][0]["cname"]
                    if len(entity["value"]) > 0
                    else entity["text"]
                )
                responder.slots["amount"] = _get(responder.slots["account"])
                responder.reply(
                    "Your {account} account balance is $"
                    + format(responder.slots["amount"], ".2f")
                )
