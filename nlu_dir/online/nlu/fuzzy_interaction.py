import abc

from online.nlu.entity import Entity
from online.nlu.interaction import InferAbbrev2StdEntity
from online.nlu.pattern_manage_dir.sentence_classification_by_patterns import SentenceClassification
from online.nlu.user_manage import usermanager
from online.utils.funcs_business import _get_last_question,_tmp_for_show_str
from online.utils.logdiy import mylog
from online.utils.nameutil import ContextNames as cname, FieldClassifyNames as dcname, \
    PatternClassificationMapNames as pcname, _default_name_abbrev, _flag_recomm_sent_pattern
from online.utils.funcs_business import _deal_interaction
from online.nlu.preprocess import Preprocess
from online.utils.nameutil import FieldClassifyNames as fcname
"""
    处理当前question，处理 上一个answer。
    question ， answer 维持在不同槽位。 
    存储句式类型
    当前句，如果上一句是 推荐，抓上一句的slots。
"""

_preprocess_class=Preprocess()
def _get_last_question_info(sessionid_in, flag_preprocess='question'):#'none' 表示不复写
    last_question, last_answer, last_sentence_pattern_classification = _get_last_question(sessionid_in)
    if flag_preprocess == 'question':
        last_question, _ = _preprocess_class.process(last_question)
    elif flag_preprocess == 'answer':
        last_answer, _ = _preprocess_class.process(last_answer)
    else:
        pass
    return last_question, last_answer, last_sentence_pattern_classification



class InteractionBase(object):
    _entity_class = Entity()
    _preprocess_class=Preprocess()
    def __init__(self):
        pass

    @abc.abstractmethod
    def judge_interaction(self, sessionid_in, label2entities_cur_dict_in, str_in):
        pass

    @abc.abstractmethod
    def deal_interaction(self, sessionid_in, label2entities_cur_dict_in, str_in):
        pass


class CurStrAbbrevInteraction(InteractionBase):
    _infer_abbrev2std_class = InferAbbrev2StdEntity()

    # 当前句有省略词 产品词
    def __init__(self):
        super(CurStrAbbrevInteraction, self).__init__()

    def judge_interaction(self, sessionid_in, label2entities_cur_dict_in, str_in):
        if not label2entities_cur_dict_in['domain'] and self._infer_abbrev2std_class.bool_abbrevation(str_in):
            mylog.info('CurStrAbbrevInteraction return True')
            return True
        else:
            return False

    def _make_o2m_for_interaction(self, str_in):
        abbrev_str, abbrev2stds_list = self._infer_abbrev2std_class.get_interaction_strs_map(str_in)
        return abbrev_str, abbrev2stds_list

    def deal_interaction(self, sessionid_in, label2entities_cur_dict_in, str_in):
        abbrev_str, abbrev2stds_list = self._make_o2m_for_interaction(str_in)
        return 1 if abbrev_str else 0, abbrev_str, abbrev2stds_list

class RecomLastQuestionMultiProductInteraction(InteractionBase):
    # 上一句是推荐，当前句缺product entity
    _sentence_classification_class=SentenceClassification()
    # _excluted_classification=[pcname.query_product.value]
    _included_classification=[pcname.common_classification.value,pcname.only_inherit_domain,]
    def __init__(self):
        super(RecomLastQuestionMultiProductInteraction, self).__init__()

    def judge_interaction(self, sessionid_in, label2entities_cur_dict_in, str_in):
        #todo 添加 领域判断
        jdpin_id=usermanager.get_user(sessionid_in)['jdpin_id']
        sentence_classification=usermanager.get_user(sessionid_in)['sentence_pattern_classification']
        key_name=jdpin_id+_flag_recomm_sent_pattern
        # print('key_name==>',key_name)
        # last_question, last_answer,last_sentence_pattern_classification = _get_last_question(sessionid_in)
        last_question, last_answer, last_sentence_pattern_classification=_get_last_question_info(sessionid_in,'none')
        # sc_cur=self._sentence_classification_class.classification_accurate(last_question)
        # print('rds.get(key_name)',)
        # print(rds.keys())
        # val_raw=rds.get(key_name)
        # if val_raw:
        #     print(eval(val_raw))
        #     val_flag=bytes(val_raw,encoding='utf-8')
            # if eval(val_raw) not in [0,'0']:
            #     print('val_flag==>',val_raw)
        if last_sentence_pattern_classification==pcname.query_product.value and sentence_classification in self._included_classification :
            mylog.info('RecomLastQuestionMultiProductInteraction return True')
            return True
        else:
            pass
            #todo 后续再打开
            # val_raw=rds.get(key_name)
            # if val_raw:
            #     flag_raw=eval(val_raw)
            #     if flag_raw and flag_raw==1 :
            #         print('测试检测到 redis 中上一句 是  推荐句式')
            #         mylog.info('测试检测到 redis 中上一句 是  推荐句式\t keyname={}'.format(str(key_name)))
            #         return True
        return False
    def deal_interaction(self, sessionid_in, label2entities_cur_dict_in, str_in):
        user_cur = usermanager.get_user(sessionid_in)
        # last_answer_rewrite, last_answer,last_sentence_pattern_classification = _get_last_question(sessionid_in)
        last_question, last_answer, last_sentence_pattern_classification=_get_last_question_info(sessionid_in,flag_preprocess='question')

        # last_question, last_answer, last_sentence_pattern_classification= _get_last_question(sessionid_in)
        jdpin_id = user_cur['jdpin_id']
        # last_answer_rewrite,_=self._preprocess_class.process(last_answer)
        mylog.info('jdpin\t{}\t,\n last_answer{}\t'.format(str(jdpin_id),str(last_question),str(last_answer)))
        abbrev2std_list=_deal_interaction(sessionid_in,[last_answer],str_in)
        mylog.info('deal_interaction:   last_answer_rewrite\t{}\n{}'.format(str(last_answer),str(abbrev2std_list)))
        if abbrev2std_list:
            return 1, _default_name_abbrev, abbrev2std_list
        else:
            return 0, '', []

