import abc
import collections
import itertools
import math
from abc import ABCMeta

import numpy as np
from sklearn import preprocessing

from common.pathutil import PathUtil
from online.nlu.preprocess import Preprocess
from online.utils.funcs import readfile_line2dict, readfile_line2list
from online.utils.logdiy import mylog
from online.utils.funcs_business import replace_char2actualvalue
"""
    召回，相似度匹配方式进行召回处理
    1.单词召回，2词召回，3词召回，多词召回
    2.召回词语，召回句子  句子词语 召回 融合在一起，先召回句子，如果没有相似句子，挨个比较词语，召回词语
      同义句召回
    3.
    
    1.设定threshold，保留部分 组合，及组合所在的句子。
    2.比较输入句子和目前存在的句子对应到关键信息组合
    3.
"""


class TfidfDiy(object):
    _UNK = '_UNK'
    _PAD = '_PAD'
    _START_VOCAB = [_UNK, _PAD]
    _UNKID = 0
    _PADID = 1
    _STARTID = [_UNKID, _PADID]

    def __init__(self,rows_elems_in):
        # self._rows_elems=rows_elems_in
        # self._ngram=2
        self._preload(rows_elems_in)
    def _preload(self,rows_elems_in):
        rows_words_in = rows_elems_in
        term2freq_dict = self._counter_words(rows_words_in)
        term2id_dict = self._make_term2id(term2freq_dict)
        dict_idf = self._calc_idf_rows(rows_words_in)
        onehot_matrix, rows,similar2std_o2o_dict = self._tfidf2onehot_rows(rows_words_in, term2id_dict, dict_idf)
        self._onehot_matrix = onehot_matrix
        self._corpus_rows = rows
        self._term2id = term2id_dict
        self._idf_dict = dict_idf
        self._similar2std_o2o_dict=similar2std_o2o_dict
    def _counter_words(self, rows_words_in):
        # 计算term 词频
        term2freq_dict = collections.defaultdict(int)
        for row_set_words_iter in rows_words_in:
            for row_words_iter in row_set_words_iter:
                for word_iter in row_words_iter:
                    # print('word_iter==>',word_iter)
                    term2freq_dict[word_iter] += 1
        for index, vocab_fill_iter in enumerate(self._START_VOCAB):
            term2freq_dict[vocab_fill_iter] = 99999 - index
        return term2freq_dict

    def _make_term2id(self, term2freq_dict):
        term2freq_sorted = sorted(term2freq_dict.items(), key=lambda x: x[1], reverse=True)
        term2id_dict = dict()

        for index, tuple_iter in enumerate(term2freq_sorted):
            pair_info_iter=list(tuple_iter)[0]
            term2id_dict[pair_info_iter] = index
        return term2id_dict

    def one_hot_base(self, term2id_in):
        # 转换为one-hot
        # 统计所有词频，id2word,建立列表
        length = len(term2id_in)
        return [1] * length

    def _tfidf2onehot_onerow(self, row_words_in, term2id_in, term2idf_in,test_in=False):
        # 根据tfidf值，结合原始one_hot，输出 带有tfidf值的onehot,归一化
        length = len(term2id_in)
        onehot = [0] * length
        dict_tf = self._calc_tf_row(row_words_in)
        for word_iter, tf_iter in dict_tf.items():
            id_iter = term2id_in.get(word_iter, self._UNKID)
            idf_iter = term2idf_in.get(word_iter,self._UNKID)
            # if test_in:
            #     tf_iter=row_words_in.count(word_iter)
            if id_iter in self._STARTID:
                onehot[id_iter] = 0.005
            else:
                onehot[id_iter] = tf_iter * idf_iter
        return onehot

    def _tfidf2onehot_rows(self, rows_words_in, term2id_in, term2idf_in):
        onehots = list()
        rows = list()
        similar2std_o2o_dict=dict()
        for row_set_iter in rows_words_in:
            for row_words_iter in row_set_iter:
                onehot_iter = self._tfidf2onehot_onerow(row_words_iter, term2id_in, term2idf_in)
                # onehot_normalize = preprocessing.normalize(onehot_iter, norm='l2')
                onehots.append(onehot_iter)
                rows.append(row_words_iter)
                similar2std_o2o_dict[tuple(row_words_iter)]=row_set_iter[0]
        onehot_matrix = np.array(onehots)
        onehot_matrix_normalize = preprocessing.normalize(onehot_matrix, norm='l2')
        return onehot_matrix_normalize, rows,similar2std_o2o_dict

    def _calc_tf_row(self, row_words_in):
        dict_tf = collections.defaultdict(int)
        # print('row_words_in==>',row_words_in)
        for word_iter in row_words_in:
            dict_tf[word_iter] += 1
        length = len(row_words_in)
        for word, freq in dict_tf.items():
            # dict_tf[word]=freq/length
            dict_tf[word] = freq / length
        return dict_tf

    def _calc_idf_rows(self, rows_words_in):
        dict_idf = collections.defaultdict(int)
        length_whole = len(rows_words_in)
        for row_set_iter in rows_words_in:
            tmp_set_words=set()
            for row_words_iter in row_set_iter:
                for term_iter in row_words_iter:
                    #   if term_iter in row_words_iter:
                    if term_iter not in tmp_set_words:
                        dict_idf[term_iter] += 1
                    else:
                        pass
                    tmp_set_words.add(term_iter)
        for term_iter, idf_iter in dict_idf.items():
            dict_idf[term_iter] = math.log(length_whole / (idf_iter*2 + 1))
        dict_idf_ordered=collections.OrderedDict()
        dict_idf_tuples=sorted(dict_idf.items(),key=lambda x:float(x[1]),reverse=True)
        for word_iter,idf_iter in dict_idf_tuples:
            dict_idf_ordered[word_iter]=idf_iter
        # for k,v in dict_idf_ordered.items():
        #     print(k,v)
        return dict_idf_ordered

    def _calc_tfidf_row(self, row_words_in, rows_words_in):
        # 计算一行，即一个集合所有元素的tfidf，返回dict{w1:1,w2:1}
        dict_tf = self._calc_tf_row(row_words_in)
        # dict_idf = self._calc_idf_rows(rows_words_in)

        tfidf_class = collections.defaultdict(int)
        for key_tf, value_tf in dict_tf.items():
            tfidf_class[key_tf] = value_tf * self._idf_dict[key_tf]
        tfidf_sorted = sorted(tfidf_class.items(), key=lambda x: x[1], reverse=True)
        words2tfidf_dict = collections.OrderedDict()
        for word_iter, tfidf_iter in tfidf_sorted:
            words2tfidf_dict[word_iter] = tfidf_iter
        return words2tfidf_dict

    def _calc_tfidf_rows(self, list_nest_in):
        # 计算词语句子矩阵的tfidf
        # todo
        length_whole = len(list_nest_in)
        for index, words_set_iter in enumerate(list_nest_in):
            # tf
            for words_iter in words_set_iter:
                words2tfidf_row_dict = self._calc_tfidf_row(words_iter, list_nest_in)
            # for key, value in words2tfidf_row_dict.items():
            #     print(key, value)
        return [[]]

    def similarity(self, row_words_in, topn):
        # 根据已有的tfidf矩阵，返回topn
        # dict_tf=self._calc_tf_row(row_words_in)

        onehot = self._tfidf2onehot_onerow(row_words_in, self._term2id, self._idf_dict,True)
        onehot_filter=[(index,elem) for index,elem in enumerate(onehot) if elem>0]
        idf_filter=[(elem,self._idf_dict.get(elem,0)) for elem in row_words_in]
        # print(onehot_filter,idf_filter,idf_filter)
        # print('onehot==>',onehot)
        for word_iter in row_words_in:
            r1=self._term2id.get(word_iter)
            # print(word_iter,r1)
            r2=self._idf_dict.get(word_iter)
            # print(r1,r2)
        onehot_normalize=preprocessing.normalize([onehot],norm='l2')
        # print('onehot_normalize==>',onehot_normalize)
        scores = np.dot(onehot_normalize, self._onehot_matrix.T)[0]
        scores_dict = {index: score_iter for index, score_iter in enumerate(scores)}
        scores_list = sorted(scores_dict.items(), key=lambda x: float(x[1]), reverse=True)
        scores_list_topn = scores_list[:topn]
        # print('scores_list_topn==>',scores_list_topn)
        indexes = [iterow[0] for iterow in scores_list_topn]
        corpus_similar = [self._similar2std_o2o_dict[tuple(self._corpus_rows[index])] for index in indexes]
        # print('corpus_similar==>\n',corpus_similar)
        scores=[item[1] for item in scores_list_topn]
        return corpus_similar,scores

