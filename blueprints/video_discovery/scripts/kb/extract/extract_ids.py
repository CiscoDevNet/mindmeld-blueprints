import json
import logging
import luigi
import os
import sys

from .commons import GetTMDB

sys.path.append('..')
from video_task import VideoDataProcessingTask  # noqa: F401
from libs.tasks import RequestAPI  # noqa: F401
from utils import load_plain_json  # noqa: F401


class GetTMDBIDs(GetTMDB):
    """
    TODO:
    """
    doc_type = luigi.Parameter()
    page_start = luigi.IntParameter()
    page_end = luigi.IntParameter()

    def run(self):
        for page_idx in range(self.page_start, self.page_end):
            output_filename = '{}_ids_{}.json'.format(self.doc_type, page_idx)
            url = '{:s}?api_key={:s}&query=*&page={:d}'.format(self.tmdb_endpoint,
                                                               self.api_key, page_idx)
            yield RequestAPI(url=url,
                             output_dir=self.output_dir,
                             output_filename=output_filename)
        logging.info('Got {} ids from page {} to {}.'.format(self.doc_type,
                                                             self.page_start, self.page_end))
        self._complete = True

    def complete(self):
        return self._complete


class GetMovieIDs(GetTMDBIDs):
    pass


class GetTVIDs(GetTMDBIDs):
    pass


class ExtractIDs(VideoDataProcessingTask):
    """
    TODO:
    """
    input_dir = luigi.Parameter()
    output_dir = luigi.Parameter()
    doc_type = luigi.Parameter()

    def run(self):
        doc_ids = collect_ids(self.input_dir, self.doc_type)
        with self.output().open('w') as fp:
            json.dump(doc_ids, fp, indent=4)

    def output(self):
        out_filename = '{}_ids.json'.format(self.doc_type)
        return self.get_output_target(out_filename)


class ExtractMovieIDs(ExtractIDs):
    def requires(self):
        return GetMovieIDs()


class ExtractTVIDs(ExtractIDs):
    def requires(self):
        return GetTVIDs()


def collect_ids(ids_dir, doc_type):
    id_files = os.listdir(ids_dir)
    logging.info('Got {:,d} {} id files.'.format(len(id_files), doc_type))
    all_ids = []
    for id_file in id_files:
        path = os.path.join(ids_dir, id_file)
        docs = load_plain_json(path)
        docs = docs.get('results', [])
        ids = [doc.get('id') for doc in docs]
        all_ids.extend(ids)
    logging.info('Got {:,d} {} ids.'.format(len(all_ids), doc_type))
    return all_ids


if __name__ == '__main__':
    luigi.run()
