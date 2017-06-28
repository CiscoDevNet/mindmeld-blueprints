import logging
import luigi
import sys
import json

from .constants import POSTER_IMG_URL

sys.path.append('..')
from video_task import VideoDataProcessingTask  # noqa: F401
from utils import dump_json, load_json, load_plain_json  # noqa: F401
from libs.tasks import ReadLocalFile  # noqa: F401


def load_credits(credit_file):
    objs = []
    with open(credit_file, 'r') as fp:
        for line in fp:
            objs.append(json.loads(line))
    logging.info('Got {} credits from {}'.format(len(objs), credit_file))
    return {
        obj['id']: obj
        for obj in objs
    }


class MergeCredit(VideoDataProcessingTask):
    doc_type = luigi.Parameter()
    detail_file = luigi.Parameter()
    credit_file = luigi.Parameter()
    output_dir = luigi.Parameter()

    def output(self):
        filename = u'{}_merged.jsonl'.format(self.doc_type)
        return self.get_output_target(filename)

    def run(self):
        credit_dict = load_credits(self.credit_file)
        fin = open(self.detail_file, 'r')
        fout = self.output().open('w')
        for line in fin:
            detail = json.loads(line)
            detail_id = detail['id']
            credit_obj = credit_dict.get(detail_id)
            if not credit_obj:
                logging.error('Cannot find credit for {} {}.'.format(self.doc_type, detail_id))
                continue
            detail.update(credit_obj)
            new_line = '{}\n'.format(json.dumps(detail, sort_keys=True))
            fout.write(new_line)
        fin.close()
        fout.close()


class MergeMovieInfo(MergeCredit):
    pass


class MergeTVInfo(MergeCredit):
    pass


class TransformDocuments(VideoDataProcessingTask):
    doc_type = luigi.Parameter()

    def requires(self):
        if self.doc_type == 'movie':
            mergeTask = MergeMovieInfo
        elif self.doc_type == 'tv':
            mergeTask = MergeTVInfo

        # logging.info('Getting {:d} {}...'.format(len(doc_ids), self.doc_type))
        return mergeTask()

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


def get_directors(raw_crew):
    return [obj['name'] for obj in raw_crew if obj.get('job') == 'Director']


def get_poster_img_url(poster_path):
    if not poster_path:
        return ''
    else:
        return POSTER_IMG_URL + poster_path


def get_release_date(release_date):
    if not release_date:
        return None
    else:
        return release_date
