import collections

from common.pathutil import PathUtil
from online.utils.configs import domain2entity2paths_set
from online.utils.funcs import list2re, dict2sorted_dict, list2sorted_list, read_data_from_paths_set
from online.utils.nameutil import FieldClassifyNames as dcname

"""
传入str列表，从中发现 ner词，输出

维护 slots槽位，每一句话都进行提取存储。
上下文进行处理，则利用这个槽位。
"""


class Entity(object):
    #   实现根据领域加载词典，加载正则，词典合并。
    #
    _pathutil_class = PathUtil()
    _domain2entity2paths_set = domain2entity2paths_set

    def __init__(self):
        self._preload()

    def _preload(self):
        self._domain2intent2words_dict, self._domain2word2intent_dict, self._domain2entity_o2o_dict, self._domain2entity_o2m_dict, self._domain2intent2std2sim_dict, self._intent2sim2std_o2o_dict = \
            self._get_entities(self._domain2entity2paths_set)
        # self._domain2intent2words_dict[dcname.alldomain.value]=self.get_intent2entities

    @property
    def re_entity_list(self):
        keys = list()
        for domain_iter, value_iter in self._domain2entity_o2o_dict.items():
            keys.extend(value_iter)
        keys_sorted = sorted(keys, key=lambda x: len(x), reverse=True)
        return list2re(keys_sorted)

    @property
    def entity_o2o_dict(self):
        vs = {}
        for k, v in self._domain2entity_o2o_dict.items():
            vs.update(v)
        vs_sorted = dict2sorted_dict(vs)
        return vs_sorted

    @property
    def entity_o2m_order_dict(self):
        vs = {}
        for k, v in self._domain2entity_o2m_dict.items():
            vs.update(v)
        vs_sorted = dict2sorted_dict(vs)
        return vs_sorted

    @property
    def get_intent2entities(self):
        # entity_o2o_dict, entity_label2words_dict, entity_word2label_dict_sorted,entity_o2m_order_dict,label2std2sim_dict=self._get_entities()
        # return entity_label2words_dict
        intent2entities_dict = collections.defaultdict(list)
        for domain_iter, items in self._domain2intent2words_dict.items():
            for intent_iter, v2 in items.items():
                intent2entities_dict[intent_iter].extend(v2)
        intent2entities_dict_sorted = dict2sorted_dict(intent2entities_dict)
        for k, v in intent2entities_dict_sorted.items():
            intent2entities_dict_sorted[k] = list2sorted_list(v)
        return intent2entities_dict_sorted

    @property
    def get_intent2sim2std_o2o_dict(self):
        return self._intent2sim2std_o2o_dict
    @property
    def get_domain2intent2std2sim_dict(self):
        return self._domain2intent2std2sim_dict
    @property
    def get_domain2pattern_dict(self):
        domain2pattern_dict = dict()
        for domain_iter, words_iter in self._domain2entity_o2o_dict.items():
            pattern_iter = list2re(words_iter)
            domain2pattern_dict[domain_iter] = pattern_iter
        return domain2pattern_dict

    @property
    def get_domain2intent2words_dict(self):
        return self._domain2intent2words_dict
    @property
    def get_domain2entity_o2m_dict(self):
        return self._domain2entity_o2m_dict
    def _get_entities(self, domain2entity2paths_set_in):
        domain2intent2words_dict, domain2word2intent_dict, domain2entity_o2o_dict, domain2entity_o2m_dict, domain2intent2std2sim_dict = {}, {}, {}, {}, {},
        intent2sim2std_o2o_dict = collections.defaultdict(dict)
        assert isinstance(domain2entity2paths_set_in, dict)
        for domain_iter, entity2paths_set_iter in domain2entity2paths_set_in.items():
            classification2words_dict, word2classification_dict, entity_o2o_dict, entity_o2m_dict, classification2std2sim_dict, classification2sim2std_o2o_dict = \
                read_data_from_paths_set(entity2paths_set_iter)

            word2classification_dict_sorted = dict2sorted_dict(word2classification_dict)
            entity_o2m_dict_sorted = dict2sorted_dict(entity_o2m_dict)
            entity_o2o_dict_sorted = dict2sorted_dict(entity_o2o_dict)

            domain2intent2words_dict[domain_iter] = classification2words_dict
            domain2word2intent_dict[domain_iter] = word2classification_dict_sorted

            domain2entity_o2o_dict[domain_iter] = entity_o2o_dict_sorted
            domain2entity_o2m_dict[domain_iter] = entity_o2m_dict_sorted
            domain2intent2std2sim_dict[domain_iter] = classification2std2sim_dict

            for intent_iter, sim2std_dict_iter in classification2sim2std_o2o_dict.items():
                intent2sim2std_o2o_dict[intent_iter].update(sim2std_dict_iter)

        alldomain_intent2words_dict = collections.defaultdict(list)
        for domain_iter, dict_iter in domain2intent2words_dict.items():
            for intent_iter, words_iter in dict_iter.items():
                alldomain_intent2words_dict[intent_iter].extend(words_iter)
        domain2intent2words_dict[dcname.alldomain.value] = alldomain_intent2words_dict

        alldomain_word2intent_dict = collections.defaultdict(list)
        for domain_iter, dict_iter in domain2word2intent_dict.items():
            for word_iter, intent_iter in dict_iter.items():
                alldomain_word2intent_dict[word_iter] = intent_iter
        domain2word2intent_dict[dcname.alldomain.value] = alldomain_word2intent_dict
        return domain2intent2words_dict, domain2word2intent_dict, domain2entity_o2o_dict, domain2entity_o2m_dict, domain2intent2std2sim_dict, intent2sim2std_o2o_dict

    def find_entity(self, str_list_in, domain_classification):
        """依靠 domain2entity2patterns 正则，每次处理一类"""
        label_entities_dict = collections.defaultdict(list)
        words_timestap = list()
        for str_iter in str_list_in:
            str_tmp = str_iter
            for word_similiar_iter, intent_iter in self._domain2word2intent_dict[domain_classification].items():
                # words_ret = re_words_iter.findall(str_tmp)
                if word_similiar_iter in str_tmp:
                    label_entities_dict[intent_iter].append(word_similiar_iter)
                    # str_tmp = str_tmp.replace(word_similiar_iter, '')
                    str_tmp = str_tmp.replace(word_similiar_iter[:-2], '')
                    words_timestap.append(word_similiar_iter)
                else:
                    pass
        return label_entities_dict, words_timestap
