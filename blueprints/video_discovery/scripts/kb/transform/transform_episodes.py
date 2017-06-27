import copy
import luigi
import sys
import json

from .commons import get_director, get_names, get_poster_img_url
from .constants import TYPE_EPISODE

sys.path.append('..')
from video_task import VideoDataProcessingTask  # noqa: F401
from utils import load_json  # noqa: F401
from libs.tasks import ReadLocalDir  # noqa: F401


class TransformEpisodes(VideoDataProcessingTask):
    doc_type = luigi.Parameter()
    input_file = luigi.Parameter()

    def output(self):
        filename = u'transformed_{}s.jsonl'.format(self.doc_type)
        return self.get_output_target(filename)

    def run(self):
        self.transform(self.input_file, self.output())

    @staticmethod
    def transform(input_file, out_target):

        fout = out_target.open('w')
        fin = open(input_file, 'r')
        for line in fin:
            tv_obj = json.loads(line)

            # Use values in TV objects as default values of episode objects.
            base_tv_obj = {
                'type': TYPE_EPISODE,
                'title': tv_obj['name'],  # To be consistent with movies
                'parent_id': tv_obj['id'],
                'overview': tv_obj.get('overview'),
                'genres': get_names(tv_obj.get('genres', [])),
                'casts': get_names(tv_obj.get('cast', [])),
                'director': get_director(tv_obj.get('crew', [])),
                'popularity': tv_obj.get('popularity'),
                'vote_count': tv_obj.get('vote_count'),
                'vote_average': tv_obj.get('vote_average'),
                'release_date': tv_obj.get('first_air_date'),
                'runtime': tv_obj.get('runtime'),
                'number_of_seasons': tv_obj.get('number_of_seasons'),
                'number_of_episodes': tv_obj.get('number_of_episodes'),
                'img_url': get_poster_img_url(tv_obj.get('poster_path', '')),
            }
            ep_objs = TransformEpisodes._get_episodes(tv_obj.get('seasons'), base_tv_obj)
            for ep_obj in ep_objs:
                line = json.dumps(ep_obj, fout, sort_keys=True)
                fout.write(line + '\n')
        fout.close()
        fin.close()

    @staticmethod
    def _get_episodes(season_objs, base_tv_obj):
        if not season_objs:
            return []
        ep_objs = []
        for season_obj in season_objs:
            '''
            {
                'season_number': 0,
                'episode_count': 6,
                'poster_path': '/AngNuUbXSciwLnUXtdOBHqphxNr.jpg',
                'air_date': '2009-02-17',
                'id': 3577
            },
            '''
            episode_count = season_obj['episode_count']
            for episode_num in range(1, episode_count + 1):
                episode_obj = copy.deepcopy(base_tv_obj)
                episode_obj.update({
                    'id': get_episode_id(season_obj.get('id', '0'), episode_num),
                    'season_number': season_obj.get('season_number'),
                    'episode_number': episode_num,
                    'img_url': get_poster_img_url(season_obj.get('poster_path', '')),
                    'release_date': season_obj.get('air_date'),
                })
                ep_objs.append(episode_obj)
        return ep_objs


def get_episode_id(season_id, episode_num):
    return u'{}_{}'.format(season_id, episode_num)
