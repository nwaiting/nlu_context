import collections
import time

from online.utils.nameutil import ContextNames as cname, FieldClassifyNames as fcname
from online.utils.nameutil import _expire_time, _threshold_num_rounds


# 从 chatrecord中获取 多轮 slots，反出
# 解决问题： 1. 根据时间决定是否继承；  2.如果上一句是 推荐：询问产品，则从问题中提取slots，则从之前存储的slots
# 处理方式：  1.每个问题，提取slots存储；
#           2.每个答案，根据问题类型，提取slots； 目前需要提取slots的问题类型：推荐
#             每个问题，保持上一个slots和当前slots
#           3.
#
#
#


def initialize_slots_dict():
    slots_dict = collections.defaultdict(list)
    for key_iter in cname:
        slots_dict[key_iter.value] = []
    return slots_dict


def filter_instances_by_time(slots_instances):
    slots_instances_filtered = []
    time_cur = time.time()
    for slots_instance_iter in slots_instances:
        if time_cur - slots_instance_iter['time'] > _expire_time:
            pass
        else:
            slots_instances_filtered.append(slots_instance_iter)
    return slots_instances_filtered


def filter_instances_by_num(slots_instances):
    return slots_instances[-1 * _threshold_num_rounds:]


def get_slots_by_key(slots_instances_in, key_in):
    slots_dict_merged = initialize_slots_dict()
    for slots_dict_iter in slots_instances_in:
        for key_raw in cname:
            key = key_raw.value
            if key in slots_dict_iter:
                value_inserted = slots_dict_iter[key_in][key]
                if value_inserted in slots_dict_merged[key]:
                    slots_dict_merged[key].remove(value_inserted)
                slots_dict_merged[key].append(value_inserted)
    return slots_dict_merged


def get_slots_from_question_and_answer(slots_instances_in):
    slots = slots_instances_in
    slots_dict_merged = initialize_slots_dict()

    for slots_dict_iter in slots:
        for key_raw in cname:
            key = key_raw.value
            value_answer = slots_dict_iter['slots_answer'].get(key)
            if value_answer:
                slots_dict_merged[key].extend(value_answer)
            value_question = slots_dict_iter['slots_question'].get(key)
            if value_question:
                slots_dict_merged[key].extend(value_question)

    return slots_dict_merged


class SlotsSingleQA(object):
    def __init__(self):
        self.__dict__ = {}
        self.__dict__['time']=None,
        self.__dict__['question']= '',
        self.__dict__['slots_question'] = initialize_slots_dict()
        # self.__dict__['slots_question']= collections.defaultdict(list),
        self.__dict__['answer']= '',
        self.__dict__['slots_answer'] = initialize_slots_dict()
        # self.__dict__['slots_answer']= collections.defaultdict(list),
        self.__dict__['domain_classification']='',
        self.__dict__['sentence_pattern_classification']=''
    def __setitem__(self, key, value):
        if key in self.__dict__:
            self.__dict__[key] = value

    def __getitem__(self, item):
        return self.__dict__[item]


class SlotsQAMulti(object):
    _slots_question_and_answer = 'question_and_answer'

    def __init__(self):
        self._slots_rounds = []

    def _get_instances(self, field_in):
        field_containter = {field_in}
        if field_in == fcname.alldomain.value:
            for name_iter in fcname:
                field_containter.add(name_iter.value)
        slots_containers = []

        for slot_qa_iter in self._slots_rounds:
            field_cur = slot_qa_iter['domain_classification']
            if field_cur in field_containter:
                slots_containers.append(slot_qa_iter)
            else:
                pass
        return slots_containers

    def _filter_instances(self, slots_instances):
        slots_instances_timefiltered_numfiltered = filter_instances_by_num(slots_instances)
        slots_instances_timefiltered = filter_instances_by_time(slots_instances_timefiltered_numfiltered)
        return slots_instances_timefiltered

    def insert(self, **kwargs):
        # 插入一个qa 槽位实例
        slots_single_class = SlotsSingleQA()
        for key, value in kwargs.items():
            if key in slots_single_class.__dict__:
                if key.startswith('slots_'):
                    assert isinstance(value, dict), '输入value相关字段不是key-value,list 形式'
                    for k1, v1 in value.items():
                        assert isinstance(v1, list), 'slots 各个元素value，需要是 list 形式'
                slots_single_class[key] = value
            else:
                raise ValueError('key={} 不在预设字段内'.format(key))
        self._slots_rounds.append(slots_single_class)

    def update_by_index(self, index, **kwargs):
        # 更新一个槽位实例
        slots_single_class = self._slots_rounds[index]
        for key, value in kwargs.items():
            if key in slots_single_class.__dict__:
                slots_single_class[key] = value
            else:
                raise ValueError('key={} 不在预设字段内'.format(key))

    def get_instances(self, field_in):
        slots_containers = self._get_instances(field_in)
        slots_instances_filtered = self._filter_instances(slots_containers)
        return slots_instances_filtered

    def get_slots_by_key(self, field_in, key_in='question_and_answer'):
        # slots_question,slots_answer,question_and_answer
        instances_filtered = self.get_instances(field_in)
        if key_in == self._slots_question_and_answer:
            return get_slots_from_question_and_answer(instances_filtered)
        else:
            return get_slots_by_key(instances_filtered, key_in)

    def get_slots_by_index(self, field_in, key_in, index_in):
        instances_filtered = self.get_instances(field_in)
        if abs(index_in)>len(instances_filtered):
            return {}
        instance = instances_filtered[index_in]
        if key_in == self._slots_question_and_answer:
            return get_slots_from_question_and_answer([instance])
        else:
            return instance[key_in]

    def delete(self):
        # 删除一个槽位实例
        pass
