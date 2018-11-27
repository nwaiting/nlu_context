class FieldCheck(object):
    def __init__(self):
        pass
    def _check_normal_str(self,str_in):
        return True
class PreprocessCheck(FieldCheck):
    def __init__(self):
        super(PreprocessCheck,self).__init__()
    def check(self,input):
        if 'question' not in input:
            return False,'缺失 question 字段'
        return self._check_normal_str(input.question),'ok'
class RewriteCheck(FieldCheck):
    def __init__(self):
        super(RewriteCheck,self).__init__()
    def check(self,input):
        #.question,input.words_segment,input.jdpin
        if 'question' not in input:
            return False,'缺失 question 字段'
        # elif 'words_segment' not in input:
        #     return False,'缺失 words_segemtn 字段'
        elif 'session' not in input:
            return False,'缺失 session 字段'
        return True,'ok'