class SimilarModelBase(object):
    __metaclass__ = ABCMeta  # 指定该类的元类是ABCMeta
    _preprocess_class = Preprocess()
    _ngram_num = 1

    def __init__(self):
        self._preload()
        # pass

    def _preload(self):
        self._stopwords = self._preload_stopwords()

    def _preload_stopwords(self):
        """停用词加载"""
        stopwords_list = readfile_line2list(PathUtil().stopwords_filepath)
        words = list(itertools.chain.from_iterable(stopwords_list))
        return words

    @abc.abstractmethod
    def __load_similar_sents(self):
        # 加载同义句
        raise ValueError('要继承复写')

    def _filter_stopwords(self, words_in):
        # 从分词句子中，过滤 停用词
        return words_in
        for worditer in words_in:
            if list(worditer)[0] not in self._stopwords:
                words_ret.append(worditer)
        return words_ret

    def _get_words_freq(self, sentences_map_in):
        # 获取所有句子词频
        words_freq_dict = collections.defaultdict(int)
        # words_freq_dict_sorted=collections.Counter()
        for key, values in sentences_map_in.items():
            words_key_iter = self._preprocess_class.cut_words(key)
            # words_key_iter_with_label=psg.lcut(key)
            for word_iter in words_key_iter:
                words_freq_dict[word_iter] += 1
            for value_iter in values:
                words_iter = self._preprocess_class.cut_words(value_iter)
                for word_iter in words_iter:
                    words_freq_dict[word_iter] += 1
        words_freq_sorted = sorted(words_freq_dict.items(), key=lambda x: int(x[1]), reverse=True)
        return words_freq_sorted
    def _get_n_gram_row(self,sentence_in,n):
        words_key_iter = self._preprocess_class.cut_words(sentence_in)

        words_key_filtered = self._filter_stopwords(words_key_iter)
        words_key_combinate = list(itertools.combinations(words_key_filtered, r=n))
        return words_key_combinate,words_key_filtered
    def _get_n_gram(self, sentences_map_in, n):
        # 获取句子中，ngram
        words_std_and_similar_list = list()
        lengths = []
        sentences = list()
        for key, values in sentences_map_in.items():
            length_raw_words = 0
            words_std_and_similar_list_iter = list()

            words_key_combinate,words_key_filtered=self._get_n_gram_row(key,n)

            words_std_and_similar_list_iter.append(words_key_combinate)
            length_raw_words += len(words_key_filtered)
            for value_iter in values:
                words_value_combinate, words_value_filtered = self._get_n_gram_row(value_iter, n)
                # words_iter = self._preprocess_class.cut_words(value_iter)
                # words_value_filtered = self._filter_stopwords(words_iter)
                length_raw_words += len(words_value_filtered)
                words_std_and_similar_list_iter.append(words_value_combinate)
            words_std_and_similar_list.append(words_std_and_similar_list_iter)
            lengths.append(length_raw_words)
            sentences.append([key, *values])
        return words_std_and_similar_list, lengths, sentences


