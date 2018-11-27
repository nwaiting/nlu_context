import sys
from enum import Enum


class ContextNames(Enum):
    domain = 'domain'
    # intent='intent'
    property = 'property'


class FieldClassifyNames(Enum):
    product = 'product'
    company = 'company'
    common = 'product'
    alldomain = 'alldomain'


class NameMap(Enum):
    last_question = 'last_question'


class RepresentWordsNames(Enum):
    person = 'person'


class PatternClassificationMapNames(Enum):
    common_classification = 'common_classification'
    inherit_from_last_sentence = 'inherit_from_last_sentence'
    only_inherit_property = 'only_inherit_property'
    only_inherit_domain = 'only_inherit_domain'
    no_inherit = 'no_inherit'
    chitchat = 'chitchat'
    query_product = 'query_product'
    domain_defination = 'domain_defination'
    pure_domain_name = 'pure_domain_name'
    bottom_no_inherit = 'bottom_no_inherit'


class ContextMap(object):
    __dict__ = {ContextNames.domain.value: 1, ContextNames.property.value: 1}

    def __init__(self):
        pass


class ResponseCategory(Enum):
    preprocess = 'preprocess'
    rewrite = 'rewrite'
    wrong_url_field = 'wrong_url_field'


class SymbolRepresentMap(Enum):
    job = 'b'
    num = 'a'


class InteractionNames(Enum):
    curstrabbrev = 'curstrabbrevinteraction'
    recomlastanswermultiproduct = 'recomlastanswermultiproduct'
    lastquestionmultiproduct = 'lastquestionmultiproduct'

class UserSlotsName(Enum):
    slots_question='slots_question'
    slots_answer='slots_answer'

_shared_strs_by_two_entity = ['保险']
_fufilled_part_str_missied={'分':'公司'}

debug = True
platform = sys.platform
_rds_slots_maintain_key = '|slots'
_key_only_question_jdpin_with = '|only_question'
_answer_type = 1
_expire_time = 21600
_threshold_num_rounds = 1000
_default_name_abbrev='产品词'
_flag_recomm_sent_pattern='|semantics_flag'

_key_kg_sentence_classificiation='missionType'
_value_kg_sentence_classificiation_recommendation='recommendation'