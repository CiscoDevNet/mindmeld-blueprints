import luigi

from .transform_movies import TransformMovies
from .transform_tvs import TransformTVs
from .transform_episodes import TransformEpisodes


class TransformTMDB(luigi.WrapperTask):
    def requires(self):
        return [TransformMovies(), TransformTVs()]

    def run(self):
        yield TransformEpisodes()


if __name__ == '__main__':
    luigi.run()
