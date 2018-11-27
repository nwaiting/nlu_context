import jieba
import time
from online.nlu.preprocess import Preprocess
from online.utils.funcs import Singleton
from online.nlu.slots_maintain import SlotsQAMulti
from online.utils.nameutil import FieldClassifyNames as fcname
"""
    1.用户历史n轮对话
    2.用户当前状态
    3.用户上一轮存储 处理，几个domain，是否是推荐。。。。
    4.用户历史对话存储获取
"""


class User(object):
    def __init__(self):
        self.__dict__ = {'domain_classification': None,
                    'str_raw': None,
                    'str_synonym': None,
                    'str_raw_cut': None,
                    'str_synonym_cut': None,
                    # 'slots_cur': {},
                    'sentence_pattern_classification': None,
                    'session_id': None,
                    'jdpin_id': None,
                    'login_time': None,
                    'dst_word_to_fufill':{},
                    'label2entities_cur_dict':{},
                    }
        self._slotsmulti_instance=SlotsQAMulti()

    def __setitem__(self, key, value):
        if key in self.__dict__:
            self.__dict__[key] = value

    def __getitem__(self, item):
        return self.__dict__[item]
    def insert_slots(self,**kwargs):
        self._slotsmulti_instance.insert(time=time.time(),**kwargs)
    def update_slots(self,index=-1,**kwargs):
        self._slotsmulti_instance.update_by_index(index,**kwargs)
    def get_slots_by_field(self,field_in):
        #field_in:  product ,    company
        slots_dict=self._slotsmulti_instance.get_slots_by_key(field_in,key_in='question_and_answer')
        return slots_dict
    def get_slots_by_index(self,domain_classification_in,index=-1):
        #field_in:  product ,    company
        # field=fcname.alldomain.value
        domain_classification=domain_classification_in
        slots_dict=self._slotsmulti_instance.get_slots_by_index(field_in=domain_classification,key_in='question_and_answer',index_in=index)
        return slots_dict
    def get_instance_by_index(self,index=-1):
        instances=self._slotsmulti_instance.get_instances(fcname.alldomain.value)
        if instances:
            return instances[-1]
        else:
            return []
class UserManager(object, metaclass=Singleton):
    _preprocess_class = Preprocess()
    _users_containers = {}

    def __init__(self):
        pass
        # print('__init__')
    def create(self, jdpin_in, session_id_in):
        if not session_id_in in self._users_containers:
            user_class = User()
            user_class['jdpin_id'] = jdpin_in
            user_class['session_id'] = session_id_in
            self._users_containers[session_id_in] = user_class
        else:
            pass
        return self._users_containers[session_id_in]

    def update(self, session_id, **kwargs):
        user_cur = self._users_containers[session_id]
        for key, value in kwargs.items():
            if key in user_cur.__dict__:
                user_cur[key] = value
            if key == 'str_raw':
                str_synonym, str_synonym_cut = self._preprocess_class.process(value)
                str_raw_cut = jieba.lcut(value)
                user_cur['str_synonym'] = str_synonym
                user_cur['str_synonym_cut'] = str_synonym_cut
                user_cur['str_raw_cut'] = str_raw_cut
            if key == 'str_synonym':
                str_synonym_cut = jieba.lcut(value)
                user_cur['str_synonym'] = value
                user_cur['str_synonym_cut'] = str_synonym_cut
    def delete(self,session_id):
        if session_id in self._users_containers:
            self._users_containers.pop(session_id)
    def get_user(self, session_id_in):
        return self._users_containers[session_id_in]


usermanager = UserManager()

