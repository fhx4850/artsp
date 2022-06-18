from abc import abstractmethod


class _ParserDataIs:
    @abstractmethod
    def collect_data(self, pages: list, count):
        pass

    @abstractmethod
    def processing_data(self, data):
        pass


class _ParserWriteDataIs:
    @abstractmethod
    def write_data(self, processing_data):
        pass


class _ParserValidationDataIs:
    pass

class ArtParser(_ParserDataIs, _ParserWriteDataIs):
    def __init__(self, pages: list, count=100):
        pass