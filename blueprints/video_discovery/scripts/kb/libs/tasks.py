from luigi.format import Gzip
from luigi.s3 import S3Target
import datetime
import logging
import luigi
import os
import requests
import time
import json

from .constants import SLEEP_TIME


class DataProcessingTask(luigi.Task):

    logfile_path = luigi.Parameter(default=None)
    target = luigi.Parameter(default='local')
    output_dir = luigi.Parameter(default='out/')
    # TODO: remove app logic
    app_name = luigi.Parameter(default='video-discovery')

    def get_output_target(self, filename):
        if self.target == 's3':
            s3_prefix = "s3://mindmeld/workbench-data/{}/".format(self.app_name)
            if self.output_dir:
                s3_prefix += self.output_dir + "/"
            date_str = datetime.datetime.today().strftime("%Y%m%d")
            hour_str = datetime.datetime.today().strftime("%H")
            full_filename = filename + "." + date_str + "-" + hour_str + ".gz"
            s3_path = s3_prefix + date_str + "/" + hour_str + "/" + full_filename
            return S3Target(s3_path, format=Gzip)
        elif self.target == 'local':
            return luigi.LocalTarget(os.path.join(self.output_dir, filename))
        else:
            logging.error("invalid target type: {}".format(self.target))
            raise

    def __init__(self, *args, **kwargs):
        self._complete = False
        luigi.Task.__init__(self, *args, **kwargs)


class CrawlWebPage(DataProcessingTask):
    """
    This task downloads metric logs from S3.
    Format of path is:
        s3://mindmeld-metrics/<app-name>/<env>/yyyy_mm_dd_<env>.json.gz
    Example:
        s3://mindmeld-metrics/uniqlo/dev/2016_10_07_dev.jsonl.gz

    """
    output_filename = luigi.Parameter(default='default_out')
    url = luigi.Parameter()

    def run(self):
        # TODO: error handling

        logging.info('Crawling web page from {}...'.format(self.url))
        # response = requests.get(self.url, headers=self.headers)
        response = requests.get(self.url)
        time.sleep(SLEEP_TIME)

        with self.output().open('w') as fout:
            fout.write(response.text)

    def output(self):
        return self.get_output_target(self.output_filename)


class RequestAPI(DataProcessingTask):
    """
    This task downloads metric logs from S3.
    Format of path is:
        s3://mindmeld-metrics/<app-name>/<env>/yyyy_mm_dd_<env>.json.gz
    Example:
        s3://mindmeld-metrics/uniqlo/dev/2016_10_07_dev.jsonl.gz

    """
    output_filename = luigi.Parameter(default='default_out')
    url = luigi.Parameter()

    def run(self):
        # TODO: error handling
        logging.info('Requesting API from {}...'.format(self.url))
        # response = requests.get(self.url, headers=self.headers)
        response = requests.get(self.url)
        time.sleep(SLEEP_TIME)
        with self.output().open('w') as fout:
            json.dump(response.json(), fout, indent=4)

    def output(self):
        return self.get_output_target(self.output_filename)


class ReadLocalFile(luigi.Task):
    file_path = luigi.Parameter()

    def output(self):
        logging.info(u'Reading local file: {}'.format(self.file_path))
        return luigi.LocalTarget(self.file_path)
