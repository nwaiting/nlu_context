# -*- coding: UTF-8 -*-
import time

import redis

from utils.config_load import get_redis_pool
from utils.nameutil import _expire_time,_key_only_question_jdpin_with
# pool = redis.ConnectionPool(host='r2m-proxy.jdfin.local', port=6379, password='QueryServerService-robot-QAhistory')
pool = get_redis_pool()
rds = redis.Redis(connection_pool=pool)


class chatRecord:
    # 当前对话时间�?
    time = 0
    # 问题
    question = ''
    # rewrite的问�?
    reQuestion = ''
    # 答案
    answer = ''
    # 问答类型
    answerType = ''

    def __init__(self, answerType, time, question, answer, reQuestion):
        self.time = time
        self.question = question
        self.answer = answer
        self.answerType = answerType
        self.reQuestion = reQuestion


# #存储用户聊天历史数据
# def saveUserHistoryQA(jdpin, userQAHistory, sentence, answer):
#     if jdpin=='':
#         return
#     if ''==sentence or ''== answer:
#         return      
#     if len(userQAHistory)<5:
#         userhistoryQAstr=produceValueFromList(userQAHistory)
#         lastQAValue=str(time.time())+"|"+sentence+"|"+answer
#         userhistoryQAstr=userhistoryQAstr+lastQAValue
#         rds.set(jdpin, userhistoryQAstr)
#     else:
#         timeList=[]
#         for TQA in userQAHistory:
#             timeList.append(TQA.split("|")[0])
#         minTime=min(timeList)
#         minIndex=minTime.index(minTime)
#         userQAHistory[minIndex]=str(time.time())+"|"+sentence+"|"+answer
#         userhistoryQAstr=produceValueFromList(userQAHistory)
#         rds.set(jdpin, userhistoryQAstr)

def produceValueFromList(userQAHistory):  # 传入一个qa-history列表，拼接起来
    userQAstr = ''
    if len(userQAHistory) == 0:
        return userQAstr
    for userQAHistoryItem in userQAHistory:
        userQAstr = userQAstr + userQAHistoryItem + "++"
    return userQAstr[0:-2]


def getUserHistoryQA(jdpin):  # 获取用户历史记录，还没有根据'|'进行拆分
    historyQAList = []
    if jdpin == '':
        return historyQAList
    historyQA_json = rds.get(jdpin)
    if historyQA_json == "" or "None" == historyQA_json or None == historyQA_json:
        return historyQAList
    # encoding=chardet.detect(historyQA_json).get('encoding')
    historyQA_json_encoding = historyQA_json.decode('utf-8')
    historyQAList = str(historyQA_json_encoding).split("++")
    return historyQAList


# jdpin:用户ID，：answerType :模块类型，目前分为闲�?(1)、财务问�?(2)、新�?(3)
def getQAPairs(jdpin, answerType=None):  # 根据++  | 进行了拆分，实例化  chatrecord,存入列表
    chatRecordList = []
    if '' == jdpin:
        return chatRecordList
    userHistoryQAList = getUserHistoryQA(jdpin)
    for userHistoryQAListItem in userHistoryQAList:
        items = userHistoryQAListItem.split("|")
        if len(items) != 5:
            continue
        else:
            chatRecordList.append(chatRecord(items[0], items[1], items[2], items[3], items[4].strip('\n')))
    chatRecordList_sorted=sorted(chatRecordList,key=lambda x:x.time,reverse=False)
    if '' == answerType or None == answerType:
        return chatRecordList_sorted
    else:
        chatRecordList_sorted = cleanchatRecordList(chatRecordList_sorted, answerType)
        return chatRecordList_sorted

def cleanchatRecordList(chatRecordList, answerType):  # 根据 answertype 对 chatrecord 实例进行了过滤
    cleanChatRecordList = []
    if len(chatRecordList) == 0 or None == answerType:
        return cleanChatRecordList
    for chatRecordListItem in chatRecordList:
        if str(answerType) == chatRecordListItem.answerType:
            cleanChatRecordList.append(chatRecordListItem)
    return cleanChatRecordList


# jdpin:用户ID�?     question：问�?  answer�? 答案    answerType：模块类型，目前分为闲聊(1)、财务问�?(2)、新�?(3)
def setQAPairs(jdpin, question, answer, answerType):  # 将 q，q，ts跟之前的qa记录组合起来，再次存入rds，最多记录5个 历史会话
    if jdpin == '':
        return
    if '' == question or '' == answer or '' == answerType or None == answerType:
        return
    userQAHistory = getUserHistoryQA(jdpin)
    if len(userQAHistory) < 5:
        userhistoryQAstr = produceValueFromList(userQAHistory)
        lastQAValue = str(answerType) + "|" + str(time.time()) + "|" + question + "|" + answer + "|" + question
        if userhistoryQAstr == '':
            userhistoryQAstr = lastQAValue
        else:
            userhistoryQAstr = userhistoryQAstr + "++" + lastQAValue
        rds.set(jdpin, userhistoryQAstr)
    else:
        timeList = []
        for TQA in userQAHistory:
            xxList = TQA.split("|")
            if len(xxList) > 1:
                timeList.append(xxList[1])
        minTime = min(timeList)
        minIndex = timeList.index(minTime)
        userQAHistory[minIndex] = str(answerType) + "|" + str(
            time.time()) + "|" + question + "|" + answer + "|" + question
        userhistoryQAstr = produceValueFromList(userQAHistory)
        rds.set(jdpin, userhistoryQAstr)
    rds.expire(jdpin,_expire_time)
