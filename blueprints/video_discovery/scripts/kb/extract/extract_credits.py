import logging
import luigi
import sys
import json

from .commons import API_KEY

sys.path.append('..')
from video_task import VideoDataProcessingTask  # noqa: F401
from libs.tasks import request_api  # noqa: F401
from utils import load_plain_json  # noqa: F401


class GetAllCredits(VideoDataProcessingTask):
    input_file = luigi.Parameter()
    doc_type = luigi.Parameter()
    tmdb_endpoint = luigi.Parameter()
    output_dir = luigi.Parameter()

    def run(self):
        doc_ids = load_plain_json(self.input_file)
        logging.info('Getting {:d} {} credits...'.format(len(doc_ids), self.doc_type))

        fout = self.output().open('w')
        for doc_id in doc_ids:
            url = '{:s}/{:d}/credits?api_key={:s}'.format(self.tmdb_endpoint, doc_id, API_KEY)
            response = request_api(url)
            if not response:
                continue
            line = '{}\n'.format(json.dumps(response.json(), sort_keys=True))
            fout.write(line)
        fout.close()

    def output(self):
        filename = '{}_credits.jsonl'.format(self.doc_type)
        return self.get_output_target(filename)


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
