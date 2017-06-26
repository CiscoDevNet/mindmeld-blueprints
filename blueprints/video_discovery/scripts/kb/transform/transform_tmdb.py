import luigi

from .transform_movies import TransformMovies
from .transform_tvs import TransformTVs


class TransformTMDB(luigi.WrapperTask):
    def requires(self):
        return [TransformMovies(), TransformTVs()]


if __name__ == '__main__':
    luigi.run()