class RecomLastAnswerMultiProductInteractionBak(InteractionBase):
    # 上一句是推荐，当前句缺product entity
    _sentence_classification_class=SentenceClassification()
    # _excluted_classification=[pcname.query_product.value]
    _included_classification=[pcname.common_classification.value,pcname.only_inherit_domain,]
    def __init__(self):
        super(RecomLastAnswerMultiProductInteraction, self).__init__()

    def judge_interaction(self, sessionid_in, label2entities_cur_dict_in, str_in):
        jdpin_id=usermanager.get_user(sessionid_in)['jdpin_id']
        sentence_classification=usermanager.get_user(sessionid_in)['sentence_pattern_classification']
        key_name=jdpin_id+_flag_recomm_sent_pattern
        # print('key_name==>',key_name)
        last_question, last_answer,last_sentence_pattern_classification = _get_last_question(sessionid_in)
        sc_cur=self._sentence_classification_class.classification_accurate(last_question)
        # print('rds.get(key_name)',)
        # print(rds.keys())
        # val_raw=rds.get(key_name)
        # if val_raw:
        #     print(eval(val_raw))
        #     val_flag=bytes(val_raw,encoding='utf-8')
            # if eval(val_raw) not in [0,'0']:
            #     print('val_flag==>',val_raw)
        if sc_cur==pcname.query_product.value and sentence_classification in self._included_classification :
            mylog.info('RecomLastAnswerMultiProductInteraction return True')
            return True
        else:
            pass
            #todo 后续再打开
            # val_raw=rds.get(key_name)
            # if val_raw:
            #     flag_raw=eval(val_raw)
            #     if flag_raw and flag_raw==1 :
            #         print('测试检测到 redis 中上一句 是  推荐句式')
            #         mylog.info('测试检测到 redis 中上一句 是  推荐句式\t keyname={}'.format(str(key_name)))
            #         return True
        return False
    def deal_interaction(self, sessionid_in, label2entities_cur_dict_in, str_in):
        user_cur = usermanager.get_user(sessionid_in)
        last_question, last_answer, last_sentence_pattern_classification= _get_last_question(sessionid_in)
        jdpin_id = user_cur['jdpin_id']
        last_answer_rewrite,_=self._preprocess_class.process(last_answer)
        mylog.info('jdpin\t{}\t获取到的last_question\t{},\n last_answer{}\t'.format(str(jdpin_id),str(last_question),str(last_answer_rewrite)))
        abbrev2std_list=_deal_interaction(sessionid_in,[last_answer_rewrite],str_in)
        if abbrev2std_list:
            mylog.info('deal_interaction:\t{}'.format(str(last_answer_rewrite)))
            return 1, _default_name_abbrev, abbrev2std_list
        else:
            return 0, '', []
