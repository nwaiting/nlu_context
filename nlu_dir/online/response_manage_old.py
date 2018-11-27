from online.field_check import PreprocessCheck,RewriteCheck
from online.nlu.preprocess import Preprocess
from online.nlu.query_rewrite import NerDeal
from online.utils.funcs import Singleton
import abc
import copy
from online.utils.nameutil import ResponseCategory as rcategory
import logging.config
from common.pathutil import PathUtil
from online.nlu.user_manage import usermanager
logging.config.fileConfig(open(PathUtil().get_logging_config, encoding='utf-8'))
logger = logging.getLogger("response_manage")

class BaseResponse(object):
    _data_return = {'status': 0, 'data': {}, 'msg': None}
    def __init__(self):
        pass
    @abc.abstractmethod
    def _check(self,input):
        pass
    @abc.abstractmethod
    def _response(self,input):
        pass
    def response(self,input_in):
        input_str='此次响应，输入的input是\t '
        for key,value in input_in.items():
            # print(key,value)
            input_str+=('\t'+key+'\t'+str(value)+'\t'*2)
        logger.info(input_str)
        data_return=self._response(input_in)
        data_return_str='此次响应，返回的data_return是\t '
        for key, value in data_return.items():
            # print(key,value)
            data_return_str += ('\t' + key + '\t' + str(value) + '\t' * 2)
        logger.info(data_return_str)
        return data_return
class PreProcessResponse(BaseResponse):
    name=rcategory.preprocess.value
    _preprocess_check_class=PreprocessCheck()
    _preprocess_class=Preprocess()
    def __init__(self):
        super(PreProcessResponse,self).__init__()
    def _preprocess(self, str_in):
        str_synonym, words = self._preprocess_class.process(str_in)
        return {'str_synonym': str_synonym, 'words_segment': words}
    def _check(self,input):
        bool_input, _msg = self._preprocess_check_class.check(input)
        return bool_input,_msg
    def _response(self,input):
        _data_return=copy.deepcopy(self._data_return)
        bool_input,_msg=self._check(input)
        if bool_input:
            _data_return['status'] = 1
            _data_return['data'] = self._preprocess(input.question)
        else:
            _data_return['status'] = 0
            _data_return['msg'] = _msg
        return _data_return
class RewriteResponse(BaseResponse):
    name=rcategory.rewrite.value
    _rewrite_check_class=RewriteCheck()
    _preprocess_class=Preprocess()
    _nerdeal_class=NerDeal()
    _usermanager=usermanager

    def __init__(self):
        super(RewriteResponse,self).__init__()
    def _rewrite(self,sessionid_in):
        # words_list_out, dst_word_to_fufill, label2entities_cur_dict, abbrev2stds_dict = self._nerdeal_class.replace_with_context(sessionid_in)
        words_list_out, dst_word_to_fufill, label2entities_cur_dict, flag_inter,abbrev_str, abbrev2std_list = self._nerdeal_class.replace_with_context(sessionid_in)

        return {'words_with_context': words_list_out, 'words_with_context_notin_curstr': dst_word_to_fufill,
                'label2entities_cur_dict': label2entities_cur_dict,'abbrev2stds_dict':abbrev2std_list}
    def _check(self,input):
        bool_input, _msg = self._rewrite_check_class.check(input)
        return bool_input,_msg
    def _response(self,input):
        _data_return=copy.deepcopy(self._data_return)
        bool_input,_msg=self._check(input)
        if bool_input:
            _data_return['status'] = 1
            # str_synonym, words = self._preprocess_class.process(input.question)
            user_cur=self._usermanager.create(input.jdpin,input.session)
            # user_cur.update({'str_synonym':str_synonym,'str_synonym_cut':str_synonym})
            usermanager.update(input.session,str_raw=input.question)
            _data_return['data'] = self._rewrite(sessionid_in=input.session)
            _data_return['data']['str_synonym'] = user_cur['str_synonym']
        else:
            _data_return['status'] = 0
            _data_return['msg'] = _msg
        return _data_return
class WrongResponse(BaseResponse):
    name=rcategory.wrong_url_field.value
    def __init__(self):
        super(WrongResponse,self).__init__()
    def _check(self,input):
        pass
    def _response(self,input):
        _data_return=copy.deepcopy(self._data_return)
        _data_return['status'] = 0
        _data_return['msg'] = 'api输入字段不对,目前仅支持  preprocess,rewrite 两个'
        return _data_return

ResponseSet=[PreProcessResponse,RewriteResponse,WrongResponse]
class ResponseManage(object):
    __dict__ = {response_class.name:response_class() for response_class in ResponseSet}
    _usermanager=usermanager
    def __init__(self):
        pass
    def distribute(self,name_in,input_in):
        logger.info('此次响应，url字段是    {}'.format(str(name_in)))
        class_cur=self.__dict__.get(name_in)
        if not class_cur:
            class_instance_cur=self.__dict__['wrong_url_field']
        else:
            class_instance_cur=class_cur

        return class_instance_cur.response(input_in)
