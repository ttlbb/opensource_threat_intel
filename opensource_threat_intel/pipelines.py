# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
from collections import OrderedDict

import pymongo
from scrapy.conf import settings


class MongoPipeline(object):
    def __init__(self):
        connection = pymongo.MongoClient(settings['MONGO_HOST'], settings['MONGO_PORT'])
        db_auth = connection.opensource_threat_intel
	if settings['MONGO_USER']!='' and  settings['MONGO_PASS']!='':
		db_auth.authenticate(settings['MONGO_USER'], settings['MONGO_PASS'])
        self.db = connection[settings['MONGO_DB']]
        self.collection = self.db[settings['MONGO_COLLECTION']]

    def process_item(self, item, spider):
        self.collection.update(
            {"indicator": item["indicator"], "tag": item["tag"]},
            {
                "$set": {"updated_time": item["updated_time"]},
                "$setOnInsert": {
                    "indicator": item["indicator"],
                    "data_type": item["data_type"],
                    "tag": item["tag"],
                    "source": item["source"],
                    "confidence": item["confidence"],
                    "alive": item["alive"],
                    "description": item['description'],
                    "created_time": item["created_time"],
                }
            },
            upsert=True
        )
        return item


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('data_utf8.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(OrderedDict(item), ensure_ascii=False, sort_keys=False) + "\n"
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()
