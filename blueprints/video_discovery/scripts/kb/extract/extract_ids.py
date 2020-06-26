import json
import logging
import luigi
import sys

from .commons import API_KEY

sys.path.append('..')
from video_task import VideoDataProcessingTask  # noqa: F401,E402
from libs.tasks import crawl_urls, request_api  # noqa: F401,E402
from utils import load_plain_json  # noqa: F401,E402


class GetTMDBIDs(VideoDataProcessingTask):
    """
    TODO:
    """
    tmdb_endpoint = luigi.Parameter()
    tmdb_filter = luigi.Parameter()
    doc_type = luigi.Parameter()
    year_start = luigi.IntParameter()
    year_end = luigi.IntParameter()

    def run(self):
        urls = self._get_all_url()
        logging.info('Start crawling {:,d} {:s} ID docs.'.format(len(urls), self.doc_type))
        crawl_urls(urls, output_file=self.get_output_path(self.output_path()))
        logging.info('Got {:,d} {:s} ID docs.'.format(len(urls), self.doc_type))

    def output_path(self):
        return '{}_ids.jsonl'.format(self.doc_type)

    def output(self):
        return self.get_output_target(self.output_path())

    def _get_all_url(self):
        urls = []

        for year_idx in range(self.year_start, self.year_end - 1, -1):
            year_filter = '{0}={1}'.format(self.tmdb_filter, year_idx)

            # Get the first page for total pages.
            url = '{:s}?query=*&{:s}&api_key={:s}'.format(self.tmdb_endpoint, year_filter, API_KEY)
            response = request_api(url)
            total_pages = response.json().get('total_pages', None)

            for page_idx in range(1, total_pages + 1):
                url = '{:s}?query=*&page={:d}&{:s}&api_key={:s}'.format(self.tmdb_endpoint,
                                                                        page_idx,
                                                                        year_filter,
                                                                        API_KEY)
                urls.append(url)
            logging.info('Getting {:,d} page of urls for {:s} at year {:d}.'.format(total_pages,
                                                                                    self.doc_type,
                                                                                    year_idx))
        return urls


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
        doc_ids = collect_ids(self.input(), self.doc_type)
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


def collect_ids(ids_file, doc_type):
    all_ids = []
    with ids_file.open('r') as fp:
        for line in fp:
            docs = json.loads(line)
            docs = docs.get('results', [])
            ids = [doc.get('id') for doc in docs]
            all_ids.extend(ids)
    logging.info('Got {:,d} {} ids.'.format(len(all_ids), doc_type))
    return list(set(all_ids))


if __name__ == '__main__':
    luigi.run()
