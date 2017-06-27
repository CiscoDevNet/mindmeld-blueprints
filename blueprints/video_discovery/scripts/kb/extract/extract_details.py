import logging
import luigi
import sys
import json

from .commons import API_KEY

sys.path.append('..')
from video_task import VideoDataProcessingTask  # noqa: F401
from libs.tasks import ReadLocalDir  # noqa: F401
from libs.tasks import request_api  # noqa: F401
from utils import dump_json, load_json, load_plain_json  # noqa: F401


class GetDetails(VideoDataProcessingTask):
    input_file = luigi.Parameter()
    doc_type = luigi.Parameter()
    tmdb_endpoint = luigi.Parameter()
    output_dir = luigi.Parameter()

    def run(self):
        doc_ids = load_plain_json(self.input_file)
        logging.info('Getting {:d} {} details...'.format(len(doc_ids), self.doc_type))

        fout = self.output().open('w')
        for doc_id in doc_ids:
            url = '{:s}/{:d}?api_key={:s}'.format(self.tmdb_endpoint, doc_id, API_KEY)
            response = request_api(url)
            if not response:
                continue
            line = '{}\n'.format(json.dumps(response.json(), sort_keys=True))
            fout.write(line)
        fout.close()

    def output(self):
        filename = '{}_details.jsonl'.format(self.doc_type)
        return self.get_output_target(filename)


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
