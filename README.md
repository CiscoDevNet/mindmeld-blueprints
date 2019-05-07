# Blueprints for the MindMeld Platform

This repo contains blueprints for various conversational applications. A blueprint is a core reference implementation of a [MindMeld conversational application](https://www.mindmeld.com). Blueprints can be leveraged to kick start  development on a new MindMeld application with a similar use case.

## Quick Start

Assuming you have pip installed with Python 3.4, Python 3.5 or Python 3.6 and Elasticsearch running in the background:

```
pip install mindmeld
python -m home_assistant build
python -m home_assistant converse
```

## Available Blueprints

### [Food Ordering](https://www.mindmeld.com/docs/blueprints/food_ordering.html)

The Food Ordering blueprint is a conversational app for ordering food from a food delivery service such as Amazon Restaurants, Caviar or JustEat. This blueprint will demonstrate building an application for interacting with a number of restaurants with different menus.

In order to convert the food ordering application into a Webex Teams bot, first make sure you have `ngrok` (https://ngrok.com/) installed and do the following:

```
# Expose your local server's port 8080 to the internet
./ngrok http 8080

# Create web hook here: https://developer.webex.com/docs/api/v1/webhooks/create-a-webhook. 
# Use ngork's publically accessible URL for the targetUrl param when creating the web hook and
# set resource=messages, event=created
export WEBHOOK_ID=<insert webhook id>

# Create bot access token here: https://developer.webex.com/my-apps/new
export BOT_ACCESS_TOKEN=<insert bot access token>

# Start the bot service
python webex_bot_server.py 
```

### [Home Assistant](https://www.mindmeld.com/docs/blueprints/home_assistant.html)

The Home Assistant blueprint is a conversational app that helps users to control appliances, lights, doors, thermostat and check the weather. This blueprint will demonstrate building an application with multiple intents, domains, entities and roles.

### [Video Discovery](https://www.mindmeld.com/docs/blueprints/video_discovery.html)
The Video Discovery blueprint is a conversational app that helps users to search for and ask questions about movies and tv shows. This blueprint will demonstrate the extensive usage of the Knowledge Base component.

## Want to learn more about MindMeld?

Visit the [MindMeld website](https://www.mindmeld.com/).

## Feedback or Support Questions

Please contact us at [mindmeld@cisco.com](mailto:mindmeld@cisco.com).