class SimilarModelSents(SimilarModelBase):
    def __init__(self):
        super(SimilarModelSents, self).__init__()
        self._load()
        self._threshold_le_2=0.8
        self._threshold_ge_2=0.7

    def __load_similar_sents(self):
        filepath = PathUtil().similiar_sentences_filepath
        line_o2m_dict, line_o2o_dict = readfile_line2dict(filepath)
        _sentences_map = line_o2m_dict
        # for k,v in _sentences_map.items():
        #     print(k,v)
        return _sentences_map

    def _load(self):
        sentences_map = self.__load_similar_sents()
        self._words_freq_sorted = self._get_words_freq(sentences_map)
        self.ngrams_nest, self._lengths_ngrams, self._sentences = self._get_n_gram(sentences_map, self._ngram_num)
        tfidf_instance=TfidfDiy(self.ngrams_nest)
        self._tfidf_instance=tfidf_instance
    def _pair2str(self,pairs_in):
        pairs=pairs_in
        # print('pairs==',pairs)
        words=[list(list(word)[0])[0] for word in pairs]
        return words
    def _filter_contain_elems(self,words_row_in,words_set_in):
        for index,words_tuple in enumerate(words_set_in):
            words_iter=words_tuple[0]
            intersect_part=set(words_row_in).intersection(set(words_iter))
            if len(intersect_part)==len(set(words_row_in)):
                return [words_set_in[index]]
        words_set_filter=[item for item in words_set_in if item[1]>0.7]
        return words_set_filter
    def similar_threshold(self,str_in):
        # words=psg.lcut(str_in)
        # print('words==>',words)
        row_words, _ = self._get_n_gram_row(str_in, self._ngram_num)
        words_rows_part, scores = self._tfidf_instance.similarity(row_words,5)
        # print(words_tuples_set)
        # print('-*- '*5)
        word_and_scores_tuples=list(zip(words_rows_part,scores))
        # print('word_and_scores_tuples==>',word_and_scores_tuples)
        word_and_scores_tuples_filter_threshold=list()
        for item in word_and_scores_tuples:
            if len(item[0])>2 or len(row_words)>2:
                if item[1]>self._threshold_ge_2:
                    word_and_scores_tuples_filter_threshold.append(item)
            else:
                if item[1]>self._threshold_le_2:
                    word_and_scores_tuples_filter_threshold.append(item)
        # word_and_scores_tuples_filter_threshold=[item for item in word_and_scores_tuples if item[1]>0.5]
        word_and_scores_tuples_filter=self._filter_contain_elems(row_words,word_and_scores_tuples_filter_threshold)
        # scores=[iterow for iterow in scores if iterow>0.5]

        words_set = list()
        scores_set=list()
        for (words_iter,score_iter) in word_and_scores_tuples_filter:
            words = self._pair2str(words_iter)
            words_set.append(words)
            scores_set.append(score_iter)
        if words_set:
            print('row_words==>', row_words)
            print('words_set==>',words_set)
            print('scores_set==>',scores_set)
        str_set=[''.join(words_iter) for  words_iter in words_set]
        str_set_replaced_characters=[replace_char2actualvalue(str_in,str_iter) for str_iter in str_set]
        return str_set_replaced_characters, scores_set
    def similar(self,str_in,topn=1):
        # words=psg.lcut(str_in)
        row_words,_=self._get_n_gram_row(str_in, self._ngram_num)
        # print('row_words==>',row_words)
        words_tuples_set,scores=self._tfidf_instance.similarity(row_words,topn)
        # print(words_tuples_set)
        # print('-*- '*5)
        words_set=list()
        for words_tuples_iter in words_tuples_set:
            # for itemrow_tuple in words_tuples_iter:
            itemrow=words_tuples_iter
            words=self._pair2str(itemrow)
            words_set.append(words)
        return words_set,scores
    def deal(self):
        for index,words_set_iter in enumerate(self.ngrams_nest):
            for words_row_iter in words_set_iter:
                words_row = [word_iter for word_iter in words_row_iter]
                # print(words_row)
                result=self._tfidf_instance.similarity(words_row,1)
            if index>10:
                break
