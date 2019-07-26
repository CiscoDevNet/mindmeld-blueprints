# -*- coding: utf-8 -*-

import os
import logging
import json
from flask import Flask, request
import requests
from ciscosparkapi import CiscoSparkAPI
from mindmeld.components import NaturalLanguageProcessor
from mindmeld.components.dialogue import Conversation
from mindmeld.bot import WebexBotServer
from mindmeld import configure_logs

if __name__ == '__main__':

    app = Flask(__name__)

    # Create web hook here: https://developer.webex.com/docs/api/v1/webhooks/create-a-webhook
    WEBHOOK_ID = os.environ.get('WEBHOOK_ID')

    # Create bot access token here: https://developer.webex.com/my-apps/new
    ACCESS_TOKEN = os.environ.get('BOT_ACCESS_TOKEN')

    configure_logs()
    nlp = NaturalLanguageProcessor('.')
    nlp.build()
    conv = Conversation(nlp=nlp, app_path='.')

    server = WebexBotServer(app, WEBHOOK_ID, ACCESS_TOKEN, conv)

    port_number = 8080
    print('Running server on port {}...'.format(port_number))

    server.run(host='localhost', port=port_number)
