import logging
import luigi
import sys

from .commons import GetTMDB

sys.path.append('..')
from video_task import VideoDataProcessingTask  # noqa: F401
from libs.tasks import RequestAPI  # noqa: F401
from utils import load_plain_json  # noqa: F401


class GetCredits(GetTMDB):
    """
    Get the credits of a single tv/movie.
    """
    doc_type = luigi.Parameter()
    doc_id = luigi.Parameter()

    def requires(self):
        output_filename = '{}_{}.json'.format(self.doc_type, self.doc_id)
        url = '{:s}/{:d}/credits?api_key={:s}'.format(self.tmdb_endpoint, self.doc_id, self.api_key)
        return RequestAPI(url=url,
                          output_dir=self.output_dir,
                          output_filename=output_filename)


class GetAllCredits(luigi.WrapperTask):
    input_file = luigi.Parameter()
    doc_type = luigi.Parameter()
    tmdb_endpoint = luigi.Parameter()
    output_dir = luigi.Parameter()

    def requires(self):
        doc_ids = load_plain_json(self.input_file)
        logging.info('Getting {:d} {} credits...'.format(len(doc_ids), self.doc_type))
        return [
            GetCredits(tmdb_endpoint=self.tmdb_endpoint,
                       output_dir=self.output_dir,
                       doc_type=self.doc_type,
                       doc_id=doc_id)
            for doc_id in doc_ids
        ]


class GetMovieCredits(GetAllCredits):
    pass


class ExtractMovieCredits(luigi.WrapperTask):
    def requires(self):
        return GetMovieCredits()


class GetTVCredits(GetAllCredits):
    pass


class ExtractTVCredits(luigi.WrapperTask):
    def requires(self):
        return GetTVCredits()


if __name__ == '__main__':
    luigi.run()