class RecallModel(SimilarModelBase):
    _entity_filepath_set = [PathUtil().domain_filepath, PathUtil().intent_filepath, PathUtil().property_filepath,
                            PathUtil().company_domain_filepath,
                            PathUtil().company_property_filepath]

    def __init__(self):
        super(RecallModel, self).__init__()

    def __load_similar_sents(self):
        # 从文件获取所有相似词的dict
        std2similar_words_dict = collections.defaultdict(list)
        for filepath_iter in self._entity_filepath_set:
            line_o2m_dict, line_o2o_dict_order = readfile_line2dict(filepath_iter)
            for key, value in line_o2m_dict.items():
                std2similar_words_dict[key].extend(value)

    def _get_words2term(self):
        # 获取每个细分字词单元跟term的映射,同时获取到字词在该term的权重
        pass

    def _get_weight_word_in_term(self):
        # 获取每个细分字词在此term中的tfidf
        pass

    def recall(self, str_in):
        # 根据输入句子，分词，召回相关的term
        pass


if __name__ == '__main__':
    sm = SimilarModelSents()
    # sm.deal()
    s='通讯地址换了咋办我想换一下了'
    s='年龄限制是什么'
    s='是多久'
    s='多大'
    s='什么是职业分类表'
    s='我要去香港，怎么买产品'
    s='是否有补偿有什么要求'
    s='怎么通知保险公司'
    s='我想查下保单'
    s='有什么限制'
    s='有什么要求'
    # s='如何理赔'
    # s='合同的解除'
    s='我想查下保单'
    s='安行万里包括哪些方面的保障'
    s='保自行车意外吗'
    s='安行万里多大年纪可以投保呀'
    s='安行万里境外险多大年纪可以投保呀'
    s='有什么要求'
    s='它的投保限制'
    s='86岁能投保吗'
    s='还没上学能投保学生意外计划吗'
    # s='它的投保条件'
    out=sm.similar_threshold(s)
    print(out)