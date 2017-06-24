import luigi

from extract.extract_all import ExtractAll


class ExtractTMDB(luigi.WrapperTask):
    # TODO: remove extract?
    def requires(self):
        return ExtractAll()


if __name__ == '__main__':
    luigi.run()
