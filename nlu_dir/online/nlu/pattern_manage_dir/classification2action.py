import collections

from online.nlu.pattern_manage_dir.dependance_parser import DependAnalysis
from online.nlu.preprocess import Preprocess
from online.nlu.pronoun_eliminate import PronounDeal
from online.nlu.recall_tfidf import SimilarModelSents
from online.nlu.user_manage import usermanager
from online.utils.logdiy import mylog
from online.utils.nameutil import PatternClassificationMapNames, ContextNames as cname, FieldClassifyNames as dcname

class ActionBase(object):
    _usermanager = usermanager

    def __init__(self):
        pass


class Action1(ActionBase):
    """继承上一句class"""
    name = PatternClassificationMapNames.inherit_from_last_sentence.value
    # _slots_maintain_class = SlotsMaintain()
    _pronoun_deal_class = PronounDeal()

    def __init__(self):
        super(Action1, self).__init__()

    def action(self, sessionid_in):
        str_in = self._usermanager.get_user(sessionid_in).__dict__['str_synonym']
        slots_instance=usermanager.get_user(sessionid_in).get_instance_by_index(-1)
        # chatRecordList = getQAPairs(sessionid_in + _key_only_question_jdpin_with, _answer_type)
        last_question = slots_instance['question']
        if last_question:
            label2entities_cur_dict, words_timestap = self._pronoun_deal_class.get_entity_from_strs([str_in],
                                                                                                    dcname.alldomain.value)
            label2entities_history_dict = self._pronoun_deal_class.get_label2entity_from_history(sessionid_in,
                                                                                                 dcname.alldomain.value)

            src_list = label2entities_history_dict.get(cname.domain.value)
            dst_list = label2entities_cur_dict.get(cname.domain.value)
            if src_list and dst_list:
                # cur_question_rewrite = last_question.replace(src_list[-1], dst_list[-1])
                self._usermanager.update(sessionid_in, str_synonym=last_question)
                return [src_list[-1]] if src_list else [], {
                    cname.domain.value: [dst_list[-1]] if dst_list else []}
            else:
                pass
        else:
            print('inherit_from_last_sentence 上文中沒有繼承到任何句子')
            last_question = ''
        return [],{}





class Action2(ActionBase):
    """只继承领域 class"""
    name = PatternClassificationMapNames.only_inherit_domain.value
    # _slots_maintain_class = SlotsMaintain()
    _prounoun_class = PronounDeal()
    _preprocess_class = Preprocess()

    def __init__(self):
        super(Action2, self).__init__()

    def action(self, sessionid_in):
        # 当前句子没有domain， 继承上文domain  当前句子有指代，继承domain， 当前句子有domain，不继承
        src_prounoun_word, dst_word_to_fufill, label2entities_cur_dict = self._prounoun_class.replace_words(
            sessionid_in)
        dst_dict = {cname.domain.value: dst_word_to_fufill[cname.domain.value]}
        return src_prounoun_word, dst_dict


class Action3(ActionBase):
    """通用正常继承class"""
    name = PatternClassificationMapNames.common_classification.value
    _prounoun_class = PronounDeal()
    # _slots_maintain_class = SlotsMaintain()
    _similarmodel_class = SimilarModelSents()
    _preprocess_class = Preprocess()
    _depend_analysis_class=DependAnalysis()
    def __init__(self):
        super(Action3, self).__init__()

    def action_accurate(self, str_in, words_list_in, jdpin_in):
        src_prounoun_word, dst_word_to_fufill, label2entities_cur_dict = self._prounoun_class.replace_words(str_in,
                                                                                                            words_list_in,
                                                                                                            jdpin_in)
        return src_prounoun_word, dst_word_to_fufill, str_in

    def action_with_fuzzy(self, sessionid_in):
        # 同义句替换，先分析当前句子实体词情况，再决定是否模糊匹配
        user_cur=self._usermanager.get_user(sessionid_in)
        src_prounoun_word, dst_word_to_fufill, label2entities_cur_dict = \
            self._prounoun_class.replace_words(sessionid_in)
        property_value = label2entities_cur_dict[cname.property.value]
        domain_list = label2entities_cur_dict[cname.domain.value]
        if not property_value:
            if domain_list:
                domain_str = domain_list[0]
                str_no_domain = user_cur['str_synonym'].replace(domain_str, '')
            else:
                domain_str = ''
                str_no_domain = user_cur['str_synonym']
            strs_set, scores_set = self._similarmodel_class.similar_threshold(str_no_domain)
            if strs_set:
                # print('recall similarity===>',words_set)
                mylog.info('similar_threshold   str_no_domain\t\t{}'.format(str(str_no_domain)))
                mylog.info('similar_threshold   words_set\t\t{}'.format(str(strs_set)))
                mylog.info('similar_threshold   scores_set\t\t{}'.format(str(scores_set)))

                str_similar = strs_set[0]
                # str_similar = ''.join(words_similar)
                str_similar_with_domain = domain_str + str_similar
                str_synonym, str_synonym_words = self._preprocess_class.process(str_similar_with_domain)
                self._usermanager.update(sessionid_in, str_synonym=str_synonym, str_synonym_cut=str_synonym_words)
                src_prounoun_word, dst_word_to_fufill, label2entities_cur_dict = self._prounoun_class.replace_words(
                    sessionid_in)

            else:
                # if '是多久' in str_no_domain:
                #     print('str_no_domain==>',str_no_domain)
                if self._depend_analysis_class.judge_complete(str_no_domain):
                    dst_word_to_fufill = {cname.domain.value: dst_word_to_fufill[cname.domain.value]}
                else:
                    pass
        else:
            pass

        return src_prounoun_word, dst_word_to_fufill

    def action(self, sessionid_in):
        # sentence_synonym, words_jieba = self._preprocess_class.process(str_in)

        return self.action_with_fuzzy(sessionid_in)
        # return self.action_accurate(str_in, words_list_in, jdpin_in)


