import luigi

from libs.run_etl import RunETL
from extract_tmdb import ExtractTMDB
from transform.transform_tmdb import TransformTMDB


class RunVideoDiscoveryETL(RunETL):
    def init_tasks(self):
        self.extract = ExtractTMDB
        self.transform = TransformTMDB
        # self.load = LoadTMDB


class RunVideoDiscoveryT(RunETL):
    def init_tasks(self):
        self.transform = TransformTMDB


if __name__ == '__main__':
    luigi.run()
