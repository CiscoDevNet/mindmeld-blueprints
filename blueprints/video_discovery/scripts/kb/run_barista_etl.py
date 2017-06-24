import luigi

from libs.run_etl import RunETL
from extract_tmdb import ExtractTMDB


class RunVideoDiscoveryETL(RunETL):
    def init_tasks(self):
        self.extract = ExtractTMDB
        # self.transform = TransformTMDB
        # self.load = LoadTMDB


if __name__ == '__main__':
    luigi.run()
