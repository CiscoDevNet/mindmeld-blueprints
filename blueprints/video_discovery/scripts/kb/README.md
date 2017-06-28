# KB Pipeline
This folder contains scripts for generating kb for Video Discovery blueprint.

## Getting Started

### Initialize
Run `pip install -r requirements.txt` to install dependencies.

Get `TMDB_API_KEY` from Juan or Ray.

Get a pre-crawled dataset with 927,143 docs from s3
```
aws s3 cp s3://mindmeld/workbench-data/video_data_0626_1k.tar.gz .
```
which contains 20k tv/movies and the rest are episodes.


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

### Import to ElasticSearch
Install WB3
- See [here](https://github.com/expectlabs/mindmeld-workbench3).

Then, run
```
$ mmworkbench load-kb -n $HOST $APP_NAME $INDEX_NAME $FILENAME
```
We use `dev-search3-001.dev` as `HOST`. The import roughly takes 45 mins.

## Run the Tests
TBD

## Deployment
TBD
