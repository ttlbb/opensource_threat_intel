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

'''
1. 修复mongo内存字段储格式不统一问题，全部设置为string
2. 修复更新机制，有更新时间的数据源通过updated_time更新

'''
# 开源数据库
connection= pymongo.MongoClient('10.24.84.55', 27017)
db_auth = connection.opensource_threat_intel
db_auth.authenticate('opensource','opensource')
db = connection["opensource_threat_intel"]
coll = db["data_v1"]


PROCESS_NUM = 5

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


# 开源数据中的数据类型 大于9的 信誉云没有，默认认为是可疑的
def tran_tag(arg_tag):
    if arg_tag > 9:
        return 0
    else:
        return arg_tag


# 开源数据不提供更新时间的取当前录入时间录入数据
def get_attack_time(arg_time, created_time):
    if arg_time == 'none':
        return created_time
    else:
        return arg_time


# 通过created_time 保证数据不会多次录入，同步爬虫库内的创建时间（同一条数据这个时间是不会再变化的）
def import_type2mg(arg_dirt, co):
    try:
        logging.info("import history data: %s" % (arg_dirt['indicator']))
        credit = int(arg_dirt['confidence']) * 8
        dict_tmp = {}
        dict_tmp.update({"attack_type": str(tran_tag(arg_dirt['tag']))})
        dict_tmp.update({"source": arg_dirt['source']})
        dict_tmp.update({"credit": credit})
        dict_tmp.update(
            {"attack_time": timestr2int(get_attack_time(arg_dirt['updated_time'], arg_dirt['created_time']))})
        dict_tmp.update({"insert_time": timestr2int(arg_dirt['created_time'])})

        co.update({"ip": arg_dirt['indicator']},
                  {"$addToSet": {"history": dict_tmp},
                   "$set": {"create_time": timestr2int(arg_dirt['created_time'])}},
                  upsert=True)
    except:
        logging.error(traceback.format_exc())


def import_type2my(arg_dirt, mysqldb, cursor):
    try:
        logging.info("import reputation data: %s" % (arg_dirt['indicator']))
        updatetime = get_attack_time(arg_dirt['updated_time'], arg_dirt['created_time'])
        credit_insert_log = 'insert into credit_ipv4_nsfocus ' \
                            '(update_time,ip,credit,attack_type,source) ' \
                            'values(%s,%s,%s,%s,%s ) ' \
                            'ON duplicate KEY UPDATE ' \
                            'update_time= VALUES (update_time), ' \
                            'credit= VALUES (credit), ' \
                            'attack_type= VALUES (attack_type), ' \
                            'source= VALUES (source)'
        credit = int(arg_dirt['confidence']) * 8
        credit_insert = [(timestr2int(arg_dirt['created_time']),
                          arg_dirt['indicator'],
                          credit,
                          tran_tag(arg_dirt['tag']),
                          arg_dirt['source'])
                         ]
        cursor.executemany(credit_insert_log, tuple(credit_insert))

        # reputation
        reputation_insert_log = 'insert into reputation_ipv4_nsfocus ' \
                                '(create_time,detect_time,update_time,ip,credit_level,attack_type) ' \
                                'values(%s,%s,%s,%s,%s,%s ) ' \
                                ' ON duplicate KEY UPDATE ' \
                                'update_time= VALUES (update_time),' \
                                'detect_time= VALUES (detect_time), ' \
                                ' credit_level= VALUES (credit_level), ' \
                                'attack_type= VALUES (attack_type), ' \
                                'create_time= IFNULL(create_time,unix_timestamp())'
        credit_level = get_level(credit)
        reputation_insert = [(timestr2int(arg_dirt['created_time']),
                              timestr2int(updatetime),
                              now,
                              arg_dirt['indicator'],
                              credit_level,
                              tran_tag(arg_dirt['tag']))
                             ]
        cursor.executemany(reputation_insert_log, tuple(reputation_insert))
        mysqldb.commit()
    except:
        mysqldb.rollback()
        logging.error(traceback.format_exc())


def use_data(flag):
    # ip 恶意历史库
    con = pymongo.MongoClient('10.24.45.133', 27017)
    mdb = con["credit_history"]
    co = mdb["ip_history_v1"]
    # 信誉库
    mysqldb = MySQLdb.connect("10.6.109.1", "credit", "qweO1!k2ndP", "credit")
    cursor = mysqldb.cursor()
    while True:
        if bulk_queue.empty() and flag.value == 1:
            logging.info(" quit queue ")
            break
        else:
            try:
                d_tmp = bulk_queue.get(timeout=8)
                logging.info('start import ip %s ' % d_tmp['indicator'])
                import_type2mg(d_tmp, co)
                import_type2my(d_tmp, mysqldb, cursor)
            except:
                logging.error(traceback.print_exc())
                pass
    con.close()


def get_data():
    logging.info("get data.....")
    # 无更新时间的数据源,查询created_time
    query_not_alive = {"data_type":0,"alive": False, "created_time": {"$gt": start_time, "$lte": now_time}}
    rets = coll.find(query_not_alive).batch_size(3000)
    logging.info(query_not_alive)
    for line in rets:
        bulk_queue.put(line)
    # 有更新时间的数据源,查询updated_time
    query_alive = {"data_type":0,"alive": True, "updated_time": {"$gt": start_time, "$lte": now_time}}
    rets_alive = coll.find(query_alive).batch_size(3000)
    logging.info(query_alive)
    for line in rets_alive:
        bulk_queue.put(line)


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
