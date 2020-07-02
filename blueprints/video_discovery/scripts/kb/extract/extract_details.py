import logging
import luigi
import sys
import json

from .commons import API_KEY

sys.path.append('..')
from video_task import VideoDataProcessingTask  # noqa: F401,E402
from libs.tasks import ReadLocalDir  # noqa: F401,E402
from libs.tasks import crawl_urls, request_api  # noqa: F401,E402
from utils import dump_json, load_json, load_plain_json  # noqa: F401,E402


class GetDetails(VideoDataProcessingTask):
    input_file = luigi.Parameter()
    doc_type = luigi.Parameter()
    tmdb_endpoint = luigi.Parameter()
    output_dir = luigi.Parameter()

    def output_path(self):
        return '{}_details.jsonl'.format(self.doc_type)

    def output(self):
        return self.get_output_target(self.output_path())

    def run(self):
        urls = self._get_all_url()
        logging.info('Start crawling {:,d} {:s} Detail docs.'.format(len(urls), self.doc_type))
        crawl_urls(urls, output_file=self.get_output_path(self.output_path()))
        logging.info('Got {:,d} {:s} Detail docs.'.format(len(urls), self.doc_type))

    def _get_all_url(self):
        doc_ids = load_plain_json(self.input_file)
        return [
            '{:s}/{:d}?api_key={:s}'.format(self.tmdb_endpoint, doc_id, API_KEY)
            for doc_id in doc_ids
        ]


class GetMovieDetails(GetDetails):
    pass


class ExtractMovieDetails(luigi.WrapperTask):
    def requires(self):
        return GetMovieDetails()


class GetTVDetails(GetDetails):
    pass


class ExtractTVDetails(VideoDataProcessingTask):
    input_dir = luigi.Parameter()
    output_episode_file = luigi.Parameter()

    def requires(self):
        return GetTVDetails()

    def output(self):
        return self.get_output_target(self.output_episode_file)

    def run(self):
        # extract episode info
        episode_info = self._extract_episodes(self.input())
        dump_json(self.output(), episode_info)

    @staticmethod
    def _extract_episodes(tv_details):
        """
        [
            {
                'tv_id': 1399,
                'name': 'Game of Thrones'
                'season_number': 1,
                'episode_count': 10,
            },
            {
                'tv_id': 1399,
                'name': 'Game of Thrones'
                'season_number': 2,
                'episode_count': 10,
            },
            ...
        ]
        """
        episodes_info = []

        # for target in tv_details:
        with tv_details.open('r') as fin:
            for line in fin:
                tv_obj = json.loads(line)
                season_info = tv_obj.get('seasons', [])
                if not season_info:
                    continue
                for season in season_info:
                    episodes_info.append({
                        'tv_id': tv_obj['id'],
                        'name': tv_obj['name'],
                        'season_number': season['season_number'],
                        'episode_count': season['episode_count'],
                    })
        return episodes_info


if __name__ == '__main__':
    luigi.run()
