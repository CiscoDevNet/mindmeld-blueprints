from luigi.format import Gzip
from luigi.s3 import S3Target
import datetime
import logging
import luigi
import os
import requests
import time
import json

import multiprocessing

from .constants import SLEEP_TIME


class DataProcessingTask(luigi.Task):

    logfile_path = luigi.Parameter(default=None)
    target = luigi.Parameter(default='local')
    output_dir = luigi.Parameter(default='out/')
    # TODO: remove app logic
    app_name = luigi.Parameter(default='default-app')

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
            # return luigi.LocalTarget(filename)
        else:
            logging.error("invalid target type: {}".format(self.target))
            raise

    def get_output_path(self, filename):
        return os.path.join(self.output_dir, filename)

    def __init__(self, *args, **kwargs):
        self._complete = False
        luigi.Task.__init__(self, *args, **kwargs)


class CrawlWebPage(DataProcessingTask):
    """
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


def request_api(url):
    logging.info('Requesting API from {}...'.format(url))
    response = requests.get(url)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logging.error('Error {} when requesting {}! :('.format(str(e), url))
        return
    time.sleep(SLEEP_TIME)
    return response


class ReadLocalFile(luigi.Task):
    file_path = luigi.Parameter()

    def output(self):
        logging.info(u'Reading local file: {}'.format(self.file_path))
        return luigi.LocalTarget(self.file_path)


class ReadLocalDir(luigi.Task):
    input_dir = luigi.Parameter()

    def output(self):
        output_files = os.listdir(self.input_dir)
        logging.info(u'Reading {:,d} files from local dir: {}'.format(len(output_files),
                                                                      self.input_dir))
        return [
            luigi.LocalTarget(os.path.join(self.input_dir, file_path))
            for file_path in output_files
        ]


def run_task(url, output_file, lock):
    res = request_api(url)
    if not res:
        return
    res = res.json()
    # ids = [result.get('id', None) for result in res.get('results', [])]
    lock.acquire()
    mode = 'w'
    if os.path.isfile(output_file):
        mode = 'a'

    with open(output_file, mode) as fp:
        # line = json.dumps(ids)
        line = json.dumps(res)
        fp.write(line + '\n')
    lock.release()


def crawl_urls(urls, output_file, num_workers=6):
    m = multiprocessing.Manager()
    mp_lock = m.Lock()
    offset = 0
    while offset < len(urls):
        pool = multiprocessing.Pool(num_workers)
        params = [(url, output_file, mp_lock) for url in urls[offset:offset+num_workers]]
        pool.starmap(run_task, params)
        pool.close()
        pool.join()
        offset += num_workers
        time.sleep(1)
