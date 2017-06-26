import logging
import luigi
import sys

from .commons import GetTMDB

sys.path.append('..')
from video_task import VideoDataProcessingTask  # noqa: F401
from libs.tasks import ReadLocalDir  # noqa: F401
from libs.tasks import RequestAPI  # noqa: F401
from utils import dump_json, load_json, load_plain_json  # noqa: F401


class GetDetail(GetTMDB):
    """
    Get the detail of a single tv/movie.
    """
    doc_type = luigi.Parameter()
    doc_id = luigi.Parameter()

    def requires(self):
        output_filename = '{}_{}.json'.format(self.doc_type, self.doc_id)
        url = '{:s}/{:d}?api_key={:s}'.format(self.tmdb_endpoint, self.doc_id, self.api_key)
        return RequestAPI(url=url,
                          output_dir=self.output_dir,
                          output_filename=output_filename)


class GetDetails(luigi.Task):
    input_file = luigi.Parameter()
    doc_type = luigi.Parameter()
    tmdb_endpoint = luigi.Parameter()
    output_dir = luigi.Parameter()

    def requires(self):
        doc_ids = load_plain_json(self.input_file)
        logging.info('Getting {:d} {} details...'.format(len(doc_ids), self.doc_type))
        return [
            GetDetail(tmdb_endpoint=self.tmdb_endpoint,
                      output_dir=self.output_dir,
                      doc_type=self.doc_type,
                      doc_id=doc_id)
            for doc_id in doc_ids
        ]

    def output(self):
        return self.input()


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
    def _extract_episodes(tv_targets):
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
        for target in tv_targets:
            tv_obj = load_json(target)
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
