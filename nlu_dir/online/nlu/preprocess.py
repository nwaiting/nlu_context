import collections
import re
import copy
import jieba
import jieba.posseg as psg

from common.pathutil import PathUtil
from online.nlu.entity import Entity
from online.nlu.trans_digit import ChineseNumberInteger
from online.utils.funcs import ReSet
from online.utils.funcs import Singleton
from online.utils.funcs import readfile_line2dict, list2re, dict2sorted_dict
from online.utils.nameutil import ContextNames as cname, SymbolRepresentMap as srepresent, _shared_strs_by_two_entity,_fufilled_part_str_missied
from online.utils.logdiy import mylog



def wapper(fn):
    def _wapper(*args):
        str_cur=args[1]
        flag_change=0
        for k,v in _fufilled_part_str_missied.items():
            if k in str_cur and k+v not in str_cur:
                flag_change=1
                str_cur=str_cur.replace(k,k+v)
        func = fn(args[0],str_cur)
        for k,v in _fufilled_part_str_missied.items():
            if flag_change==1:
                func=func.replace(v,'',1)
        return func
    return _wapper

class SimiliarReplace(object):
    _similiar_filepath = PathUtil().similiar_words_filepath
    _pathutil_class = PathUtil()
    _entity_class = Entity()
    _reback_filepath = PathUtil().reback_file

    def __init__(self):
        self._preload()
        self._reback_o2o_dict = self._preload_reback()

    def _preload_reback(self):
        #替换了替换错了，回退城一个标准的实体词
        line_o2m_dict, line_o2o_dict_order = readfile_line2dict(self._reback_filepath)
        return line_o2o_dict_order

    def _preload(self):
        # 同义词和标准词的对应
        line_o2m_dict, line_o2o_dict = readfile_line2dict(self._similiar_filepath)
        self._entity_o2o_dict = self._entity_class.entity_o2o_dict
        entity_o2o_dict_tmp = {**line_o2o_dict, **self._entity_o2o_dict}
        self._o2o_similar_dict = dict2sorted_dict(entity_o2o_dict_tmp)
        self.re_o2o_similar_keys = re.compile('(' + '|'.join(self._o2o_similar_dict.keys()) + ')')
        #一对多的对应
        o2m_similar_dict = collections.OrderedDict()
        entity_o2m_dict = self._entity_class.entity_o2m_order_dict
        o2m_tmp_dict = [entity_o2m_dict, line_o2m_dict]
        for o2m_dict_iter in o2m_tmp_dict:
            for o_iter, m_iter in o2m_dict_iter.items():
                if o_iter not in o2m_similar_dict:
                    o2m_similar_dict[o_iter] = set(m_iter)
                else:
                    o2m_similar_dict[o_iter].update(m_iter)
        re_o2m_similiar_dict = dict()
        for o_iter, m_iter in o2m_similar_dict.items():
            m_iter_sorted = sorted(m_iter, key=lambda x: len(x), reverse=True)
            o2m_similar_dict[o_iter] = m_iter_sorted
            re_o2m_similiar_dict[o_iter] = list2re(m_iter_sorted)
        self._o2m_similar_dict = o2m_similar_dict
        self._re_o2m_similar_dict = re_o2m_similiar_dict
        # self._entity_class.get_label2entities()
    @property
    def get_o2o_map_word_and_sentence(self):
        line_o2m_dict, line_o2o_dict = readfile_line2dict(PathUtil().similiar_sentences_filepath)
        # 句子同义置换和同义词同义置换同时放在一块进行处理
        word_o2o_dict = self._o2o_similar_dict
        o2o_dict = {**word_o2o_dict, **line_o2o_dict}
        o2o_dict_sorted = dict2sorted_dict(o2o_dict)
        return o2o_dict_sorted
    @property
    def o2m_similar_dict(self):
        return self._o2m_similar_dict

    @property
    def re_o2m_similar_dict(self):
        return self._re_o2m_similar_dict
    def replace_str(self, str_in):  # 字符串判断
        str_tmp = str_in

        _fufilled_part_str_missied_copy=copy.deepcopy(_fufilled_part_str_missied)
        flag_change = 0
        for k, v in _fufilled_part_str_missied.items():
            if k in str_tmp and k + v not in str_tmp:
                flag_change = 1
                str_tmp = str_tmp.replace(k, k + v)


        tmp_key_store = ['A#$', 'B#$', 'C#$', 'D#$', 'E#$', 'F#$', 'G#$']
        tmp_key_dict = {}
        index_incres = 0
        tmp_kept_strs_part_dict = dict()
        for sent_similar_iter, sent_std_iter in self._o2o_similar_dict.items():

            if sent_similar_iter in str_tmp:
                for k in list(_fufilled_part_str_missied_copy.keys()):
                    v=_fufilled_part_str_missied_copy[k]
                    if k+v in sent_similar_iter:
                        _fufilled_part_str_missied_copy.pop(k)
                elems = []
                str_split = str_tmp.split(sent_similar_iter)
                char_represent = tmp_key_store[index_incres]
                tmp_key_dict[tmp_key_store[index_incres]] = sent_std_iter
                for elem in str_split[:-1]:
                    elem += char_represent
                    if self.re_o2o_similar_keys.search(str_split[-1]):
                        pass
                    elif sent_similar_iter[-2:] in _shared_strs_by_two_entity:
                        elem += sent_similar_iter[-2:]
                        tmp_kept_strs_part_dict[char_represent + sent_similar_iter[-2:]] = char_represent

                    else:
                        pass
                    elems.append(elem)
                index_incres += 1
                elems.append(str_split[-1])
                str_tmp = ''.join(elems)
            else:
                pass
        for key, value in tmp_kept_strs_part_dict.items():
            str_tmp = str_tmp.replace(key, value)
        for key, value in tmp_key_dict.items():
            str_tmp = str_tmp.replace(key, value)

        for k, v in _fufilled_part_str_missied_copy.items():
            if flag_change == 1:
                str_tmp = str_tmp.replace(v, '', 1)

        return str_tmp

    def replace_list(self, str_list_in):  # 分词结果比较
        str_list_tmp = str_list_in
        for raw_word_iter, standard_word_iter in self._o2o_similar_dict.items():
            for index, word_iter in enumerate(str_list_tmp):
                if word_iter == raw_word_iter:
                    str_list_tmp[index] = standard_word_iter
                elif index >= 1 and str_list_tmp[index - 1][:-2] + word_iter == raw_word_iter:
                    str_list_tmp[index] = standard_word_iter
                else:
                    pass
        return str_list_tmp

    def bool_entity_words_exists_and_number(self, sentence_in):
        str_tmp = sentence_in
        counter_exist = 0
        for raw_word_iter, standard_word_iter in self._entity_o2o_dict.items():
            if raw_word_iter in str_tmp:
                str_tmp = str_tmp.replace(raw_word_iter, '')
                counter_exist += 1
        return bool(counter_exist), counter_exist

    def reback_replace(self, str_synonym_in, str_raw_in):
        str_tmp = str_synonym_in
        for word_old_iter, word_new_iter in self._reback_o2o_dict.items():
            if word_old_iter in str_synonym_in and word_old_iter in str_raw_in:
                pass
            elif word_old_iter in str_synonym_in and word_new_iter in str_raw_in:
                str_tmp = str_tmp.replace(word_old_iter, word_new_iter)
            else:
                pass
        return str_tmp

