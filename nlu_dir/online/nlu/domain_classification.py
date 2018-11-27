import collections
import re
from online.nlu.entity import Entity
from online.utils.nameutil import FieldClassifyNames as dcnames


class DomainClassification(object):
    _entity_class = Entity()
    _pattern_classification={dcnames.company.value:re.compile('公司')}
    def __init__(self):
        self._preload()

    def _preload(self):
        self._domain2patterns = self._get_patterns()

    def _get_patterns(self):
        return self._entity_class.get_domain2pattern_dict

    def classify(self, str_in):
        domain2matches = collections.defaultdict(list)
        for domain_iter, pattern_iter in self._domain2patterns.items():
            result_findall = pattern_iter.findall(str_in)
            if result_findall:
                domain2matches[domain_iter] = result_findall
        if domain2matches:
            domain2matches_sorted = sorted(domain2matches.items(), key=lambda x: (len(x[1]), len(x[1][0])),
                                           reverse=True)
            return domain2matches_sorted[0][0]
        for classiciation_iter,pattern_iter in self._pattern_classification.items():
            if pattern_iter.search(str_in):
                return classiciation_iter
        return dcnames.common.value
