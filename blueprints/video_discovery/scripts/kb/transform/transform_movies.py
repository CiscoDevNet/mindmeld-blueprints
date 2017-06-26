import luigi
import sys
import json

from .commons import get_director, get_names
from .commons import TransformDocuments
from .constants import POSTER_IMG_URL

sys.path.append('..')
from video_task import VideoDataProcessingTask  # noqa: F401
from utils import load_json  # noqa: F401


class TransformMovies(TransformDocuments):
    input_file = luigi.Parameter()

    @staticmethod
    def transform(in_targets, out_target):
        with out_target.open('w') as fout:
            for in_target in in_targets:
                movie_obj = load_json(in_target)
                transformed_movie_obj = {
                    'title': movie_obj['title'],
                    'id': movie_obj['id'],
                    'imdb_id': movie_obj.get('imdb_id'),
                    'overview': movie_obj.get('overview'),
                    'genres': get_names(movie_obj.get('genres', [])),
                    'casts': get_names(movie_obj.get('cast', [])),
                    'director': get_director(movie_obj.get('crew', [])),
                    'popularity': movie_obj.get('popularity'),
                    'vote_count': movie_obj.get('vote_count'),
                    'vote_average': movie_obj.get('vote_average'),
                    'release_date': movie_obj.get('release_date'),
                    'runtime': movie_obj.get('runtime'),
                    'img_url': POSTER_IMG_URL + movie_obj.get('poster_path', ''),
                }
                line = json.dumps(transformed_movie_obj, fout, sort_keys=True)
                fout.write(line + '\n')
