import copy

import jieba
from online.utils.configs import _environ
from online.nlu.domain_classification import DomainClassification
from online.nlu.fuzzy_interaction import FuzzyInterAction
from online.nlu.pattern_manage_dir.classification2action import Classification2Action
from online.nlu.pattern_manage_dir.sentence_classification_by_patterns import SentenceClassification
from online.nlu.preprocess import Preprocess
from online.nlu.pronoun_eliminate import PronounDeal
from online.nlu.user_manage import usermanager
from online.utils.funcs_business import _get_last_question, request_post_kg
from online.utils.logdiy import mylog
from online.utils.nameutil import PatternClassificationMapNames as classification_name, FieldClassifyNames as dcnames, \
    UserSlotsName as usname
from online.utils.nameutil import _flag_recomm_sent_pattern, _key_kg_sentence_classificiation, \
    _value_kg_sentence_classificiation_recommendation, PatternClassificationMapNames as pcname
from online.utils.redis_operation import getQAPairs, rds

"""
    处理当前question，处理 上一个answer。
    question ， answer 维持在不同槽位。 
    存储句式类型
    当前句，如果上一句是 推荐，抓上一句的slots。
"""


def _get_sentence_pattern_from_kg(sessionid_in, str_in):
    jdpin = usermanager.get_user(sessionid_in)['jdpin_id']
    status, result = request_post_kg(str_in, jdpin)
    sentence_pattern_classification_recommend = ''
    if status == 1:
        if _key_kg_sentence_classificiation in result:
            sentence_pattern_classification = result[_key_kg_sentence_classificiation]
            if sentence_pattern_classification == _value_kg_sentence_classificiation_recommendation:
                mylog.info('从图谱中获取句式\t{}'.format(sentence_pattern_classification))
                sentence_pattern_classification_recommend = pcname.query_product.value
        else:
            pass
    else:
        pass
    return sentence_pattern_classification_recommend

class NerDeal(object):
    _prounoun_class = PronounDeal()
    _sentenceclassification_class = SentenceClassification()
    _fuzzy_interaction_class = FuzzyInterAction()
    _preprocess_class = Preprocess()
    _usermanager_class = usermanager
    _domain_classification_class = DomainClassification()
    _classification2action_class = Classification2Action()

    def __init__(self):
        pass

    def _pattern_classification(self, sentence_in):
        return self._sentenceclassification_class.classification(sentence_in)

    def replace_words_list(self, words_list_in, src_prounoun_word, dst_word_to_fufill):
        words_list_out = copy.deepcopy(words_list_in)
        dst_word_out = copy.deepcopy(dst_word_to_fufill)
        if src_prounoun_word:
            for src_word in src_prounoun_word:
                index_pronoun = words_list_out.index(src_word)
                for label, words_iter in dst_word_out.items():
                    if words_iter:
                        entity_to_be_repl = words_iter.pop()
                        words_list_out[index_pronoun] = entity_to_be_repl
                        break
                    else:
                        pass
        for key, value in dst_word_out.items():
            words_list_out.extend(value)
        return words_list_out

    def _get_last_questionbak(self, jdpin_in):
        chatRecordList = getQAPairs(jdpin_in)
        if chatRecordList:
            last_question = chatRecordList[-1].question
            last_answer = chatRecordList[-1].answer
        else:
            last_question, last_answer = '', ''
        return last_question, last_answer

    def _get_entity_from_last_answer(self, str_in):
        return self._prounoun_class.get_entity_from_strs([str_in], dcnames.alldomain.value)

    def _deal_last_question(self, session_id_in):
        last_question, last_answer, last_sentence_pattern_classification = _get_last_question(session_id_in)
        classification = self._pattern_classification(last_question)
        if classification == classification_name.query_product.value:
            label2entities_cur_dict, words_timestap = self._get_entity_from_last_answer(last_answer)
            # self._slots_maintain_class.update_slots(label2entities_cur_dict, session_id_in)
            usermanager.get_user(session_id_in).update_slots(-1, **{usname.slots_answer.value: label2entities_cur_dict})
        else:
            pass

    def _classification_sentence_pattern(self, sessionid_in,str_in):
        user_cur=usermanager.get_user(sessionid_in)
        classification = self._pattern_classification(str_in)
        if classification == classification_name.bottom_no_inherit.value:
            str_synonym, _ = self._preprocess_class.process(str_in)
            classification = self._pattern_classification(str_synonym)

        if _environ=='online':
            sentence_pattern_classification_from_kg = _get_sentence_pattern_from_kg(sessionid_in, user_cur['str_raw'])
            if sentence_pattern_classification_from_kg:
                # user_cur['sentence_pattern_classification'] = sentence_pattern_classification_from_kg
                classification=sentence_pattern_classification_from_kg
            else:
                pass
        return classification

    def _get_prounoun_and_dst_words(self, sessionid_in):
        return self._classification2action_class.act(sessionid_in)

    def replace_with_context_only_question(self, sessionid_in):
        """
            根据历史对话，从历史对话提取实体，根据当前str中是否存在指代词，决定 实体是补充还是替换
            args:
                str_in: 输入字符串
                words_list_in：输入字符串分词结果
                jdpin_in： id
            return：
                words_list_out: 补全后的分词列表
                dst_word_out：   从历史对话记录提取的slots
                label2entities_cur_dict： 当前用户话提取的slots，准备存入列表的slots
        """
        user_cur = self._usermanager_class.get_user(sessionid_in)
        sentence_classification = self._classification_sentence_pattern(sessionid_in,user_cur['str_raw'])
        mylog.info('sentence_classification:\t\t{}\tstr_raw\t{}'.format(sentence_classification, user_cur['str_raw']))
        self._usermanager_class.update(sessionid_in, sentence_pattern_classification=sentence_classification)
        src_prounoun_word, dst_word_to_fufill = self._get_prounoun_and_dst_words(sessionid_in)
        label2entities_cur_dict, words_timestap = self._prounoun_class.get_entity_from_strs([user_cur['str_synonym']],
                                                                                            user_cur[
                                                                                                'domain_classification'])
        words_list_out = self.replace_words_list(user_cur['str_synonym_cut'], src_prounoun_word, dst_word_to_fufill)
        usermanager.update(sessionid_in,**{'dst_word_to_fufill':dst_word_to_fufill,'label2entities_cur_dict':label2entities_cur_dict})
        return words_list_out, dst_word_to_fufill, label2entities_cur_dict



    def replace_with_context(self, sessionid_in):
        self._deal_last_question(sessionid_in)
        # todo 添加分类
        user_cur = usermanager.get_user(sessionid_in)
        # todo 添加当前槽位切换
        domain_classification = self._domain_classification_class.classify(user_cur['str_synonym'])
        mylog.info('domain_classification:\t\t{}'.format(domain_classification))
        usermanager.update(sessionid_in, domain_classification=domain_classification)

        # usermanager.get_user(sessionid_in).update_slots(index=-1,sentence_pattern_classification=sentence_pattern_classification_from_kg)
        # self._usermanager_class.update(sessionid_in,{'str_raw':str_in,'str_synonym':str_synonym,
        #                                              'domain_classification':domain_classification,'str_synonym_cut':str_synonym_cut})
        words_list_out, dst_word_to_fufill, label2entities_cur_dict = self.replace_with_context_only_question(
            sessionid_in)
        # print('words_list_out, dst_word_to_fufill, label2entities_cur_dict==>',words_list_out, dst_word_to_fufill, label2entities_cur_dict)
        flag_inter, abbrev_str, abbrev2std_list = self._fuzzy_interaction_class.deal_fuzzy_interaction(sessionid_in,
                                                                                                       label2entities_cur_dict,
                                                                                                       user_cur[
                                                                                                           'str_raw'],
                                                                                                       words_list_out)
        usermanager.get_user(sessionid_in).insert_slots(
            **{'question': user_cur['str_synonym'], 'slots_question': label2entities_cur_dict,
               'domain_classification': user_cur['domain_classification'],
               'sentence_pattern_classification': user_cur['sentence_pattern_classification']})
        rds.set(user_cur['jdpin_id'] + _flag_recomm_sent_pattern, 0)
        return words_list_out, dst_word_to_fufill, label2entities_cur_dict, flag_inter, abbrev_str, abbrev2std_list


