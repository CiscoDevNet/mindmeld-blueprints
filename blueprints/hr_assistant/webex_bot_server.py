# -*- coding: utf-8 -*-

import os
import logging
import json
from flask import Flask, request
import requests
from ciscosparkapi import CiscoSparkAPI

from mmworkbench.components import NaturalLanguageProcessor
from mmworkbench.components.dialogue import Conversation
from mmworkbench import configure_logs

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Create web hook here: https://developer.webex.com/docs/api/v1/webhooks/create-a-webhook
WEBHOOK_ID = os.environ.get('WEBHOOK_ID')

# Create bot access token here: https://developer.webex.com/my-apps/new
ACCESS_TOKEN = os.environ.get('BOT_ACCESS_TOKEN')

if not WEBHOOK_ID or not ACCESS_TOKEN:
    raise Exception('WEBHOOK_ID and BOT_ACCESS_TOKEN are not set')

spark_api = CiscoSparkAPI(ACCESS_TOKEN)
ACCESS_TOKEN_WITH_BEARER = 'Bearer ' + ACCESS_TOKEN
CISCO_API_URL = 'https://api.ciscospark.com/v1'


# Build the food ordering application
configure_logs()
nlp = NaturalLanguageProcessor('.')
nlp.build()
conv = Conversation(nlp=nlp, app_path='.')


def _url(path):
    return CISCO_API_URL + path


def get_message(msg_id):
    headers = {'Authorization': ACCESS_TOKEN_WITH_BEARER}
    resp = requests.get(_url('/messages/{0}'.format(msg_id)), headers=headers)
    response = json.loads(resp.text)
    response['status_code'] = str(resp.status_code)
    return response


def post_message(room_id, text):
    headers = {'Authorization': ACCESS_TOKEN_WITH_BEARER, 'content-type': 'application/json'}
    payload = {'roomId': room_id, 'text': text}
    resp = requests.post(url=_url('/messages'), json=payload, headers=headers)
    response = json.loads(resp.text)
    response['status_code'] = str(resp.status_code)
    return response


@app.route('/', methods=['POST'])
def handle_message():
    me = spark_api.people.me()
    data = request.get_json()

    for key in ['personId', 'id', 'roomId']:
        if key not in data['data'].keys():
            return 'OK'

    if data['id'] != WEBHOOK_ID:
        logger.debug("Retrieved Webhook_id {} doesnt match".format(data['id']))
        return 'OK'

    person_id = data['data']['personId']
    msg_id = data['data']['id']
    txt = get_message(msg_id)
    room_id = data['data']['roomId']

    if 'text' not in txt:
        return 'OK'

    message = str(txt['text']).lower()

    # Ignore the bot's own responses, else it would go into an infinite loop
    # of answering it's own questions.
    if person_id != me.id:
        post_message(room_id, conv.say(message)[0])
    return 'OK'


if __name__ == '__main__':
    port_number = 8080
    print('Running server on port {}...'.format(port_number))
    app.run(host='localhost', port=port_number)
