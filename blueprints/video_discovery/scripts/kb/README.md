# KB Pipeline
This folder contains scripts for generating kb for Food Ordering blueprint.

## Getting Started

### Initialize
Run `pip install -r requirements.txt` to install dependencies.


## Run the Pipeline
```
$ python run_barista_etl.py RunBaristaETL --local-scheduler
```
The output will be in folder `out-20170329`.

Currently we only have `extract` and `transform` steps, `load` is WIP.

## Run the Tests
TBD

## Deployment
TBD
