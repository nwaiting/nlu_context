from online.nlu.user_manage import usermanager
from online.utils.redis_operation import getQAPairs
import requests
from online.utils.logdiy import mylog
from online.nlu.entity import Entity
from online.utils.nameutil import ContextNames as cname
from online.utils.funcs import reset
_url_kg_slots = 'http://xxx'


def _get_last_question(sessionid_in):
    jdpin_id = usermanager.get_user(sessionid_in)['jdpin_id']
    instance = usermanager.get_user(sessionid_in).get_instance_by_index(-1)
    last_sentence_pattern_classification = ''
    if instance:
        last_question = instance.question
        last_sentence_pattern_classification = instance.sentence_pattern_classification
        # print('last_question==>',last_question)
        chatRecordList = getQAPairs(jdpin_id)
        if chatRecordList:
            last_answer = chatRecordList[-1].answer
            last_question = chatRecordList[-1].question
            usermanager.get_user(sessionid_in).update_slots(-1, **{'answer': last_answer})

            # mylog.info('获取 上一轮 question\t{}\n，answer\t{}\n 从 redis'.format(str(last_question),str(last_answer)))
            # mylog.info('redis中5轮问题 开始')
            # for chatrecord_iter in chatRecordList:
            #     question_iter=chatrecord_iter.question
            #     answer_iter=chatrecord_iter.answer
            #     mylog.info('redis 迭代  question\t{}\t\tanswer\t{}'.format(question_iter,answer_iter))
            # mylog.info('redis中5轮问题 开始')

        else:
            mylog.info('_get_last_question 获取到instance，但是没有chatRecordList，last_question={}'.format(last_question))
            last_answer = ''
    else:
        mylog.info('_get_last_question  没有获取到instance')
        last_question, last_answer = '', ''
    mylog.info('从redis获取到的last_question\t{},\n last_answer\t{},\nlast_sentence_pattern_classification\t{}'.format(last_question,last_answer,last_sentence_pattern_classification))
    return last_question, last_answer, last_sentence_pattern_classification


def request_post_kg(str_in, jdpin_in):
    # params = {"question": "我要去潜水能买什么产品？", "jdPin": "安行万里保不保外国人"}
    params = {"question": str_in, "jdPin": jdpin_in}
    status = 0
    try:
        result = requests.post(_url_kg_slots, json=params, timeout=0.5).json()
        status = 1
        mylog.info('请求kg 返回结果\t{}'.format(str(result)))
    except Exception as e:
        error_str = 'request_kg 错误信息{}\t url\t{}字段\t{}'.format(str(e.args), str(_url_kg_slots), str(params))
        mylog.debug(error_str)
        mylog.info(error_str)
        result = {}
    return status, result


_tmp_for_show_str = {
    '附加安康福瑞长期重大疾病保险B款': '安康福瑞附加险',
    '安联附加安康逸生长期重大疾病保险B款': '安康逸生附加险',
    '安联安康逸生两全保险B款': '安康逸生两全保险',
    '安联安康无忧医疗保险': '安康无忧医疗保险',
    '安联安康福瑞两全保险B款': '安康福瑞两全险',
}

_entity_class = Entity()


def _get_entity_from_strs(str_list_in, domain_classification):
    """从string中获取实体词"""
    label2entities_cur_dict, words_timestap = _entity_class.find_entity(str_list_in, domain_classification)
    return label2entities_cur_dict, words_timestap


def _deal_interaction(sessionid_in, strs_get_entity_from, str_cur):
    user_cur = usermanager.get_user(sessionid_in)
    last_label2entities_cur_dict, last_words_timestap = _get_entity_from_strs(strs_get_entity_from,
                                                                              user_cur['domain_classification'])
    abbrev2std_list = list()
    for entity_iter in last_label2entities_cur_dict[cname.domain.value]:
        str_iter = entity_iter + str_cur
        # todo 暂时，为了显示
        # abbrev2std_list.append({entity_iter: str_iter})
        abbrev2std_list.append({_tmp_for_show_str.get(entity_iter, entity_iter): str_iter})
    # mylog.info('获取到的abbrev2std_list\t{}'.format(str(abbrev2std_list)))
    return abbrev2std_list



def replace_char2num(s_old,s_new):
    str_replaced=s_new
    for pattern_iter1 in reset.character_and_unit:
        match_part_new=pattern_iter1.search(s_new)
        if match_part_new:
            for pattern_iter2 in reset.arabnum_and_unit:
                match_part_old=pattern_iter2.search(s_old)
                if match_part_old:
                    str_new=match_part_new.groupdict()['character']
                    str_old=match_part_old.groupdict()['number']
                    str_replaced=s_new.replace(str_new,str_old)
    return str_replaced
def replace_char2actualvalue(s_old,s_new):
    str_replaced=replace_char2num(s_old,s_new)
    return str_replaced

if __name__=='__main__':
    s_old='18块钱能买保险吗'
    s_new='a岁能买保险吗18'
    result=replace_char2actualvalue(s_old,s_new)
    print(result)