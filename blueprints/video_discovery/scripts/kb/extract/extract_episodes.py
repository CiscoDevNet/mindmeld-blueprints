import logging
import luigi
import sys
from video_task import VideoDataProcessingTask  # noqa: F401
from libs.tasks import RequestAPI  # noqa: F401
from utils import load_plain_json  # noqa: F401

from .commons import GetTMDB

sys.path.append('..')


class GetEpisode(GetTMDB):
    """
    Get the credits of a single tv/movie.
    """
    doc_id = luigi.Parameter()
    season = luigi.Parameter()
    episode = luigi.Parameter()

    def requires(self):
        output_filename = '{}_s{}e{}.json'.format(self.doc_id, self.season, self.episode)
        url = '{:s}/{:d}/season/{:d}/episode/{:d}?api_key={:s}'.format(self.tmdb_endpoint,
                                                                       self.doc_id,
                                                                       self.season,
                                                                       self.episode,
                                                                       self.api_key)
        return RequestAPI(url=url,
                          output_dir=self.output_dir,
                          output_filename=output_filename)


class GetEpisodes(luigi.WrapperTask):
    input_file = luigi.Parameter()

    def requires(self):
        season_objs = load_plain_json(self.input_file)
        logging.info('Getting {:d} seasons...'.format(len(season_objs)))
        episode_tasks = []
        for season_obj in season_objs:
            for episode_num in range(1, season_obj['episode_count'] + 1):
                episode_tasks.append(
                    GetEpisode(
                            doc_id=season_obj['tv_id'],
                            season=season_obj['season_number'],
                            episode=episode_num,
                    )
                )
        logging.info('Getting {:d} episodes...'.format(len(episode_tasks)))
        return episode_tasks


if __name__ == '__main__':
    luigi.run()
