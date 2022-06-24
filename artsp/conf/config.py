import conf.config as conf
CONF_PATH = 'D:/Python/parsing/arts/conf/config.py'

LOG_HID_PATH = conf.LOG_HID_PATH
POSTS_PATH = conf.POSTS_PATH
TAGS_PATH = conf.TAGS_PATH
CATEGORIES_PATH = conf.CATEGORIES_PATH
CSV_DIR = conf.CSV_DIR


class SEC_NAME:
    community = 'community'
    trending = 'trending'


class JsonDataType:
    Json = [
        TAGS_PATH,
        CATEGORIES_PATH,
    ]
    List = [
        LOG_HID_PATH,
        POSTS_PATH
    ]