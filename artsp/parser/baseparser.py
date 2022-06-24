import csv
from abc import abstractmethod
import requests
import json
import abc
import threading
import datetime
import os
from artsp.conf import config
import time


class _ParserCollectDataIc(metaclass=abc.ABCMeta):
    """Data acquisition logic interface."""
    @abstractmethod
    def collect_posts_data(self, pages: list, count):
        """
        Сollection of a list of a certain amount of data.

        :param pages: list of start page and end page
        :type pages: list
        :param count: number of posts per page
        :type count: int
        :return: None
        """
        pass

    @abstractmethod
    def collect_post_detail_data(self, hash_id):
        """
        Collecting data from each post.

        :param hash_id: hash id of the post to process
        :type hash_id: str
        :return: list
        """
        pass

    @abstractmethod
    def collect_post_detail_data_slow(self, hash_id):
        """
        Collecting data from each post in slow mode.

        :param hash_id: hash id of the post to process
        :type hash_id: str
        :return: list
        """
        pass

    @abstractmethod
    def collect(self):
        """
        Main method to run collection of all data.

        :return: None
        """
        pass


class _ParserProcessingDataIc(metaclass=abc.ABCMeta):
    @abstractmethod
    def get_posts_data_hid(self, data):
        """
        Returns the hash id of each post.

        :param data: List of posts
        :type data: list
        :return: list
        """
        pass

    @abstractmethod
    def processing_post_detail(self, data):
        """
        Processing of received data.

        :param data: List of posts
        :type data: list
        :return: list
        """
        pass


class _ParserWriteDataIc(metaclass=abc.ABCMeta):
    @abstractmethod
    def write_data(processing_data, path):
        """
        Recording data with deletion of previously recorded.

        :param processing_data: Recording data.
        :type processing_data: list, dict
        :param path: Path to the file to be written.
        :return: None
        """
        pass

    @abstractmethod
    def append_json_data(processing_data, path):
        """
        Adding data to a file without deleting old data.

        :param processing_data: Recording data.
        :type processing_data: list, dict
        :param path: Path to the file to be written.
        :return: None
        """
        pass


class _ParserValidationDataIc(metaclass=abc.ABCMeta):
    pass


class _ConvertDataIc(metaclass=abc.ABCMeta):
    @abstractmethod
    def convert_to_csv(path):
        """
        :param path: Path to the file to be converted.
        :return: None
        """
        pass


class _ValidatorIc(metaclass=abc.ABCMeta):
    @abstractmethod
    def hid_validation(hid):
        """
        Checking for hash id in log file.

        :param hid: Hash id
        :return: bool
        """
        pass


class _BasePostParser(_ParserCollectDataIc):
    """The class represents the implementation of methods for collecting data."""
    _delay = 10

    def collect_post_detail_data(self, hash_id):
        thr = []
        post_detail_data = []
        t1 = datetime.datetime.now()
        for h in hash_id:
            t = threading.Thread(target=self._set_post_detail_data, args=(h, post_detail_data))
            thr.append(t)
            t.start()
        for tt in thr:
            tt.join()
        t2 = datetime.datetime.now()
        print(t2-t1)
        return post_detail_data

    def collect_post_detail_data_slow(self, hash_id):
        post_detail_data = []
        t1 = datetime.datetime.now()
        for x, i in enumerate(hash_id):
            time.sleep(self._delay)
            print(f'Set pdd -> {x+1}')
            self._set_post_detail_data(i, post_detail_data)
        t2 = datetime.datetime.now()
        print(t2-t1)
        return post_detail_data

    def _set_post_detail_data(self, hid, pdd):
        pdd.append(requests.get(url=f'https://www.artstation.com/projects/{hid}.json').json())

    def set_delay(self, val):
        """Setting a pause in slow mode."""
        self._delay = val
        return self


