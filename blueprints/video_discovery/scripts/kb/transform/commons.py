import logging
import luigi
import sys
import os

sys.path.append('..')
from video_task import VideoDataProcessingTask  # noqa: F401
from utils import dump_json, load_json, load_plain_json  # noqa: F401
from libs.tasks import ReadLocalFile  # noqa: F401


class MergeCredit(VideoDataProcessingTask):
    doc_id = luigi.Parameter()
    doc_type = luigi.Parameter()
    detail_dir = luigi.Parameter()
    credit_dir = luigi.Parameter()
    output_dir = luigi.Parameter()

    def requires(self):
        filename = u'{}_{}.json'.format(self.doc_type, self.doc_id)
        detail_file = os.path.join(self.detail_dir, filename)
        credit_file = os.path.join(self.credit_dir, filename)

        return [ReadLocalFile(file_path=detail_file), ReadLocalFile(file_path=credit_file)]

    def output(self):
        filename = u'{}_{}.json'.format(self.doc_type, self.doc_id)
        return self.get_output_target(filename)

    def run(self):
        detail = load_json(self.input()[0])
        credit = load_json(self.input()[1])

        detail.update(credit)
        dump_json(self.output(), detail)


class MergeMovieInfo(MergeCredit):
    pass


class MergeTVInfo(MergeCredit):
    pass


class TransformDocuments(VideoDataProcessingTask):
    input_file = luigi.Parameter()
    doc_type = luigi.Parameter()

    def requires(self):
        if self.doc_type == 'movie':
            mergeTask = MergeMovieInfo
        elif self.doc_type == 'tv':
            mergeTask = MergeTVInfo

        doc_ids = load_plain_json(self.input_file)
        logging.info('Getting {:d} {}...'.format(len(doc_ids), self.doc_type))
        return [
            mergeTask(doc_id=doc_id)
            for doc_id in doc_ids
        ]

    def output(self):
        filename = u'transformed_{}s.jsonl'.format(self.doc_type)
        return self.get_output_target(filename)

    def run(self):
        self.transform(self.input(), self.output())

    @staticmethod
    def transform(in_targets, out_target):
        raise NotImplementedError


def get_names(raw_objs):
    """
    [{'name': 'Action', 'id': 28}, {'name': 'Adventure', 'id': 12}]
    """
    return [obj['name'] for obj in raw_objs]


def get_director(raw_crew):
    candidates = [obj['name'] for obj in raw_crew if obj.get('job') == 'Director']
    if candidates:
        return candidates[0]