class SimiarReplaceO2o(object):
    _entity_class=Entity()
    _field_o2o_needed=[cname.domain.value,]
    def __init__(self):
        self._preload()
    def _preload(self):
        intent2sim2std_o2o_dict=collections.defaultdict(dict)
        for field_iter in self._field_o2o_needed:
            dict_iter=self._get_o2o_by_intent(field_iter)
            intent2sim2std_o2o_dict[field_iter].update(dict_iter)
        for field_iter,o2o_iter in intent2sim2std_o2o_dict.items():
            intent2sim2std_o2o_dict[field_iter]=dict2sorted_dict(o2o_iter)
        self._intent2sim2std_o2o_dict=intent2sim2std_o2o_dict
    def _get_o2o_by_intent(self,intent_in):
        return self._entity_class.get_intent2sim2std_o2o_dict[intent_in]
    def kept_intent_in_str(self,str_in):
        symbol2actual=dict()
        represents=['H#$', 'I#$', 'J#$', 'K#$', 'L#$', 'M#$', 'N#$']
        str_tmp=str_in
        counter=0
        for intent,o2o_dict_iter in self._intent2sim2std_o2o_dict.items():
            for sim_iter,std_iter in o2o_dict_iter.items():
                if sim_iter in str_tmp:
                    symbol_cur=represents[counter]
                    counter+=1
                    str_tmp=str_tmp.replace(sim_iter,symbol_cur)
                    symbol2actual[symbol_cur]=sim_iter
        return str_tmp,symbol2actual