class _BaseProcessingData(_ParserProcessingDataIc):
    """The class represents the implementation of methods for processing data."""
    _tags_data = {}
    _posts_data = []
    _categories = {}

    def get_posts_data_hid(self, data):
        posts = [p for post in data for p in post['data']]
        posts_hash_ids = []
        for p in posts:
            posts_hash_ids.append(p['hash_id'])
        return posts_hash_ids

    def processing_post_detail(self, data):
        posts_detail_data = []
        posts_hid = []
        if _DataLog.get_hid_log() != None:
            for p in data:
                if _Validator.hid_validation(p['hash_id']):
                    posts_hid.append(p['hash_id'])
                    self._posts_detail_extraction(p)
                    self._tags_extraction(p)
                    self._categories_extraction(p)
        else:
            for p in data:
                posts_hid.append(p['hash_id'])
                self._posts_detail_extraction(p)
                self._tags_extraction(p)
                self._categories_extraction(p)
        _DataLog(posts_hid)
        return posts_detail_data

    def _posts_detail_extraction(self, p):
        """
        Extracting some fields from a post.

        :param p: Post
        :type p: dict
        :return: None
        """
        post = {'id': p['id'],
                'title': p['title'], 'cover_url': p['cover_url'], 'views_count': p['views_count'], 'likes_count': p['likes_count'],
                'comments_count': p['comments_count'], 'permalink': p['permalink'],
                'published_at': p['published_at'],
                'hash_id': p['hash_id']}
        self._posts_data.append(post)

    def _tags_extraction(self, p):
        """
        Extracting tags from a post.

        :param p: Post
        :type p: dict
        :return: None
        """
        tags = set()
        for tag in p['tags']:
            tags.add(tag.lower().lstrip('#'))
        for i in tags:
            if i in self._tags_data.keys():
                self._tags_data[i].append(p['hash_id'])
            else:
                self._tags_data[i] = []
                self._tags_data[i].append(p['hash_id'])

    def _categories_extraction(self, p):
        """
        Extracting categories from a post.

        :param p: Post
        :type p: dict
        :return: None
        """
        categories = set()
        for category in p['categories']:
            categories.add(category['name'])
        for i in categories:
            if i in self._categories.keys():
                self._categories[i].append(p['hash_id'])
            else:
                self._categories[i] = []
                self._categories[i].append(p['hash_id'])

    def get_categories(self):
        return self._categories

    def get_tags(self):
        return self._tags_data

    def get_posts(self):
        return self._posts_data


class _BaseDataWriter(_ParserWriteDataIc):
    """The class is an implementation of methods for writing data to a file."""
    @staticmethod
    def write_data(processing_data, path):
        with open(path, 'w', encoding="utf-8") as d:
            json.dump(processing_data, d, indent=4, ensure_ascii=False)

    @staticmethod
    def append_json_data(processing_data, path):
        with open(path, 'a', encoding="utf-8") as d:
            pass
        if processing_data:
            if os.stat(path).st_size != 0:
                with open(path, 'r', encoding="utf-8") as d:
                    json_data = json.load(d)

                __class__._datatype(json_data, processing_data)

                with open(path, 'w', encoding="utf-8") as d:
                    json.dump(json_data, d, indent=4, ensure_ascii=False)
            else:
                with open(path, 'w', encoding="utf-8") as d:
                    json.dump(processing_data, d, indent=4, ensure_ascii=False)

    @classmethod
    def _datatype(cls, load_data, p_data):
        """
        Determining the type of file to write.

        :param load_data: Loaded data from a file with records.
        :param p_data: Post data to be processed.
        :type p_data: list|dict
        :return: None
        """
        if type(p_data) == list:
            for i in p_data:
                load_data.append(i)
        if type(p_data) == dict:
            for i in p_data:
                if i in load_data.keys():
                    for j in p_data[i]:
                        load_data[i].append(j)
                else:
                     load_data[i] = p_data[i]


class _BaseDataConverter(_ConvertDataIc):
    @staticmethod
    def convert_to_csv(path):
        if _Validator.csv_data_list(path):
            __class__._convert_list_to_csv(path)
        if _Validator.csv_data_json(path):
            __class__._convert_json_to_csv(path)

    @classmethod
    def _convert_list_to_csv(cls, path):
        l_to = config.CSV_DIR
        with open(path, 'r', encoding='utf-8') as d:
            data = json.load(d)
        with open(l_to, 'w', encoding='utf-8') as d:
            csv_writer = csv.writer(d)
            count = 0
            for dda in data:
                if count == 0:
                    header = list(dda.keys())
                    csv_writer.writerow(header)
                    count += 1
                csv_writer.writerow(dda.values())

    # TODO: implement method
    @classmethod
    def _convert_json_to_csv(cls, path):
        pass


class _DataLog:
    """Creating a log."""
    def __init__(self, data: list):
        """
        :param data: Recording data.
        """
        self._data = data
        self._log_hid()

    def _log_hid(self):
        """Write hash id to log file."""
        _BaseDataWriter.append_json_data(self._data, config.LOG_HID_PATH)

    @staticmethod
    def get_hid_log():
        if os.stat(config.LOG_HID_PATH).st_size == 0:
            return None
        else:
            with open(config.LOG_HID_PATH, 'r', encoding='utf-8') as d:
                return json.load(d)


class _Validator(_ValidatorIc):
    @staticmethod
    def hid_validation(hid):
        """
        Checks if the hash id already exists in the log file.

        :param hid: Hash id.
        :type hid: str
        :return: bool
        """
        if not hid in _DataLog.get_hid_log():
            return True
        else:
            return False

    @staticmethod
    def csv_data_json(path):
        """Check json if file type is passed."""
        jdt = config.JsonDataType.Json
        if path in jdt:
            return True
        else:
            return False

    @staticmethod
    def csv_data_list(path):
        """Check list if file type is passed."""
        ldt = config.JsonDataType.List
        if path in ldt:
            return True
        else:
            return False