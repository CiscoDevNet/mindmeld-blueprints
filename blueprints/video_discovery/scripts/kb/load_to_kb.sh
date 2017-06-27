#!/bin/bash

HOST=dev-search3-001.dev
APP_NAME=video_discovery
INDEX_NAME=20170627
FILENAME=output_data_0626_1k/transformed/video_1k.jsonl


mmworkbench load-kb -n $HOST $APP_NAME $INDEX_NAME $FILENAME