def jieba_add_words():
    reset = ReSet()
    pu = PathUtil()
    filepaths = [pu.domain_filepath, pu.intent_filepath, pu.property_filepath, pu.company_domain_filepath
        , pu.company_property_filepath, pu.prounoun_filepath]
    words_ret = list()
    for filepath in filepaths:
        with open(filepath, 'r', encoding='utf-8') as fr:
            lines = [line.strip('\r\n ') for line in fr]
            for line in lines:
                words_iter = reset.split_pattern[0].split(line)
                words_iter = [word_iter for word_iter in words_iter if len(word_iter) > 1]
                words_ret.extend(words_iter)
    return words_ret


def jieba_diy():
    diywords_filepath = PathUtil().diy_words_filepath
    jieba.load_userdict(diywords_filepath)
    # print(psg.lcut('什么是职业分类表'))
    for word_iter in jieba_add_words():
        jieba.add_word(word_iter)
    jieba.suggest_freq(['那', '不买'], tune=True)


class Preprocess(object,metaclass=Singleton):
    _reset_class = ReSet()
    _similiar_class = SimiliarReplace()
    _entity_class = Entity()
    _chinese_number_class = ChineseNumberInteger()
    _similarreplace_o2o_class=SimiarReplaceO2o()
    def __init__(self):
        self._preload()

    def _preload(self):
        jieba_diy()
        o2o_dict_sorted = self._load_similar_sentence()
        self._similar_line_o2o_dict = self._expand_similar_sentences(o2o_dict_sorted)
        self._load_represent_chars_map()

    def _load_represent_chars_map(self):
        line_o2m_dict, line_o2o_dict_order = readfile_line2dict(PathUtil().char_represent_map_file)
        self._represent_char_o2o_dict = line_o2o_dict_order

    def _expand_similar_sentences(self, o2o_dict_sorted_in):
        # similar_line_o2o_dict = self._similar_line_o2o_dict
        similar_line_o2o_dict = o2o_dict_sorted_in
        o2m_similar_dict = self._similiar_class.o2m_similar_dict
        similar_line_o2o_expanded_dict = dict()
        for similar_str_iter, std_str_iter in similar_line_o2o_dict.items():
            for std_word, re_similar_words in self._similiar_class.re_o2m_similar_dict.items():
                matched_part = re_similar_words.search(similar_str_iter)
                if matched_part:
                    matched_str = matched_part.group()
                    for word_iter in o2m_similar_dict[std_word]:
                        new_str_iter = similar_str_iter.replace(matched_str, word_iter)
                        similar_line_o2o_expanded_dict[new_str_iter] = std_str_iter
        # print('before  expand', len(o2o_dict_sorted_in))
        _similar_line_o2o_dict = {**o2o_dict_sorted_in, **similar_line_o2o_expanded_dict}
        _similar_line_o2o_dict_sorted = dict2sorted_dict(_similar_line_o2o_dict)
        # print('after   expand', len(_similar_line_o2o_dict_sorted))
        return _similar_line_o2o_dict_sorted

    def _load_similar_sentence(self):
        line_o2m_dict, line_o2o_dict = readfile_line2dict(PathUtil().similiar_sentences_filepath)
        # 句子同义置换和同义词同义置换同时放在一块进行处理
        # word_o2o_dict = self._similiar_class._o2o_similar_dict
        # o2o_dict = {**word_o2o_dict, **line_o2o_dict}
        o2o_dict = line_o2o_dict
        o2o_dict_sorted = dict2sorted_dict(o2o_dict)
        return o2o_dict_sorted

    def _synonym_replace_by_words(self, word_list_in):
        return self._similiar_class.replace_list(word_list_in)

    def _synonym_replace_by_str(self, word_list_in):
        return self._similiar_class.replace_str(''.join(word_list_in))

    def _synonym_replace(self, word_list_in):
        return self._synonym_replace_by_str(word_list_in)

    def _cut_words(self, str_in):
        return jieba.lcut(str_in)

    def _clean_start_end(self, str_in):
        return str_in.strip('\r\n ')

    def _clean_punc(self, str_in):
        str_tmp = str_in
        for pattern_iter in self._reset_class.puncs_pattern:
            str_tmp = pattern_iter.sub('', str_tmp)
        return str_tmp

    def _similar_sentences_replace_kept_raw(self,str_in):
        str_tmp, symbol2actual=self._similarreplace_o2o_class.kept_intent_in_str(str_in)
        return str_tmp,symbol2actual
    def _similar_sentences_replace_kernal(self,str_in):
        str_symbol_replace, replace_new2old_dict = self.char2symbol(str_in)
        str_tmp = str_symbol_replace
        tmp_key_store = ['A#$', 'B#$', 'C#$', 'D#$', 'E#$', 'F#$', 'G#$']
        tmp_key_dict = {}
        index_incres = 0
        for sent_similar_iter, sent_std_iter in self._similar_line_o2o_dict.items():
            if sent_similar_iter in str_tmp:
                elems = []
                str_split = str_tmp.split(sent_similar_iter)
                char_represent = tmp_key_store[index_incres]
                tmp_key_dict[tmp_key_store[index_incres]] = sent_std_iter
                for elem in str_split[:-1]:
                    elem += char_represent
                    elems.append(elem)
                index_incres += 1
                elems.append(str_split[-1])
                str_tmp = ''.join(elems)
            else:
                pass
        for key, value in tmp_key_dict.items():
            str_tmp = str_tmp.replace(key, value)
        for char_iter, reals_iter in replace_new2old_dict.items():
            for real_iter in reals_iter:
                str_tmp = str_tmp.replace(char_iter, real_iter, 1)
        return str_tmp

    def _similiar_sentences_replace(self, str_in):
        str_kept_raw=str_in
        str_kept_raw_sim_replace=self._similar_sentences_replace_kernal(str_kept_raw)
        return str_kept_raw_sim_replace
    def _chinese_number2arab_number(self, words_list_in):
        str_in = ''.join(words_list_in)
        for pattern_iter in self._reset_class.chinese_number_unitmeasur_pattern:
            if pattern_iter.search(str_in):
                words_ret = list()
                for word_iter in words_list_in:
                    flag_change = 0
                    for pattern_iter in self._reset_class.chinese_number_pattern:
                        if pattern_iter.fullmatch(word_iter):
                            word_transed = str(self._chinese_number_class.trans_chinese2digit(word_iter))

                            flag_change = 1
                            break
                    else:
                        for pattern_iter in self._reset_class.chinese_number_unitmeasur_pattern:
                            if pattern_iter.fullmatch(word_iter):
                                number_cur = pattern_iter.search(word_iter).groupdict()['number']
                                unit_cur = pattern_iter.search(word_iter).groupdict()['unit']
                                number_cur_transed = self._chinese_number_class.trans_chinese2digit(number_cur)
                                # print(number_cur_transed,type(number_cur_transed))
                                word_transed = str(number_cur_transed) + unit_cur
                                flag_change = 1
                    if flag_change == 0:
                        word_transed = word_iter
                    else:
                        if word_transed in ['10',10]:
                            word_transed='1'
                    words_ret.append(word_transed)

                return words_ret
        return words_list_in

    def _reback_replace(self, str_synonym_in, str_raw_in):
        return self._similiar_class.reback_replace(str_synonym_in, str_raw_in)

    def _arab2symbol(self, str_in):
        replace_new2old_dict = collections.defaultdict(list)
        str_tmp = str_in
        for pattern_iter in self._reset_class.num_pattern:
            match_part = pattern_iter.search(str_tmp)
            while match_part and match_part.groupdict()['number'] != srepresent.num.value:
                if match_part:
                    old_str = match_part.groupdict()['number']
                    str_tmp = str_tmp.replace(old_str, srepresent.num.value)
                    replace_new2old_dict[srepresent.num.value].append(old_str)
                else:
                    pass
                match_part = pattern_iter.search(str_tmp)

        return str_tmp, replace_new2old_dict

    def _job2symbol(self, str_in):
        str_tmp = str_in
        replace_new2old_dict = collections.defaultdict(list)
        for pattern_iter in self._reset_class.job_pattern:
            match_part = pattern_iter.search(str_tmp)
            while match_part and match_part.groupdict()['job'] != srepresent.job.value:
                if match_part:
                    old_str = match_part.groupdict()['job']
                    str_tmp = str_tmp.replace(old_str, srepresent.job.value)
                    replace_new2old_dict[srepresent.job.value].append(old_str)
                else:
                    pass
                match_part = pattern_iter.search(str_tmp)
                # print('1')
        return str_tmp, replace_new2old_dict

    def _represent_char2normalize(self, str_in):
        str_tmp = str_in
        for sim_iter, std_iter in self._represent_char_o2o_dict.items():
            str_tmp = str_tmp.replace(sim_iter, std_iter)
        return str_tmp

    def char2symbol(self, str_in):
        str_arab, arab_replace_new2old_dict = self._arab2symbol(str_in)
        str_job, job_replace_new2old_dict = self._job2symbol(str_arab)
        str_char2normalize_tmp = self._represent_char2normalize(str_job)
        replace_new2old_dict = {**arab_replace_new2old_dict, **job_replace_new2old_dict}
        return str_char2normalize_tmp, replace_new2old_dict

    def cut_words(self, str_in):
        return psg.lcut(str_in)

    def process(self, str_in):
        str_clean_se = self._clean_start_end(str_in)
        str_clean_punc = self._clean_punc(str_clean_se)
        str_std = self._similiar_sentences_replace(str_clean_punc)
        # str_std=str_clean_punc
        words = jieba.lcut(str_std)
        words_replaced = self._synonym_replace(words)
        words_number_transed = self._chinese_number2arab_number(words_replaced)
        str_synonym = ''.join(words_number_transed)
        str_synonym = self._reback_replace(str_synonym, str_in)
        words = self._cut_words(str_synonym)
        mylog.info(
            '当前class\t{}\t\t 当前函数{}\n 输入str\t，输出str\t'.format(str(self.__class__), 'process', str_in, str_synonym))
        return str_synonym, words


