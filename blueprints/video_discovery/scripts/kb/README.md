# KB Pipeline
This folder contains scripts for generating kb for Video Discovery blueprint.

## Getting Started

### Initialize
Run `pip install -r requirements.txt` to install dependencies.

Get `TMDB_API_KEY` from Juan or Ray.

Get a pre-crawled dataset with ~330k docs from s3
```
aws s3 cp s3://mindmeld/workbench-data/video-data-0706.tar.gz .
```


## Run the Pipeline
First, start Luigi daemon
```
$ luigid
```
Then, run
```
$ TMDB_API_KEY=<TMDB_API_KEY> python run_video_etl.py RunVideoETL
```
The output will be in folder `output_data`.

To get the top 20k tv/movies, it roughly takes 8 hrs in total.

Currently we only have `extract` and `transform` steps in Luigi, `load` is not implemented yet.

## Import to ElasticSearch
Install WB3
- See [here](https://github.com/expectlabs/mindmeld-workbench3).

Switch to branch `feature/stream-load-kb` in WB3
- It's temporarily solution since the PR hasn't been merged yet.

Then, run
```
$ mmworkbench load-kb -n $HOST $APP_NAME $INDEX_NAME $FILENAME
```
We use `dev-search3-001.dev` as `HOST` or you can use local running ES. 
The import roughly takes 20 mins.

### Example
Say we want to import the data at July 6:
```
# Download from s3
$ aws s3 cp s3://mindmeld/workbench-data/video-data-0706.tar.gz .
# Unzip it
$ video-data-0706.tar.gz
```
Prepare WB3 (temporarily fix)
```
cd $YOUR_WB3_DIR
git checkout feature/stream-load-kb
```
If you want to import to local ES, make sure it is now running.

Then start importing
```
cd output_data-0706-release_year/transformed
mmworkbench load-kb -n $HOST video_discovery 20170706 transformed_tvs.jsonl
mmworkbench load-kb -n $HOST video_discovery 20170706 transformed_movies.jsonl
```



## Run the Tests
TBD

## Deployment
TBD
