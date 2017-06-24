import luigi

from libs.tasks import DataProcessingTask


class BaristaDataProcessingTask(DataProcessingTask):
    app_name = luigi.Parameter(default='barista')


if __name__ == '__main__':
    luigi.run()
