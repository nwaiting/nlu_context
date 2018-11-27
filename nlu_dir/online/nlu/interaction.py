import collections
import copy
import itertools
import os

import jieba

from common.pathutil import PathUtil
from online.nlu.entity import Entity
from online.utils.funcs import write2txt, readfile_line2dict, dict2sorted_dict
from online.utils.nameutil import ContextNames as cname, FieldClassifyNames as dcname
from online.utils.funcs_business import _deal_interaction,_tmp_for_show_str
"""
    获取混淆简称：获取每个domain下所有词term，获取每个词term的简称情况，2--5个字，同domain下的简称进行混淆检索，用非同domain的进行检测
    保留下的即为混淆词，建立 {混淆词：【标准term】}
"""


class TrainAbbrev2StdEntity(object):
    """处理情况：单词完整，单词缩略， 带有缩略的句子"""
    _del_chars = ['保', '险', '附', '加', '合', '同', '公', '司', '疾', '病','两','全','意','外','重','疾','旅','行','健','医','疗']
    _entity_class = Entity()
    _filename_general = 'abbreviations2entity_{}.txt'
    _filepath_general = os.path.join(PathUtil().files_dirpath, _filename_general)
    _abbreviations_entity = [cname.domain.value]

    def __init__(self):
        self._preload()
        # self._load_words()
        pass

    def __load_entity_words(self):
        """load o2m_dict"""
        label2std2sim_dict = self._entity_class.get_domain2intent2std2sim_dict[dcname.product.value]
        return label2std2sim_dict

    def _preload(self):
        self._label2std2sim_dict = self.__load_entity_words()
        domain2abbrev2std_dict = self._get_intersection_abbreviations()
        self._write(domain2abbrev2std_dict)

    def create_abbreviations_map(self):
        self._preload()

    def _get_abbreviations_oneterm(self, elems_in):
        r_range = (2, 3, 4)
        results = list()
        for elem_iter in elems_in:
            for r_iter in r_range:
                combinations_iter = list(itertools.combinations(elem_iter, r=r_iter))
                results.extend(combinations_iter)
        return set(results)

    def _combinate_elems(self, nest_list_in):
        combinations_2 = list(itertools.combinations(nest_list_in, r=2))
        return combinations_2

    def _get_duplicate_abbreviations(self, list_one_in, list_two_in):
        intersected_items = set(list_one_in).intersection(set(list_two_in))
        return intersected_items

    def _get_different_abbreviations(self, list_one_in, list_two_in):
        difference_items = set(list_one_in).difference(set(list_two_in))
        return difference_items

    def _del_abbreviations(self, list_in):
        abbreviations_filtered = list()
        for elem_iter in list_in:
            flag_exist = False
            for char_iter in self._del_chars:
                if char_iter in elem_iter:
                    flag_exist = True
                    break
                else:
                    pass
            if not flag_exist:
                abbreviations_filtered.append(elem_iter)
        return abbreviations_filtered

    def _get_abbreviations(self, dict_in):
        results = collections.defaultdict(dict)
        for domain_iter, values in dict_in.items():
            for std_iter, sim_iter in values.items():
                combinations_iter = self._get_abbreviations_oneterm(sim_iter)
                results[domain_iter].update({std_iter: combinations_iter})
        return results

    def _abbreviations2complete(self, nest_dict_in):
        domain2abbrev2std_dict = collections.defaultdict(dict)
        for domain_iter, values_iter in nest_dict_in.items():
            allwords_domain = itertools.chain.from_iterable(list(values_iter.values()))
            for word_iter in allwords_domain:
                for std_iter, abbrevations_iter in values_iter.items():
                    if word_iter in abbrevations_iter:
                        if word_iter not in domain2abbrev2std_dict[domain_iter]:
                            domain2abbrev2std_dict[domain_iter][word_iter] = set()
                        else:
                            pass
                        domain2abbrev2std_dict[domain_iter][word_iter].add(std_iter)
        return domain2abbrev2std_dict

    def _get_intersection_abbreviations(self):
        label2std2abbreviations = collections.defaultdict(dict)
        domain2terms = self._get_abbreviations(self._label2std2sim_dict)
        counter = 0
        for domain_iter, std2terms in domain2terms.items():
            # combinations_2=self._combinate_elems(terms)
            domain2terms_copy = copy.deepcopy(domain2terms)
            domain2terms_copy.pop(domain_iter)
            for std_iter, term_iter in std2terms.items():
                std2terms_copy = copy.deepcopy(std2terms)
                std2terms_copy.pop(std_iter)
                terms_del_curitem = set(list(itertools.chain.from_iterable(list(std2terms_copy.values()))))
                duplicate_items = self._get_duplicate_abbreviations(term_iter, terms_del_curitem)
                duplicate_del_items = self._del_abbreviations(duplicate_items)
                # print(duplicate_items)
                duplicate_different_items = self._get_different_abbreviations(duplicate_del_items, domain2terms_copy)
                if duplicate_different_items:
                    label2std2abbreviations[domain_iter][std_iter] = duplicate_different_items
                counter += 1
                print(counter)
        # for k1,v1 in label2std2abbreviations.items():
        #     for k2,v2 in v1.items():
        #         print(k1,k2,v2)
        domain2abbrev2std_dict = self._abbreviations2complete(label2std2abbreviations)
        return domain2abbrev2std_dict

    def _write(self, domain2abbrev2std_dict_in):
        for domain_iter, abbrev2std_dict_iter in domain2abbrev2std_dict_in.items():
            filepath_cur = self._filepath_general.format(domain_iter)
            write2txt(abbrev2std_dict_iter, filepath_cur)

    def judge(self, str_preprocessed_in):
        pass

