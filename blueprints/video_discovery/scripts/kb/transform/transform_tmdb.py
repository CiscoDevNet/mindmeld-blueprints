import json
import logging
import luigi
import math
import sys
from video_task import VideoDataProcessingTask  # noqa: F401
from utils import load_jsonl  # noqa: F401

from .transform_movies import TransformMovies
from .transform_tvs import TransformTVs
# from .transform_episodes import TransformEpisodes

sys.path.append('..')


class NormalizeTMDB(VideoDataProcessingTask):
    output_dir = luigi.Parameter()

    def requires(self):
        return [TransformMovies(), TransformTVs()]

    def output(self):
        filename = u'transformed_videos.jsonl'
        return self.get_output_target(filename)

    def run(self):
        # TODO: don't read it all into memory
        movie_data = load_jsonl(self.input()[0])
        tv_data = load_jsonl(self.input()[1])
        video_data = self._filter(movie_data + tv_data)
        video_data = self._normalize(video_data)
        with self.output().open('w') as fp:
            for obj in video_data:
                line = '{}\n'.format(json.dumps(obj))
                fp.write(line)

    @staticmethod
    def _filter(objs):
        return [obj for obj in objs if obj.get('release_date')]

    @staticmethod
    def _normalize(objs):
        popularity_max = max(obj['popularity'] for obj in objs)
        popularity_min = min(obj['popularity'] for obj in objs)
        logging.info('Get min /max for pop: {}/{}'.format(popularity_min, popularity_max))
        for obj in objs:
            obj['popularity'] = normalize(obj['popularity'], popularity_min, popularity_max)
        return objs


def normalize(val, min_val, max_val):
    """
    Normalize the popularity value with log transformation.
    """
    new_val = val - min_val + 1
    return math.log(new_val)


class TransformTMDB(luigi.WrapperTask):
    def requires(self):
        return NormalizeTMDB()

    def run(self):
        # yield TransformEpisodes()
        pass


if __name__ == '__main__':
    luigi.run()