def setQARePairs(jdpin, question, requestion, answer, answerType):
    if jdpin == '':
        return
    if '' == question or '' == answer or '' == answerType or None == answerType:
        return
    userQAHistory = getUserHistoryQA(jdpin)
    if len(userQAHistory) < 5:
        userhistoryQAstr = produceValueFromList(userQAHistory)
        lastQAValue = str(answerType) + "|" + str(time.time()) + "|" + question + "|" + answer + "|" + requestion
        if userhistoryQAstr == '':
            userhistoryQAstr = lastQAValue
        else:
            userhistoryQAstr = userhistoryQAstr + "++" + lastQAValue
        rds.set(jdpin, userhistoryQAstr)
    else:
        timeList = []
        for TQA in userQAHistory:
            timeList.append(TQA.split("|")[1])
        minTime = min(timeList)
        minIndex = timeList.index(minTime)
        userQAHistory[minIndex] = str(answerType) + "|" + str(
            time.time()) + "|" + question + "|" + answer + "|" + requestion
        userhistoryQAstr = produceValueFromList(userQAHistory)
        rds.set(jdpin, userhistoryQAstr)


def setUserInfo(jdpin, infoKey, infoValue):  # 一个用户下可以存不同的key-value
    if '' == jdpin or '' == infoKey or '' == infoValue:
        return
    jdpininfo = str(jdpin) + '|info'
    user_info_dict = {}
    user_info_dict = getUserInfo(jdpin)
    user_info_dict[infoKey] = infoValue
    rds.set(jdpininfo, str(user_info_dict))


def getUserInfo(jdpin):
    jdpininfo = str(jdpin) + '|info'
    historyInfo_json = rds.get(jdpininfo)
    if None == historyInfo_json or '' == historyInfo_json:
        return {}
    historyInfo_json_encoding = historyInfo_json.decode('utf-8')
    user_info_dict = eval(historyInfo_json_encoding)
    return user_info_dict


def getUserStatus(jdpin, infoKey):
    jdpininfo = str(jdpin) + '|' + str(infoKey)
    historyInfo_json = rds.get(jdpininfo)
    if None == historyInfo_json or '' == historyInfo_json:
        return None
    historyInfo_json_encoding = historyInfo_json.decode('utf-8')
    return historyInfo_json_encoding


def setUserStatus(jdpin, infoKey, infoValue):
    if '' == jdpin or '' == infoKey or '' == infoValue:
        return
    jdpininfo = str(jdpin) + '|' + str(infoKey)
    rds.set(jdpininfo, infoValue)


def insert_into_rds(jdpin, part_key_in, values_in):
    # print('insert_into_rds 调用==>',jdpin, part_key_in, values_in)
    key_str = str(jdpin)  + part_key_in
    old_dict = get_from_rds(jdpin, part_key_in)
    # for key,value in values_in.items():
    #     if old_dict.get(key):
    #         value.extend(old_dict[key])
    #     else:
    #         pass
    if old_dict:
        for key, value in old_dict.items():
            if values_in.get(key):
                for value_ready_iter in values_in[key]:
                    if value_ready_iter in value:
                        value.remove(value_ready_iter)
                value.extend(values_in[key])
            else:
                pass
    else:
        old_dict = values_in
    rds.set(key_str, str(old_dict))
    rds.expire(key_str,_expire_time)
    return True


def get_from_rds(jdpin, part_key_in):
    key_str = str(jdpin)  + part_key_in
    values_ret = rds.get(key_str)
    if not values_ret:
        values_ret = b'{}'
    # print('values_ret rds get  key:{}\t value'.format(key_str), values_ret.decode('utf-8'))
    return eval(values_ret)


if __name__ == "__main__":
    # setUserInfo('1234', '安行万里的投保年龄', '123')
    # setUserInfo('1234', '安行万里的保障地区', '123')
    # setUserInfo('1234', '安行万里的保险事故通知有哪些', '123')
    # setUserInfo('1234', '123', '123')
    # r=getUserInfo('1234')
    # print(r)
    import sys

    sys.path.append('../../')
    # from online.nlu.slots_maintain import SlotsMaintain
    from online.nlu.preprocess import Preprocess
    from online.nlu.query_rewrite import NerDeal

    preprocess_class = Preprocess()
    nerdeal_class = NerDeal()
    # slots_maintain_class = SlotsMaintain()

    jdpin = '12345'
    sententc = '安行万里的投保年龄'
    answer = '没问题'
    setQAPairs(jdpin, sententc, answer, 1)
    # print(rds.keys())
    sententc = '安行万里的保障地区'
    answer = '没问题'
    setQAPairs(jdpin, sententc, answer, 1)
    sententc = '安行万里的保险事故通知有哪些'
    answer = '没问题'
    setQAPairs(jdpin, sententc, answer, 1)
    sententc = '目的地填写错误怎么办'
    answer = '没问题'
    setQAPairs(jdpin, sententc, answer, 1)
    sententc = '什么是定期寿险'
    answer = '没问题'
    setQAPairs(jdpin, sententc, answer, 1)
    result = getQAPairs(jdpin, 1)
    print(result)
    answer = '没问题'
    rds.set('longzai1119e1161|semantics_flag',1)
    # while True:
    #     sententc = input('输入 history 数据')
    #     jdpin = input('输入 jdpin')
    #     setQAPairs(jdpin, sententc, answer, 1)
    #     result = getQAPairs(jdpin, 1)
    #
    #     sentence_synonym, words_jieba = preprocess_class.process(sententc)
    #     words_with_context, slots_maintain, label2entities_cur_dict = nerdeal_class.replace_with_context(
    #         sentence_synonym, words_jieba, jdpin)
    #     slots_maintain_class.update_slots(label2entities_cur_dict, jdpin)
    #
    #     print('显示历史数据', result)