if __name__ == '__main__':
    s = '安顺畅游II/随心飞（意外险/航意险）买了后不想要了'
    s = '附加安康福瑞长期重大疾病保险和附加安康福瑞长期重大疾病保险的我们的合同有'
    s = '安康福瑞两全保险出险安康保险事故逸生B款怎么办保险事故怎么搞'
    s = '安联安康福瑞两全保险B款出事了怎么办'
    s = '就诊医院有什么要求'
    s = '安联安康逸生两全保险（B款）如何解除合同？解除合同风险是什么？'
    s = '保险金额是什么安联安康无忧医疗保险'
    s = '安康可以买吗福瑞呢'
    s = '我是从事教育行业的，18岁可以买2000块钱的保险吗'
    s = '安联安康无忧医疗保险计划表'
    s = '安联安康无忧医疗保险保险责任'
    s = '安康无忧保险金给付'
    s = '安康福瑞两全保险（B款）基本保险金额'
    s = '安康无忧合同终止'
    s = '安康无忧合同的解除'
    s = '安康无忧责任免除'
    s = '安行万里保单咋使用'
    s = '安行万里基本保险金额'
    s = '安行万里基本保额'
    s = '安行万里保单周年日十几号'
    s = '安行万里保单怎么使用'
    s = '安康'
    s = 'B款安联安康福瑞最低是多少'
    s = '保障范围呢'
    s = '安康福瑞的投保年龄'
    s = '合同解除流程呢'
    s = '我要去香港，怎么买产品'
    s = '122112'
    s = '安康福瑞保险金额'
    s = '安康无忧医疗保障保险计划表'
    s = '上海分公司的电话多少'
    # s = '安联安康无忧医疗保险10年后可以申请理赔吗吗'
    # s='安联安康无忧医疗保险怎么通知保险公司'
    # s='是否有补偿有什么要求'
    # s='我想查下保单信息'
    # s='安行万里退保条件'
    # s='安行万里境外险的保单信息'
    # s = '什么是职业分类表'
    # s = '安联安康福瑞两全保险B款争议处理'
    # s='附加安康福瑞长期重大疾病保险B款十八周岁前重大疾病的定义'
    # s='能退保吗安康逸生B款'
    # s='你好啊'
    # preprocess_class=Preprocess()
    # out=preprocess_class.process(s)
    # print(out)
    # s='安康逸生B款能退保吗'
    # s='1'
    # s='安联安康无忧医疗保险怎么通知保险公司'
    # s='安康的投保年龄'
    # s='如何理赔'
    # s='出境自驾，你们的产品保吗？'
    # s='安康无忧保险费的支付及宽限期'
    # s='我家孩子两岁，怎么配置保险'
    # s='安行万里境外险的保单信息'
    s='86岁能投保安行万里吗'
    s='18周岁能投保安行万里吗'
    s='十七周岁了买啥保险'
    s='我今年内十七周岁了买啥保险'
    s='还没上学能投保学生意外计划吗'
    preprocess_class = Preprocess()
    out = preprocess_class.process(s)
    # out = preprocess_class.char2symbol(s)
    print([out])
