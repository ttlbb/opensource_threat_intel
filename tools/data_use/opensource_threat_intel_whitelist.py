# -*- coding: utf-8 -*-
import logging
import os
import sys
import time
import traceback
from multiprocessing import Process, Queue, Value

import MySQLdb
import pymongo
import requests

# 开源数据库
connection= pymongo.MongoClient('10.24.84.55', 27017)
db_auth = connection.opensource_threat_intel
db_auth.authenticate('opensource','opensource')
db = connection["opensource_threat_intel"]
coll = db["data_v1"]

PROCESS_NUM = 30

now_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time()))
# 执行时带上录入 前n天
start_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time() - 24 * 60 * 60 * int(sys.argv[1])))

log_xpath = "/tmp/%s.log" % os.path.basename(__file__)


def init_log(log_xpath):
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%Y %b %d %H:%M:%S',
                        filename=log_xpath,
                        filemode='a')


def get_level(credit):
    if credit >= 90:
        return 5
    elif credit > 10:
        return 3
    elif credit == 0:
        return 0
    else:
        return 1


def timestr2int(str_time):
    timeStamp = int(time.mktime(time.strptime(str_time, "%Y-%m-%dT%H:%M:%S")))
    return str(timeStamp)


def tran_tag(arg_tag):
    if arg_tag == 0:
        return 'ip'
    else:
        return 'url'



def import_type2my(arg_dirt, mysqldb, cursor):
    try:
        logging.info("import whitelist data: %s" % (arg_dirt['indicator']))
        data_type = tran_tag(arg_dirt['data_type'])
        credit_insert_log = 'insert into info_whitelist' \
                            '(type,value,source,level) ' \
                            'values(%s,%s,%s,%s ) ' \
                            'ON duplicate KEY UPDATE ' \
                            'source= VALUES (source), ' \
                            'level = VALUES (level)'
        credit_insert = [(data_type,
                          arg_dirt['indicator'],
                          arg_dirt['source'],
                          arg_dirt['description'])
                         ]
        cursor.executemany(credit_insert_log, tuple(credit_insert))

        mysqldb.commit()
    except:
        mysqldb.rollback()
        logging.error(traceback.format_exc())


def use_data(flag):
    # 信誉库
    mysqldb = MySQLdb.connect("10.6.109.1", "dashboard", "nsf0cus", "dashboard")
    cursor = mysqldb.cursor()
    while True:
        if bulk_queue.empty() and flag.value == 1:
            logging.info("quit queue")
            break
        else:
            try:
                d_tmp = bulk_queue.get(timeout=8)
                logging.info('start import ip %s ' % d_tmp['indicator'])
                import_type2my(d_tmp, mysqldb, cursor)
            except:
                logging.error(traceback.print_exc())
                pass
    sys.exit()


def get_data():
    logging.info("get data.....")
    # 无更新时间的数据源,查询created_time tag为白名单的
    query_not_alive = {"tag":11,"alive": False, "created_time": {"$gt": start_time, "$lte": now_time}}
    rets = coll.find(query_not_alive).batch_size(3000)
    for line in rets:
        bulk_queue.put(line)
    # 有更新时间的数据源,查询updated_time
    query_alive = {"tag":11,"alive": True, "updated_time": {"$gt": start_time, "$lte": now_time}}
    rets_alive = coll.find(query_alive).batch_size(3000)
    for line in rets_alive:
        bulk_queue.put(line)
    connection.close()


def run():
    end_flag = Value('i', 0)
    ps = [Process(target=use_data, args=(end_flag,)) for x in xrange(PROCESS_NUM)]
    for p in ps:
        p.start()
    get_data()
    end_flag.value = 1
    for p in ps:
        p.join()


if '__main__' == __name__:
    now = int(time.time())
    init_log(log_xpath)
    bulk_queue = Queue(100)
    session = requests.Session()
    run()