class Action4(ActionBase):
    """不继承 class"""
    name = PatternClassificationMapNames.no_inherit.value

    def __init__(self):
        super(Action4, self).__init__()

    def action(self, sessionid_in):
        domain_history_list = []
        src_list = []
        return src_list, {cname.domain.value: [domain_history_list[-1]] if domain_history_list else []}


class Action5(object):
    name = PatternClassificationMapNames.query_product.value

    def __init__(self):
        pass

    def action(self, sessionid_in):
        domain_history_list = []
        src_list = []
        return src_list, {cname.domain.value: [domain_history_list[-1]] if domain_history_list else []}


class Action6(ActionBase):
    """不继承 class"""
    name = PatternClassificationMapNames.bottom_no_inherit.value

    def __init__(self):
        super(Action6, self).__init__()

    def action(self, sessionid_in):
        domain_history_list = []
        src_list = []
        return src_list, {cname.domain.value: [domain_history_list[-1]] if domain_history_list else []}


class Action7(ActionBase):
    """只继承领域 class"""
    name = PatternClassificationMapNames.only_inherit_property.value
    # _slots_maintain_class = SlotsMaintain()
    _prounoun_class = PronounDeal()
    _preprocess_class = Preprocess()

    def __init__(self):
        super(Action7, self).__init__()

    def action(self, sessionid_in):
        # 当前句子没有domain， 继承上文domain  当前句子有指代，继承domain， 当前句子有domain，不继承
        src_prounoun_word, dst_word_to_fufill, label2entities_cur_dict = self._prounoun_class.replace_words(
            sessionid_in)
        # dst_dict = {cname.property.value: dst_word_to_fufill[cname.property.value]}
        dst_dict = {cname.domain.value: dst_word_to_fufill[cname.domain.value]}
        return src_prounoun_word, dst_dict

class Action8(ActionBase):
    """只继承领域 class"""
    name = PatternClassificationMapNames.domain_defination.value
    # _slots_maintain_class = SlotsMaintain()
    _prounoun_class = PronounDeal()
    _preprocess_class = Preprocess()

    def __init__(self):
        super(Action8, self).__init__()

    def action(self, sessionid_in):
        # 当前句子没有domain， 继承上文domain  当前句子有指代，继承domain， 当前句子有domain，不继承
        src_prounoun_word, dst_word_to_fufill, label2entities_cur_dict = self._prounoun_class.replace_words(
            sessionid_in)
        # dst_dict = {cname.property.value: dst_word_to_fufill[cname.property.value]}
        dst_dict = {cname.domain.value: dst_word_to_fufill[cname.domain.value]}
        return src_prounoun_word, dst_dict

class Action9(object):
    name=PatternClassificationMapNames.pure_domain_name.value
    _indexes=[-1,-2,-3,-4,-5]
    def __init__(self):
        pass
    def action(self,sessionid_in):
        str_in = usermanager.get_user(sessionid_in).__dict__['str_synonym']
        domain_classification = usermanager.get_user(sessionid_in).__dict__['domain_classification']
        slots_dict=collections.defaultdict(list)
        for index_iter in self._indexes:
            slots_instance = usermanager.get_user(sessionid_in).get_slots_by_index(domain_classification,index_iter)
            for k,v in slots_instance.items():
                if v:
                    slots_dict[k].append(v)
        if cname.domain.value in slots_dict:
            slots_dict.pop(cname.domain.value)
        slots_dict_only_one=collections.defaultdict(list)
        for k,v in slots_dict.items():
            if v:
                slots_dict_only_one[k]=v[0]
            else:
                slots_dict_only_one[k]=[]
        return [],slots_dict_only_one

Actions = [Action1, Action2, Action3, Action4, Action5, Action6, Action7,Action8,Action9]
Name2actions_dict = {action_iter.name: action_iter() for action_iter in Actions}


class Classification2Action(object):
    """根据不同类别，调用不同child class 的action 函数"""
    _usermanager = usermanager

    def __init__(self):
        pass

    def act(self, sessionid_in):
        # print(classification_in)
        sentence_pattern_classification = self._usermanager.get_user(sessionid_in)['sentence_pattern_classification']
        assert sentence_pattern_classification in Name2actions_dict
        class_cur = Name2actions_dict[sentence_pattern_classification]
        return class_cur.action(sessionid_in)
