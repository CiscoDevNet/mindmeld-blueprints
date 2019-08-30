#!/bin/bash
cd blueprints

rm app.tar.gz
tar -czf app.tar.gz --exclude=.generated* --exclude=indexes --exclude=.generated --exclude=*.pyc --exclude=**/*.pyc --exclude=__pycache__ --exclude=**/.mm_keep -C video_discovery .
aws s3 rm s3://mindmeld-blueprints-master/video_discovery/app.tar.gz
aws s3 rm s3://mindmeld-blueprints-staging/video_discovery/app.tar.gz
aws s3 rm s3://mindmeld-blueprints-develop/video_discovery/app.tar.gz
aws s3 cp app.tar.gz s3://mindmeld-blueprints-staging/video_discovery/app.tar.gz
aws s3 cp app.tar.gz s3://mindmeld-blueprints-develop/video_discovery/app.tar.gz
aws s3 cp app.tar.gz s3://mindmeld-blueprints-master/video_discovery/app.tar.gz

rm app.tar.gz
tar -czf app.tar.gz --exclude=.generated* --exclude=indexes --exclude=.generated --exclude=*.pyc --exclude=**/*.pyc --exclude=__pycache__ --exclude=**/.mm_keep -C kwik_e_mart .
aws s3 rm s3://mindmeld-blueprints-master/kwik_e_mart/app.tar.gz
aws s3 rm s3://mindmeld-blueprints-staging/kwik_e_mart/app.tar.gz
aws s3 rm s3://mindmeld-blueprints-develop/kwik_e_mart/app.tar.gz
aws s3 cp app.tar.gz s3://mindmeld-blueprints-staging/kwik_e_mart/app.tar.gz
aws s3 cp app.tar.gz s3://mindmeld-blueprints-develop/kwik_e_mart/app.tar.gz
aws s3 cp app.tar.gz s3://mindmeld-blueprints-master/kwik_e_mart/app.tar.gz


rm app.tar.gz
tar -czf app.tar.gz --exclude=.generated* --exclude=indexes --exclude=.generated --exclude=*.pyc --exclude=**/*.pyc --exclude=__pycache__ --exclude=**/.mm_keep -C home_assistant .
aws s3 rm s3://mindmeld-blueprints-master/home_assistant/app.tar.gz
aws s3 rm s3://mindmeld-blueprints-staging/home_assistant/app.tar.gz
aws s3 rm s3://mindmeld-blueprints-develop/home_assistant/app.tar.gz
aws s3 cp app.tar.gz s3://mindmeld-blueprints-staging/home_assistant/app.tar.gz
aws s3 cp app.tar.gz s3://mindmeld-blueprints-develop/home_assistant/app.tar.gz
aws s3 cp app.tar.gz s3://mindmeld-blueprints-master/home_assistant/app.tar.gz


rm app.tar.gz
tar -czf app.tar.gz --exclude=.generated* --exclude=indexes --exclude=.generated --exclude=*.pyc --exclude=**/*.pyc --exclude=__pycache__ --exclude=**/.mm_keep -C food_ordering .
aws s3 rm s3://mindmeld-blueprints-master/food_ordering/app.tar.gz
aws s3 rm s3://mindmeld-blueprints-staging/food_ordering/app.tar.gz
aws s3 rm s3://mindmeld-blueprints-develop/food_ordering/app.tar.gz
aws s3 cp app.tar.gz s3://mindmeld-blueprints-staging/food_ordering/app.tar.gz
aws s3 cp app.tar.gz s3://mindmeld-blueprints-develop/food_ordering/app.tar.gz
aws s3 cp app.tar.gz s3://mindmeld-blueprints-master/food_ordering/app.tar.gz


rm app.tar.gz
tar -czf app.tar.gz --exclude=.generated* --exclude=indexes --exclude=.generated --exclude=*.pyc --exclude=**/*.pyc --exclude=__pycache__ --exclude=**/.mm_keep -C hr_assistant .
aws s3 rm s3://mindmeld-blueprints-master/hr_assistant/app.tar.gz
aws s3 rm s3://mindmeld-blueprints-staging/hr_assistant/app.tar.gz
aws s3 rm s3://mindmeld-blueprints-develop/hr_assistant/app.tar.gz
aws s3 cp app.tar.gz s3://mindmeld-blueprints-staging/hr_assistant/app.tar.gz
aws s3 cp app.tar.gz s3://mindmeld-blueprints-develop/hr_assistant/app.tar.gz
aws s3 cp app.tar.gz s3://mindmeld-blueprints-master/hr_assistant/app.tar.gz


rm app.tar.gz
tar -czf app.tar.gz --exclude=.generated* --exclude=indexes --exclude=.generated --exclude=*.pyc --exclude=**/*.pyc --exclude=__pycache__ --exclude=**/.mm_keep -C template .
aws s3 rm s3://mindmeld-blueprints-master/template/app.tar.gz
aws s3 rm s3://mindmeld-blueprints-staging/template/app.tar.gz
aws s3 rm s3://mindmeld-blueprints-develop/template/app.tar.gz
aws s3 cp app.tar.gz s3://mindmeld-blueprints-staging/template/app.tar.gz
aws s3 cp app.tar.gz s3://mindmeld-blueprints-develop/template/app.tar.gz
aws s3 cp app.tar.gz s3://mindmeld-blueprints-master/template/app.tar.gz

rm app.tar.gz
