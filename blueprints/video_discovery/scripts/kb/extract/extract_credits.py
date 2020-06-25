import logging
import luigi
import sys
from video_task import VideoDataProcessingTask  # noqa: F401
from libs.tasks import crawl_urls, request_api  # noqa: F401
from utils import load_plain_json  # noqa: F401

from .commons import API_KEY

sys.path.append('..')


class GetAllCredits(VideoDataProcessingTask):
    input_file = luigi.Parameter()
    doc_type = luigi.Parameter()
    tmdb_endpoint = luigi.Parameter()
    output_dir = luigi.Parameter()

    def output_path(self):
        return '{}_credits.jsonl'.format(self.doc_type)

    def output(self):
        return self.get_output_target(self.output_path())

    def run(self):
        urls = self._get_all_url()
        logging.info('Start crawling {:,d} {:s} Credit docs.'.format(len(urls), self.doc_type))
        crawl_urls(urls, output_file=self.get_output_path(self.output_path()))
        logging.info('Got {:,d} {:s} Credit docs.'.format(len(urls), self.doc_type))

    def _get_all_url(self):
        doc_ids = load_plain_json(self.input_file)
        return [
            '{:s}/{:d}/credits?api_key={:s}'.format(self.tmdb_endpoint, doc_id, API_KEY)
            for doc_id in doc_ids
        ]


class GetMovieCredits(GetAllCredits):
    pass


class ExtractMovieCredits(luigi.WrapperTask):
    def requires(self):
        return GetMovieCredits()


class GetTVCredits(GetAllCredits):
    pass


class ExtractTVCredits(luigi.WrapperTask):
    def requires(self):
        return GetTVCredits()


if __name__ == '__main__':
    luigi.run()
