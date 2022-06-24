import json
from baseparser import _BasePostParser, _BaseProcessingData, _BaseDataWriter, _BaseDataConverter
import requests
from artsp.conf import config as conf
import time


class _Parser(_BasePostParser):
    def __init__(self, pages: list, count, section_name):
        self._data = list()
        self._pages = pages
        self._count = count
        self.ps_data = None
        self._post_detail_data = None
        self._section_name = section_name

    def collect_posts_data(self, pages: list, count):
        for i in range(pages[0], pages[1]+1):
            print(f'Collect data, pages: {i}/{pages[1]}')
            responce = requests.get(
                url=f'https://www.artstation.com/api/v2/community/explore/projects/{self._section_name}.json?page={i}&dimension=all&per_page={count}')
            self._data.append(responce.json())
            time.sleep(10)

    def write_posts_data(self, dir: str):
        _DataWriter.write_data(self.ps_data.processing_post_detail(self._post_detail_data), dir)

    def append_posts_data(self):
        self.ps_data.processing_post_detail(self._post_detail_data)
        _DataWriter.append_json_data(self.ps_data.get_tags(), conf.TAGS_PATH)
        _DataWriter.append_json_data(self.ps_data.get_posts(), conf.POSTS_PATH)
        _DataWriter.append_json_data(self.ps_data.get_categories(), conf.CATEGORIES_PATH)


    def get_processing_post_detail_data(self, path: str):
        with open(path, 'r', encoding='UTF-8') as d:
            return json.load(d)

    def get_post_detail_data(self):
        return self._post_detail_data

    def get_data(self):
        return self._data

    def collect(self, slow_mode=True):
        self.collect_posts_data(self._pages, self._count)
        self.ps_data = _ProcessingData(self._data)
        if slow_mode:
            self._post_detail_data = self.collect_post_detail_data_slow(self.ps_data.get_hash_ids())
        else:
            self._post_detail_data = self.collect_post_detail_data(self.ps_data.get_hash_ids())


class _ProcessingData(_BaseProcessingData):
    def __init__(self, data):
        self._data = data
        self._hash_ids = self.get_posts_data_hid(self._data)

    def get_hash_ids(self):
        return self._hash_ids


class _DataWriter(_BaseDataWriter):
    pass


class DataConverter(_BaseDataConverter):
    pass


class TrendingParser(_Parser):
    def __init__(self, pages: list, count):
        if pages[1] > 500 or pages[0] < 1:
            print('!!! Enter correct pages')
            return
        if count > 100 or count < 10 or count % 2 != 0:
            print('!!! Enter correct count')
            return
        super().__init__(pages, count, conf.SEC_NAME.trending)


if __name__ == '__main__':
    cp = TrendingParser([1, 1], 100)
    cp.collect(slow_mode=False)
    cp.append_posts_data()
