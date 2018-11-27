import jieba
import jieba.posseg as psg
class DependAnalysis(object):
    def __init__(self):
        self.needed_elems={'n','v','x'}
    def judge_complete(self,str_in):
        result=psg.lcut(str_in)
        # print(result)
        # r1=list(zip([list(item)[0] for item in result],[list(item)[1] for item in result]))
        r1=[list(item)[0] for item in result]
        r2=[list(item)[1] for item in result]
        # print(r1)
        # print(r2)
        counter=0
        for elem_needed_iter in self.needed_elems:
            for elem_test_iter in r2:
                if elem_needed_iter in elem_test_iter:
                    counter+=1
        # print('-*- '*5)
        return counter>1
if __name__=='__main__':
    str_in=['的是什么','投保年龄是什么','是多少','可以申请吗','赔多少','的年龄呢','是多久']
    da=DependAnalysis()

    for str_iter in str_in:
        r=da.judge_complete(str_iter)
        print(r)