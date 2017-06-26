import luigi

from libs.tasks import DataProcessingTask


class VideoDataProcessingTask(DataProcessingTask):
    app_name = luigi.Parameter(default='video-discovery')


if __name__ == '__main__':
    luigi.run()
