import collections
import copy

from common.pathutil import PathUtil
from online.nlu.entity import Entity
from online.nlu.user_manage import usermanager
# from online.nlu.slots_maintain import SlotsMaintain
from online.utils.funcs import list2re, readfile_line2list
from online.utils.logdiy import logging
from online.utils.nameutil import ContextMap as cmap
from online.utils.nameutil import ContextNames as cname

logger = logging.getLogger(__file__)
"""
保险  合同  保障  保险费 保险金 其他  释义  投保规则    服务规则
"""


class PronounBase(object):
    _path_class = PathUtil()
    entity_class = Entity()

    def __init__(self):
        self._preload()

    def _preload(self):
        pronouns = self._get_pronouns()
        compare_pronouns = self._get_compare_pronouns()
        self._re_prounouns = list2re(pronouns)
        self._re_compare_pronouns = list2re(compare_pronouns)

    def _get_pronouns(self):
        prouns = readfile_line2list(self._path_class.prounoun_filepath)
        return prouns

    def _get_compare_pronouns(self):
        pronouns = readfile_line2list(self._path_class.compare_pronoun_filepath)
        return pronouns

    def bool_pronouns_exist(self, str_in):
        prounous = self._re_prounouns.findall(str_in)
        return bool(prounous), prounous

    def bool_compare_pronoun_exist(self, str_in):
        prounoun = self._re_compare_pronouns.findall(str_in)
        return bool(prounoun), prounoun

    def get_pronoun_word(self, word_list_in):
        """获取含有指代词的具体词"""
        word_proun = [word_iter for word_iter in word_list_in if self._re_prounouns.search(word_iter)]
        word_proun_filter_entity = [word_iter for word_iter in word_proun if
                                    not self.entity_class.re_entity_list.search(word_iter)]
        return word_proun_filter_entity


