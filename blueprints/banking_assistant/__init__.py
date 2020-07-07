# -*- coding: utf-8 -*-
"""This module contains a MindMeld application"""
from mindmeld import Application
from mindmeld.core import FormEntity
import random
import json
import os

app = Application(__name__)

__all__ = ["app"]

# User data class and helper functions for handlers

user = None


class User:
    def __init__(self, request):
        self.sample_users = {
            "johndoe123": 0,
            "larry_l12": 1,
            "splashbro30": 2,
        }
        user = self._pull_data(request)
        directory = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(directory, "data/sample_user_data.json")
        with open(path) as f:
            data = json.load(f)
            self.data = data[user]

    def _pull_data(self, request):
        if request.context.get("user_name"):
            user_name = request.context.get("user_name")
            if user_name in self.sample_users:
                self.user = self.sample_users[user_name]
            else:
                self.user = random.choice([0, 1, 2])
        else:
            self.user = random.choice([0, 1, 2])
        return self.user

    def put(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data[key]

    def check_value(self, responder):
        return self.get(responder.slots["origin"]) >= responder.slots["amount"]


def _credit_amount_helper(request, responder, entity, user):
    responder.slots["payment"] = (
        entity["value"][0]["cname"] if len(entity["value"]) > 0 else entity["text"]
    )
    if responder.slots["payment"] == "minimum":
        responder.reply(
            "OK, we have scheduled your credit card payment for your minimum balance of $"
            "{min:.2f}"
        )
        user.put("credit", user.get("credit") - responder.slots["min"])
        user.put("checking", user.get("checking") - responder.slots["min"])
    else:
        responder.reply(
            "OK, we have scheduled your credit card payment for your {payment} of $"
            "{total_balance:.2f}"
        )
        user.put("credit", 0)
        user.put("checking", user.get("checking") - responder.slots["total_balance"])


def _exact_amount_helper(request, responder, entity, user):
    try:
        responder.slots["amount"] = entity["value"][0]["value"]
    except KeyError:
        responder.reply(
            "Unable to recognize the amount of money you have provided, try "
            "formatting the value like this '$40.50'."
        )
        return
    if 0 < responder.slots["amount"] <= user.get("credit"):
        responder.slots["amount"] = entity["value"][0]["value"]
        responder.reply(
            "OK, we have scheduled your credit card payment for $"
            "{amount:.2f}."
        )
        user.put("credit", round(user.get("credit") - entity["value"][0]["value"], 2))
        user.put("checking", round((user.get("checking") - responder.slots["amount"]), 2))
    elif responder.slots["amount"] < 0:
        responder.reply("Please input an amount greater than zero.")
    else:
        responder.reply(
            "The amount you have specified is greater than your credit balance of $"
            "{total_balance:.2f}."
        )


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

transfer_form = {
    "entities": [
        FormEntity(
            entity="account_type",
            role="origin",
            responses=["Sure. Transfer from which account - checking or savings?"],
            retry_response=["That account is not correct. Transfer from which account?"],
        ),
        FormEntity(
            entity="account_type",
            role="dest",
            responses=["To which account - checking or savings?"],
            retry_response=["That account is not correct. Transfer to which account?"],
        ),
        FormEntity(
            entity="sys_amount-of-money",
            responses=["And how much do you want to transfer?"],
            retry_response=[
                "That amount is not correct. "
                "Please try formatting the value like this '$40.50'."
            ],
        ),
    ],
    "exit_keys": [
        "cancel",
        "cancel transfer",
        "stop transfer",
        "restart",
        "exit",
        "reset",
        "no",
        "nevermind",
        "stop",
        "back",
        "help",
        "stop it",
        "go back",
        "new task",
        "other",
        "return",
        "end",
    ],
    "exit_msg": "A couple of other banking tasks you can try are reporting a"
    " fraudulent charge and setting up AutoPay",
    "max_retries": 1,
}

balance_form = {
    "entities": [
        FormEntity(
            entity="account_type",
            responses=["Sure. For which account - checkings, savings, or credit?"],
            retry_response=[
                "That account is not correct."
                " Please try checkings, savings, or credit."
            ],
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
    "exit_msg": "A few other banking tasks you can try are ordering checks and paying bills.",
    "max_retries": 1,
}

# Dialogue state handlers


@app.handle(intent="greet")
def greet(request, responder):
    global user
    if not user:
        user = User(request)
    responder.slots["name"] = user.get("first_name")
    replies = [
        "Hi {name}, how can I help with your banking tasks? You can try transferring "
        "money between accounts or paying a bill.",
        "Hello {name}, thanks for choosing MindMeld Bank. You can do things "
        "like: ask for your routing number, order "
        "checks, and check bill due dates.",
        "Welome to MindMeld Bank {name}, how can I help with your banking tasks? "
        "You can try reporting a fraud charge or a lost credit card.",
        "Thanks for using MindMeld Bank, {name}! What would you like to do today? "
        "A few things I can help with are: "
        "checking balances, paying off your credit card, and setting up a new card.",
    ]
    responder.reply(replies)


@app.handle(intent="exit")
def exit(request, responder):
    responder.reply(["Bye!", "Goodbye!", "Have a nice day."])


@app.handle(intent="help")
def help(request, responder):
    responder.reply(
        [
            "A few things I can help you with are: checking balances,"
            " paying off your credit card, and setting up a new card.",
            "Looks like you need help. Have you tried: asking for your routing"
            " number, ordering checks, and checking bill due dates.",
            "You can try reporting a fraud charge or a lost credit card.",
            "Need some suggestions? Try ordering some "
            "checks by saying 'order checks', or check your balance for savings,"
            " checking, or credit account by saying 'check balance' and then the account name.",
            "A few of things you can ask me are: 'how to apply for a loan', 'what is my routing "
            "number', and 'can you pay my credit card bill'.",
            "Try asking about card activation or reporting a stolen card.",
            "A few things I can help with are: reporting a fraudulent charge,"
            " paying off your credit card, and resetting your PIN.",
            "Have you tried asking for your routing number yet? You can do that by saying 'what "
            "is my routing number'.",
            "Have you tried making a transfer? You can do that by saying 'transfer money'.",
            "Need some suggestions? You can ask me something like 'lost my PIN', 'card is "
            "stolen', or 'setup a new card'.",
        ]
    )


@app.handle(intent="lost_creditcard")
def faq_lost_creditcard_handler(request, responder):
    global user
    if not user:
        user = User(request)
    responder.slots["email"] = user.get("email")
    replies = [
        "I've noted that your card may have been lost or stolen. Please follow up "
        "immediately by calling 1-800-555-7456 or clicking the link in the email sent to {email}."
    ]
    responder.reply(replies)


@app.handle(intent="new_creditcard")
def faq_new_creditcard_handler(request, responder):
    global user
    if not user:
        user = User(request)
    responder.slots["email"] = user.get("email")
    replies = [
        "An email has been sent to {email} with the available credit card offers for you. You may "
        "also visit a local branch and talk to a MindMeld teller."
    ]
    responder.reply(replies)


@app.handle(intent="order_checks")
def faq_order_checks_handler(request, responder):
    global user
    if not user:
        user = User(request)
    responder.slots["email"] = user.get("email")
    replies = [
        "We have placed an order for a checkbook, which contains 50 checks. To confirm, change "
        "quantity of checks, or for any other questions, please view the link in"
        " the email sent to {email}."
    ]
    responder.reply(replies)


@app.handle(intent="routing_number")
def faq_routing_number_handler(request, responder):
    global user
    if not user:
        user = User(request)
    responder.slots["routing"] = user.get("routing")
    replies = ["Your routing number is {routing}."]
    responder.reply(replies)


@app.handle(intent="fraud_charge")
def faq_fraud_charge_handler(request, responder):
    global user
    if not user:
        user = User(request)
    responder.slots["email"] = user.get("email")
    replies = [
        "We have placed a hold on your card to avoid any further fraudulent activity. An email "
        "has been sent to {email} on how to reactivate your card."
    ]
    responder.reply(replies)


@app.handle(intent="forgot_pin")
def faq_forgot_pin_handler(request, responder):
    global user
    if not user:
        user = User(request)
    responder.slots["email"] = user.get("email")
    replies = [
        "We have sent you an email at {email} with the steps on how to reset or recover your PIN."
    ]
    responder.reply(replies)


@app.handle(intent="apply_loan")
def faq_apply_loan_handler(request, responder):
    global user
    if not user:
        user = User(request)
    responder.slots["email"] = user.get("email")
    replies = [
        "We have sent you an email with a loan eligibility form at {email}. For any further"
        " questions regarding loans you will need to visit our website MindMeld.com/loans."
    ]
    responder.reply(replies)


@app.handle(intent="activate_creditcard")
def faq_activate_creditcard_handler(request, responder):
    global user
    if not user:
        user = User(request)
    responder.slots["email"] = user.get("email")
    replies = [
        "You can activate your card by clicking on the link sent to your email"
        " at {email} or you can call us at 1-800-432-3117."
    ]
    responder.reply(replies)


@app.handle(default=True)
def default(request, responder):
    replies = [
        "I'm not sure how to help with that. Try asking about account"
        " balances or ordering checks.",
        "I'm afraid I don't know how to help with that."
        " You can try to ask to check your balance or pay a bill.",
        "Sorry, I do not know what that is. Try asking about"
        " card activation or reporting a stolen card.",
        "I'm afraid I can not help with that. A few banking tasks"
        " you can try are: transferring "
        "balances and paying bills.",
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


@app.auto_fill(intent="transfer_money", form=transfer_form)
def transfer_money_handler(request, responder):
    global user
    if not user:
        user = User(request)
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
    if user.check_value(responder):
        responder.reply(
            [
                "All right. A transfer of ${amount:.2f}"
                " from your "
                "{origin} to your {dest} has been initiated."
            ]
        )
        user.put(
            responder.slots["origin"],
            user.get(responder.slots["origin"]) - responder.slots["amount"],
        )
        user.put(
            responder.slots["dest"],
            user.get(responder.slots["dest"]) + responder.slots["amount"],
        )
    else:
        responder.reply(
            [
                "You do not have ${amount:.2f} "
                "in your {origin} account. "
                "The max you can transfer from your {origin} is $"
                + format(user.get(responder.slots["origin"]), ".2f")
            ]
        )


@app.handle(intent="pay_creditcard")
def pay_creditcard_handler(request, responder):
    global user
    if not user:
        user = User(request)
    responder.slots["min"] = round(user.get("credit") * 0.05)
    responder.slots["total_balance"] = user.get("credit")
    if user.get("credit") > 0:
        if request.entities:
            for entity in request.entities:
                if entity["type"] == "credit_amount":
                    _credit_amount_helper(request, responder, entity, user)
                else:
                    _exact_amount_helper(request, responder, entity, user)
        else:
            responder.params.allowed_intents = (
                "accounts_creditcards.pay_creditcard",
                "faq.help",
            )
            responder.reply(
                "What amount do you want to pay off? "
                "You can choose to make a minimum payment of ${min} up"
                " to the total balance of ${total_balance}."
            )
    else:
        responder.reply(
            "Looks like your credit balance is $0, no need to make a payment at this time."
        )


@app.handle(intent="setup_autopay")
def setup_autpay_handler(request, responder):
    global user
    if not user:
        user = User(request)
    if request.entities:
        if user.get("auto_pay") == 0:
            replies = ["Autopay is already off. To turn back on just say 'autopay on'."]
        else:
            replies = [
                "Autopay has been turned off. To turn back on just say 'autopay on'."
            ]
            user.put("auto_pay", 0)
    else:
        if user.get("auto_pay") != 0:
            replies = [
                "AutoPay is already turned on. To turn off just say 'autopay off'."
            ]
        else:
            replies = [
                "AutoPay has been turned on. To turn off just say 'autopay off'."
            ]
            user.put("auto_pay", 1)
    responder.reply(replies)


@app.auto_fill(intent="check_balances", form=balance_form)
def check_balances_handler(request, responder):
    global user
    if not user:
        user = User(request)
    if request.entities:
        for entity in request.entities:
            if entity["type"] == "account_type":
                responder.slots["account"] = (
                    entity["value"][0]["cname"]
                    if len(entity["value"]) > 0
                    else entity["text"]
                )
                responder.slots["amount"] = user.get(responder.slots["account"])
                responder.reply(
                    "Your {account} account balance is ${amount:.2f}"
                )
