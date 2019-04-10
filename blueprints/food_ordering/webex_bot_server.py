# -*- coding: utf-8 -*-

import logging
import json
from flask import Flask, request
import requests
from ciscosparkapi import CiscoSparkAPI

from mmworkbench.components import NaturalLanguageProcessor
from mmworkbench.components.dialogue import Conversation

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Create web hook here: https://developer.webex.com/docs/api/v1/webhooks/create-a-webhook
WEBHOOK_ID = '<INSERT WEBHOOK ID>'

# Create bot access token here: https://developer.webex.com/my-apps/new
ACCESS_TOKEN = '<INSERT ACCESS TOKEN>'

spark_api = CiscoSparkAPI(ACCESS_TOKEN)
ACCESS_TOKEN = 'Bearer ' + ACCESS_TOKEN
CISCO_API_URL = 'https://api.ciscospark.com/v1'

# Build the food ordering application
nlp = NaturalLanguageProcessor('.')
nlp.load()
conv = Conversation(nlp=nlp, app_path='.')


def _url(path):
    return CISCO_API_URL + path


def get_message(msg_id):
    headers = {'Authorization': ACCESS_TOKEN}
    resp = requests.get(_url('/messages/{0}'.format(msg_id)), headers=headers)
    response = json.loads(resp.text)
    response['status_code'] = str(resp.status_code)
    return response


def post_message(room_id, text):
    headers = {'Authorization': ACCESS_TOKEN, 'content-type': 'application/json'}
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
    message = str(txt['text']).lower()

    if person_id == me.id:
        return 'OK'
    else:
        post_message(room_id, conv.say(message)[0])
        return 'OK'


if __name__ == '__main__':
    app.run(host='localhost', port=8080)