class PronounDeal(object):
    # _slots_class = SlotsMaintain()
    _pb_class = PronounBase()
    _entity_class = Entity()
    _usermanager = usermanager

    def __init__(self):
        self._label2num_dict = self._make_slots_dict()

    def _make_slots_dict(self):
        return cmap().__dict__

    def _bool_two_domain(self, str_cur_in):
        is_pronouns, prounous = self._pb_class.bool_compare_pronoun_exist(str_cur_in)
        return is_pronouns

    def _bool_pronouns(self, str_cur_in):
        is_pronoun, _ = self._pb_class.bool_pronouns_exist(str_cur_in)
        if is_pronoun:
            return True
        else:
            is_compare_pronoun, _ = self._pb_class.bool_compare_pronoun_exist(str_cur_in)
            return is_pronoun

    def _get_domain_from_history(self, domain_list_cur_in, label2entities_history_dict):
        val_domain_ret = copy.deepcopy(domain_list_cur_in)
        if not cname.domain.value in label2entities_history_dict:
            pass
        else:
            for val_iter in label2entities_history_dict[cname.domain.value][::-1]:
                if val_iter not in domain_list_cur_in:
                    if len(val_domain_ret) < 2:
                        val_domain_ret.append(val_iter)
                    else:
                        break
        val_domain_ret_remove_cur = set(val_domain_ret).difference(set(domain_list_cur_in))
        return val_domain_ret_remove_cur

    def _get_pronoun_word(self, word_list_in):
        """获取代词"""
        pronouns_cur = self._pb_class.get_pronoun_word(word_list_in)
        return pronouns_cur

    def get_label2entity_from_history(self, sessionid_in, domain_classification_in):
        """从历史数据中获取 label 对应的  实体词"""
        return usermanager.get_user(sessionid_in).get_slots_by_field(domain_classification_in)

    def _judge_pronoun(self, str_cur_in):
        """判断是否存在指代"""
        label2num_dict = copy.deepcopy(self._label2num_dict)
        is_pronoun = False
        if self._bool_two_domain(str_cur_in):
            label2num_dict[cname.domain.value] = 2
            label2num_dict[cname.property.value] = 0
            is_pronoun = True
        elif self._bool_pronouns(str_cur_in):
            is_pronoun = True
        else:
            pass
        return is_pronoun, label2num_dict

    def get_entity_from_strs(self, str_list_in, domain_classification):
        """从string中获取实体词"""
        label2entities_cur_dict, words_timestap = self._entity_class.find_entity(str_list_in, domain_classification)
        return label2entities_cur_dict, words_timestap

    def _get_some_entities(self, label2num_dict, label2entities_history_dict_in, label2entities_cur_dict_in):
        """根据是否需要两个实体词，结合当前句子中存在的实体词数量，进行补充"""
        # self._label2entities_history_dict = self._get_label2entity_from_history(jdpin_in)
        label2entities_history_dict_tmp = copy.deepcopy(label2entities_history_dict_in)
        label2entities_cur_dict_tmp = collections.defaultdict(list)
        label2entities_history_duplicate = collections.OrderedDict()
        # print('label2entities_history_dict_tmp==>\n', label2entities_history_dict_tmp)
        for label, vals in label2entities_history_dict_tmp.items():
            vals_del = [val_iter for val_iter in vals if val_iter not in label2entities_cur_dict_in.get(label, [])]
            label2entities_history_duplicate[label] = vals_del
        for label_iter, number_iter in label2num_dict.items():
            end_num = -1 * (number_iter - len(label2entities_cur_dict_in[label_iter]))
            if end_num < 0 and label2entities_history_duplicate[label_iter]:
                label2entities_cur_dict_tmp[label_iter] = label2entities_history_duplicate[label_iter][end_num:]
            else:
                label2entities_cur_dict_tmp[label_iter] = []

        label2entities_cur_dict_ret = collections.OrderedDict()
        label2entities_cur_dict_ret[cname.domain.value] = label2entities_cur_dict_tmp[cname.domain.value]
        label2entities_cur_dict_tmp.pop(cname.domain.value)
        for label_iter, entities_iter in label2entities_cur_dict_tmp.items():
            label2entities_cur_dict_ret[label_iter] = entities_iter

        for key, values in label2entities_cur_dict_ret.items():
            while len(values) != len(list(set(values))):
                for index, value_iter in enumerate(values):
                    if values.count(value_iter) > 1:
                        values.pop(values.index(value_iter))

        return label2entities_cur_dict_ret

    def get_pronouns(self, word_list_in):
        return self._get_pronoun_word(word_list_in)

    def replace_words(self, sessionid_in):
        """
           指代消解，判断有无指代，
           存在指代，则判断此句有几个成分，指代替换成没有的成分，优先级domain
           没有指代跳出函数
        """
        str_synonym = self._usermanager.get_user(sessionid_in).__dict__['str_synonym']
        str_synonym_cut = self._usermanager.get_user(sessionid_in).__dict__['str_synonym_cut']
        domain_classification = self._usermanager.get_user(sessionid_in).__dict__['domain_classification']
        is_pronoun, label2num_dict = self._judge_pronoun(str_synonym)
        label2entities_history_dict = self.get_label2entity_from_history(sessionid_in, domain_classification)
        label2entities_cur_dict, words_timestap = self.get_entity_from_strs([str_synonym], domain_classification)
        # print('label2entities_history_dict==>\n',label2entities_history_dict)
        label2entities_cur_dict_ret = self._get_some_entities(label2num_dict, label2entities_history_dict,
                                                              label2entities_cur_dict)
        src_prounoun_word = self._get_pronoun_word(str_synonym_cut)
        logger.info('当前class\t{}\t\t 当前函数{}\n ,输入str_cur_in\t{},输入word_list_in\t{}\t,输入jdpin\t{}\t'.
                    format(str(self.__class__), 'replace_words', str(str_synonym), str(str_synonym_cut), sessionid_in))
        output_str = 'src_prounoun_word\t{}\t, label2entities_cur_dict_ret\t{}\t, label2entities_cur_dict\t{}\t'. \
            format(str(src_prounoun_word), str(label2entities_cur_dict_ret), str(label2entities_cur_dict))
        logging.info(output_str)
        return src_prounoun_word, label2entities_cur_dict_ret, label2entities_cur_dict


if __name__ == '__main__':
    import jieba

    # from online.utils.funcs import jieba_add_words
    # words_add=jieba_add_words()
    # for word_iter in words_add:
    #     jieba.add_word(word_iter)
    s = '目的地填写错误怎么办'
    s = '那个填写错误怎么办'
    words = jieba.lcut(s)
    jdpin = 12345
    pd = PronounDeal()

    result = pd.replace_words(s, words, jdpin)
    print(result)