if __name__ == '__main__':
    s = '目的地填写错误怎么办'
    # s = '保险事故通知填写错误怎么办'
    # s = '通知填写错误怎么办'
    # s = '我想买安康无忧的责任范围'
    # s = '保单信息查询'
    # s = '合同的解除及风险'
    # s = '减额的交清有什么规则吗'
    # s = '合同的解除及风险'
    # s = '是否有补偿'
    # s = '安联安康无忧保险费率调整'
    # s = '安康无忧是否有补偿'
    # s = '我要去日本应该买什么产品'
    # s = '安康有什么产品'
    # s = '什么是职业分类表'
    # s = '安康的投保年龄'
    # s = '安行万里保障地区都是哪'
    # s='122112'
    s = '是否有补偿有什么要求'
    s = '我想查下保单'
    s = '122112'
    s = '上海分公司的电话是多少'
    s = '安联安康无忧医疗保险投保年龄是什么'
    s = '旅行险投保年龄意外险是什么两全险'
    # s='境外旅行能选择这款保险计划吗'
    # s='公司几点上班'
    s = '安行万里租的车保吗'
    s = '我要去境外旅行'
    s = '我想买个两全险'
    s = '安行万里境外险的保单信息'
    s='86岁能投保安行万里吗'

    words = jieba.lcut(s)
    jdpin = str(12345678)
    session = 'session' + jdpin
    pd = PronounDeal()
    ner = NerDeal()
    usermanager.create(jdpin, session)
    usermanager.update(session, str_raw=s)
    out = ner.replace_with_context(session)
    print(out)

"""
'domain_classification':None,
                 'str_raw':None,
                 'str_synonym':None,
                 'str_raw_cut':None,
                 'str_synonym_cut':None,
                'slots_history':{},
                'slots_cur':{},
                'sentence_pattern_classification':None,
                'session_id':None,
                'jdpin_id':None,
                'login_time':None,
"""
