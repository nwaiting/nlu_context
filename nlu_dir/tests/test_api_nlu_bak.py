import requests
import random
url='http://localhost:9047/nlu/rewrite'
def t1():
    question='安行万里你好歹'
    jdpin='tt13'
    params={'question':question,'session':jdpin,'jdpin':jdpin}
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
    ]

    jdpin_cur=jdpin_+str(random.randint(1000,2000))
    for one_round_iter in two_rounds_list:
        params['question']=one_round_iter[0]
        params['session']=jdpin_cur
        result01 = requests.get(url=url, params=params).json()

        params['question']=one_round_iter[1]
        params['session']=jdpin_cur
        params['jdpin']=jdpin_cur
        # params['test_field']='test_field'
        result02 = requests.get(url=url, params=params).json()
        print(result02['data']['words_with_context'])
        assert ''.join(result02['data']['words_with_context'])==one_round_iter[2]

if __name__=='__main__':
    t1()
    t2()