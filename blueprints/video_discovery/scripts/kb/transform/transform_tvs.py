import luigi
import sys
import json

from .commons import get_director, get_names
from .commons import TransformDocuments
from .constants import POSTER_IMG_URL

sys.path.append('..')
from video_task import VideoDataProcessingTask  # noqa: F401
from utils import load_json  # noqa: F401


class TransformTVs(TransformDocuments):
    input_file = luigi.Parameter()

    @staticmethod
    def transform(in_targets, out_target):
        with out_target.open('w') as fout:
            for in_target in in_targets:
                tv_obj = load_json(in_target)
                transformed_tv_obj = {
                    'title': tv_obj['name'],  # To be consistent with movies
                    'id': tv_obj['id'],
                    'overview': tv_obj.get('overview'),
                    'genres': get_names(tv_obj.get('genres', [])),
                    'casts': get_names(tv_obj.get('cast', [])),
                    'director': get_director(tv_obj.get('crew', [])),
                    'popularity': tv_obj.get('popularity'),
                    'vote_count': tv_obj.get('vote_count'),
                    'vote_average': tv_obj.get('vote_average'),
                    'release_date': tv_obj.get('first_air_date'),
                    'runtime': tv_obj.get('runtime'),  # TODO: check episode data
                    'img_url': POSTER_IMG_URL + tv_obj.get('poster_path', ''),
                }
                line = json.dumps(transformed_tv_obj, fout, sort_keys=True)
                fout.write(line + '\n')
