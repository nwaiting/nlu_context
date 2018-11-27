import requests
import random
import time

# url='http://localhost:9047/nlu/rewrite'
url='http://localhost:9100/nlu/rewrite'
# url='http://10.240.68.106:9047/nlu/rewrite'
def t1():
    question='安行万里你好歹'
    jdpin='tt13'
    session='session_tt13'
    params={'question':question,'session':session,'jdpin':jdpin}
    result=requests.get(url=url,params=params).json()
    print('result==>\n',result)
    assert '安行万里境外险' in result['data']['label2entities_cur_dict']['domain']
    assert result['data']['words_with_context']==['安行万里境外险', '你', '好歹']
def t2():
    jdpin_='tt'
    params={'question':'','session':''}

    two_rounds_list=[
        [
            '安康福瑞两全保险条款中的毒品是什么意思',
            '那它附加险的满期日是什么时候',
            '安联安康福瑞两全保险B款附加险的满期日是什么时候',
        ],
        [
            ' 安行万里退保条件',
            '安行万里的退保流程是啥',
            '安联安康无忧医疗保险有等待期吗',


        ],
        [
            '给我看一下安康无忧的保险计划保险事故',
            '给我看一下安康无忧的计划表',
            '安联安康无忧医疗保险等待期是多久',
        ],
        [
            '随心飞的投保年龄',
            '安联安康无忧医疗保险等待期是多久',
        ],
        [
            '随心飞的投保年龄',
            '安联安康无忧医疗保险等待期是多久',
        ],
    ]

    jdpin_cur=jdpin_+str(random.randint(1000,2000))
    ts=time.time()
    counter=0
    for one_round_iter in two_rounds_list:
        params['question']=one_round_iter[0]
        params['session']='session_'+jdpin_cur
        params['jdpin']=jdpin_cur
        t1=time.time()
        result01 = requests.get(url=url, params=params).json()
        print(time.time()-t1)
        # print(result01['data']['words_with_context'])

        params['question']=one_round_iter[1]
        # params['jdpin']=jdpin_cur
        # params['test_field']='test_field'

        t2=time.time()
        result02 = requests.get(url=url, params=params).json()
        print(time.time()-t2)
        if counter==0:
            print('result02==>\n',result02)
            print('-*- '*5)
            print(result02['data']['words_with_context'])
            assert ''.join(result02['data']['words_with_context'])==one_round_iter[2]
        counter+=2
    time_cost=time.time()-ts
    print(time_cost,counter)
if __name__=='__main__':
    t1()
    t2()
