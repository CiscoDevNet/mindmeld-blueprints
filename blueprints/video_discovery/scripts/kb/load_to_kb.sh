#!/bin/bash

HOST=dev-search3-001.dev
APP_NAME=ray_test_video_discovery
INDEX_NAME=20170702


DATA_DIR=data/output_data-0629-1900/transformed

FILENAME=transformed_tvs.jsonl
time mmworkbench load-kb -n $HOST $APP_NAME $INDEX_NAME $DATA_DIR/$FILENAME

FILENAME=transformed_movies.jsonl
time mmworkbench load-kb -n $HOST $APP_NAME $INDEX_NAME $DATA_DIR/$FILENAME
