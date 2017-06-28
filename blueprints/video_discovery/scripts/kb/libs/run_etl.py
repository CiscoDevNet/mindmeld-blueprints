import logging
import luigi


class RunETL(luigi.Task):
    is_complete = False

    def init_tasks(self):
        # TODO: initialize folders?
        raise NotImplementedError

    def requires(self):
        self.init_tasks()

    def complete(self):
        return self.is_complete

    def run(self):
        if hasattr(self, 'extract') and self.extract:
            logging.info('Running Extract task.')
            yield self.extract()
        else:
            logging.info('Skipping Extract task.')

        if hasattr(self, 'transform') and self.transform:
            logging.info('Running Transform task.')
            yield self.transform()
        else:
            logging.info('Skipping Transform task.')

        if hasattr(self, 'load') and self.load:
            logging.info('Running Load task.')
            yield self.load()
        else:
            logging.info('Skipping Load task.')

        self.is_complete = True


if __name__ == '__main__':
    luigi.run()
