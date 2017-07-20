import luigi
import sys
import json

from .commons import get_countries, get_directors, get_names, get_poster_img_url
from .commons import get_release_date, get_release_year
from .commons import TransformDocuments
from .constants import TYPE_MOVIE

sys.path.append('..')
from video_task import VideoDataProcessingTask  # noqa: F401
from utils import load_json  # noqa: F401


class TransformMovies(TransformDocuments):
    input_file = luigi.Parameter()

    @staticmethod
    def transform(in_target, out_target):
        fout = out_target.open('w')
        fin = in_target.open('r')
        for line in fin:
            movie_obj = json.loads(line)
            transformed_movie_obj = {
                'doc_type': TYPE_MOVIE,
                'title': movie_obj['title'],
                'id':  '{}_{}'.format(TYPE_MOVIE, movie_obj['id']),
                'imdb_id': movie_obj.get('imdb_id'),
                'overview': movie_obj.get('overview'),
                'genres': get_names(movie_obj.get('genres', [])),
                'cast': get_names(movie_obj.get('cast', [])),
                'countries': get_countries(movie_obj.get('production_countries', [])),
                'directors': get_directors(movie_obj.get('crew', [])),
                'popularity': movie_obj.get('popularity'),
                'vote_count': movie_obj.get('vote_count'),
                'vote_average': movie_obj.get('vote_average'),
                'release_date': get_release_date(movie_obj.get('release_date')),
                'release_year': get_release_year(movie_obj.get('release_date')),
                'runtime': movie_obj.get('runtime'),
                'img_url': get_poster_img_url(movie_obj.get('poster_path', '')),
            }
            line = json.dumps(transformed_movie_obj, fout, sort_keys=True)
            fout.write(line + '\n')
        fout.close()
        fin.close()