class LastQuestionMultiProductInteracton(InteractionBase):
    # 上一句有多个product，当前句没用product
    _sentence_classifications_needed = [pcname.common_classification.value, pcname.only_inherit_domain.value, ]

    def __init__(self):
        super(LastQuestionMultiProductInteracton, self).__init__()

    def _get_entity_from_strs(self, str_list_in, domain_classification):
        """从string中获取实体词"""
        label2entities_cur_dict, words_timestap = self._entity_class.find_entity(str_list_in, domain_classification)
        return label2entities_cur_dict, words_timestap
    def judge_interaction(self, sessionid_in, label2entities_cur_dict_in, str_in):
        #todo 添加 领域判断
        user_cur = usermanager.get_user(sessionid_in)
        # last_question, last_answer,last_sentence_pattern_classification = _get_last_question(sessionid_in)

        last_question, last_answer, last_sentence_pattern_classification=_get_last_question_info(sessionid_in,flag_preprocess='question')

        last_label2entities_cur_dict, last_words_timestap = self._get_entity_from_strs([last_question],user_cur['domain_classification'])
        mylog.info('last_question\t{}'.format(str(last_question)))
        mylog.info('last_label2entities_cur_dict[cname.domain.value\t{}'.format(str(last_label2entities_cur_dict[cname.domain.value])))
        mylog.info('label2entities_cur_dict_in[cname.domain.value\t{}'.format(str(label2entities_cur_dict_in[cname.domain.value])))
        mylog.info('sentence_pattern_classification\t{}'.format(str(user_cur['sentence_pattern_classification'])))
        if len(last_label2entities_cur_dict[cname.domain.value]) > 1 and not label2entities_cur_dict_in['domain'] and \
                user_cur['sentence_pattern_classification'] in self._sentence_classifications_needed:
            mylog.info('LastQuestionMultiProductInteracton return True')
            return True
        else:
            return False

    def deal_interaction(self, sessionid_in, label2entities_cur_dict_in, str_in):
        # last_question, last_answer,last_sentence_pattern_classification = _get_last_question(sessionid_in)
        # last_question_rewrite,_=self._preprocess_class.process(last_question)
        last_question, last_answer, last_sentence_pattern_classification=_get_last_question_info(sessionid_in,flag_preprocess='question')
        mylog.info('deal_interaction:\t{}'.format(str(last_question)))
        abbrev2std_list=_deal_interaction(sessionid_in,[last_question],str_in)
        return 1, _default_name_abbrev, abbrev2std_list

class PureIntentInteraction(InteractionBase):
    _domain_areas=[fcname.product.value,]
    def __init__(self):
        super(PureIntentInteraction,self).__init__()
    def judge_interaction(self, sessionid_in, label2entities_cur_dict_in, str_in):
        user_cur=usermanager.get_user(sessionid_in)
        #{'dst_word_to_fufill':dst_word_to_fufill,'label2entities_cur_dict':label2entities_cur_dict})
        dst_word_to_fufill=user_cur['dst_word_to_fufill']
        label2entities_cur_dict=user_cur['label2entities_cur_dict']
        str_synonym_cut=user_cur['str_synonym_cut']
        str_raw_cut=user_cur['str_raw_cut']
        domain_classification=user_cur['domain_classification']
        intent_num=0
        if cname.property.value in dst_word_to_fufill:
            intent_num+=len(dst_word_to_fufill[cname.property.value])
        if cname.domain.value in dst_word_to_fufill:
            intent_num+=len(dst_word_to_fufill[cname.domain.value])
        if cname.property.value in label2entities_cur_dict:
            intent_num+=len(label2entities_cur_dict[cname.property.value])
        if cname.domain.value in label2entities_cur_dict:
            intent_num+=len(label2entities_cur_dict[cname.domain.value])
        if intent_num==1 and len(str_raw_cut)==1 and domain_classification in self._domain_areas :
            return True
        else:
            return False
    def deal_interaction(self, sessionid_in, label2entities_cur_dict_in, str_in):
        user_cur=usermanager.get_user(sessionid_in)
        domain_classification=user_cur['domain_classification']
        product_names=self._entity_class.get_domain2intent2std2sim_dict[domain_classification][cname.domain.value]
        product2str_dict=[{_tmp_for_show_str.get(product_iter,product_iter):product_iter+str_in} for product_iter in product_names]
        return 1, _default_name_abbrev, product2str_dict
class NoInteraction(InteractionBase):
    def __init__(self):
        super(NoInteraction, self).__init__()

    def judge_interaction(self, sessionid_in, label2entities_cur_dict_in, str_in):
        if label2entities_cur_dict_in['domain']:
            return True
        else:
            return False


InteractionSet = [CurStrAbbrevInteraction, LastQuestionMultiProductInteracton,RecomLastQuestionMultiProductInteraction,PureIntentInteraction]


class FuzzyInterAction(object):
    interactions_instances = [class_obj() for class_obj in InteractionSet]
    no_interaction = NoInteraction()

    def __init__(self):
        pass

    def deal_fuzzy_interaction(self, sessionid_in, label2entities_cur_dict_in, str_in, words_list_out):
        # todo 改成 class，不同的情况不同的交互
        if self.no_interaction.judge_interaction(sessionid_in, label2entities_cur_dict_in, str_in):
            mylog.info('no_interaction.judge_interaction  return True')
            pass
        else:
            for class_obj_iter in self.interactions_instances:
                if class_obj_iter.judge_interaction(sessionid_in, label2entities_cur_dict_in, str_in):
                    flag_inter, abbrev, abbrev2std_list = class_obj_iter.deal_interaction(sessionid_in,
                                                                                          label2entities_cur_dict_in,
                                                                                          str_in)
                    mylog.info(' {} return True'.format(str(class_obj_iter)))
                    return flag_inter, abbrev, abbrev2std_list
                else:
                    pass
        mylog.info('交互反问模块都没有return True')
        return 0, '', []
