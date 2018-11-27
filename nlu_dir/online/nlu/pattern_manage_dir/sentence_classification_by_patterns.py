import collections
import re

from common.pathutil import PathUtil
from online.nlu.entity import Entity
from online.utils.funcs import read_yaml_dict_onelayer, readfile_line2dict,read_data_from_paths_set
from online.utils.nameutil import PatternClassificationMapNames
from online.nlu.preprocess import SimiliarReplace
from online.nlu.recall_tfidf import SimilarModelSents
_answer_type = 1


class EntitySet(object):
    _entity_class = Entity()
    _words_map_filepaths={'pronoun':[PathUtil().prounoun_filepath]}
    def __init__(self):
        pass

    def get_all_represent_words(self):
        label2entities_part1 = self._entity_class.get_intent2entities
        label2entities_part2 = self.__read_represent_words()
        label2entities_part3=self.__read_words_map_filepaths()
        label2entities = {**label2entities_part1, **label2entities_part2,**label2entities_part3}
        return label2entities
    def __read_words_map_filepaths(self):
        """获取代词映射"""
        #classification2words_dict,word2classification_dict,entity_o2o_dict,entity_o2m_dict,classification2std2sim_dict,classification2sim2std_o2o_dict
        entity_label2words_dict, entity_word2label_dict, entity_o2o_dict,_,_,_=read_data_from_paths_set(self._words_map_filepaths)
        return entity_label2words_dict
    def __read_represent_words(self):
        """获取字母表示的一类词的映射"""
        filepath = PathUtil().get_represent_words_map
        line_o2m_dict, line_o2o_dict = readfile_line2dict(filepath)
        # print(line_o2m_dict)
        return line_o2m_dict


def _trans_label2words_format():
    entity_set_class = EntitySet()
    label2words = entity_set_class.get_all_represent_words()
    label2words_format = collections.defaultdict(list)
    for label, words in label2words.items():
        label_format = '<' + label + '>'
        # print('words==>',words)
        words_str = '(' + '|'.join(words) + ')'
        label2words_format[label_format] = words_str
    return label2words_format


def fill_words2patterns():
    """将 words 填充 到 句式 pattern 中"""
    label2words_str = _trans_label2words_format()
    ymlpath = PathUtil().get_pattern_with_represent_yamlpath
    key2patterns_str_dict = read_yaml_dict_onelayer(ymlpath)
    key2patterns_dict = collections.defaultdict(list)
    for key, patterns_str in key2patterns_str_dict.items():
        for pattern_str in patterns_str:
            pattern_str_cur = pattern_str
            for label, words_str_iter in label2words_str.items():
                if label in pattern_str_cur:
                    pattern_str_cur = pattern_str_cur.replace(label, words_str_iter)
            pattern_cur = re.compile(pattern_str_cur)
            key2patterns_dict[key].append(pattern_cur)
    return key2patterns_dict

class SentenceClassification(object):
    _entity_set_class = EntitySet()
    _similiar_class=SimiliarReplace()
    _similar_threshold_class=SimilarModelSents()
    _words_add=['理赔','选择','款','计划','保','感冒发烧','什么时候','保险','时间','买','合同','岁','年龄']
    _re_words_dd=re.compile('('+'|'.join(_words_add)+')')
    def __init__(self):
        self._preload()

    def _preload(self):
        """读取句式模板， 读取 repres_words, 进行正则拼接"""
        key2patterns_dict = fill_words2patterns()
        self._classification2patterns = key2patterns_dict

    def _get_patterns(self):
        ymlpath = PathUtil().get_pattern_with_represent_yamlpath
        key2patterns_dict = read_yaml_dict_onelayer(ymlpath)

    def _get_represent_words(self):
        pass
    def _bool_entity_words_exists(self,sentence_in):
        bool_exist,counter_exist=self._similiar_class.bool_entity_words_exists_and_number(sentence_in)
        return bool_exist

    def classification(self, sentence_in):
        #todo
        return self.classification_fuzzy(sentence_in)
    def classification_fuzzy(self, sentence_in):
        """根据模板分类，对sentence 进行分类"""
        #todo
        # print('sentence_in===>',sentence_in)
        for classification_iter, patters_iter in self._classification2patterns.items():
            for pattern_iter in patters_iter:
                if pattern_iter.search(sentence_in):
                    return classification_iter
        if self._bool_entity_words_exists(sentence_in):
            return PatternClassificationMapNames.common_classification.value
        elif self._re_words_dd.search(sentence_in):
            return PatternClassificationMapNames.common_classification.value
        else:
            #todo 添加 tfidf 同义挖掘
            # print('_bool_entity_words_exists False sentence_in==>',sentence_in)
            # return PatternClassificationMapNames.common_classification.value
            words_set, scores_set=self._similar_threshold_class.similar_threshold(sentence_in)
            if words_set:
                str_cur=''.join(words_set[0])
                if self._bool_entity_words_exists(str_cur):
                    return PatternClassificationMapNames.common_classification.value
            return PatternClassificationMapNames.bottom_no_inherit.value
    def classification_accurate(self, sentence_in):
        """根据模板分类，对sentence 进行分类"""
        #todo
        for classification_iter, patters_iter in self._classification2patterns.items():
            for pattern_iter in patters_iter:
                if pattern_iter.search(sentence_in):
                    return classification_iter
        if self._bool_entity_words_exists(sentence_in):
            return PatternClassificationMapNames.common_classification.value
        elif self._re_words_dd.search(sentence_in):
            return PatternClassificationMapNames.common_classification.value
        else:
            #todo 添加 tfidf 同义挖掘
            return PatternClassificationMapNames.bottom_no_inherit.value