class InferAbbrev2StdEntity(object):
    _abbreviations_entity = [cname.domain.value]
    _filename_general = 'abbreviations2entity_{}.txt'
    _filepath_general = os.path.join(PathUtil().files_dirpath, _filename_general)
    _entity_class = Entity()

    def __init__(self):
        self._load_words()

    def _load_words(self):
        self._label2abbreviation2std_map = self._load_abbreviation2std_map()

    def _load_abbreviation2std_map(self):
        results = collections.defaultdict(dict)
        for label_iter in self._abbreviations_entity:
            filepath = self._filepath_general.format(label_iter)
            line_o2m_dict, line_o2o_dict_order = readfile_line2dict(filepath)
            for k, v in line_o2m_dict.items():
                # print('line_o2m_dict[k]==>',line_o2m_dict[k])
                line_o2m_dict[k].remove(k)
                line_o2m_dict_sorted = dict2sorted_dict(line_o2m_dict)
            results[label_iter] = line_o2m_dict_sorted
        return results

    def get_interaction_strs_map(self, str_in):
        abbrev2stds_list = list()
        abbrev_str = ''
        for label_iter in self._abbreviations_entity:
            for abbrev_iter, stds_iter in self._label2abbreviation2std_map[label_iter].items():
                if abbrev_iter in str_in:
                    abbrev_str = abbrev_iter
                    for std_iter in stds_iter:
                        str_replaced = str_in.replace(abbrev_iter, std_iter)
                        # abbrev2stds_list.append({std_iter: str_replaced})
                        #todo 后期再改回来，前端显示
                        abbrev2stds_list.append({_tmp_for_show_str.get(std_iter, std_iter): str_replaced})
                        # results.append(str_replaced)
                        # results_words.append(jieba.lcut(str_replaced))
                    return abbrev_str, abbrev2stds_list
        return abbrev_str, []

    def bool_abbrevation(self, str_in):
        abbrev_str, abbrev2stds_list = self.get_interaction_strs_map(str_in)
        if abbrev2stds_list:
            return True
        else:
            return False


if __name__ == '__main__':
    ia = TrainAbbrev2StdEntity()
    a1 = '安康无忧医疗保险'
    a2 = '安康无忧养老保险'
    r1 = list(itertools.combinations(list(a1), r=2))
    r2 = list(itertools.combinations(list(a2), r=2))
    r3 = set(r1).intersection(r2)
    print(r1)
    print(r2)
    print(r3)
