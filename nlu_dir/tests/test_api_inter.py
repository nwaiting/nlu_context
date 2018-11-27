import requests
url='http://localhost:9047/nlu/rewrite'


while True:
    question = input('输入question')
    jdpin = input('输入 jdpin')
    params = {'question': question, 'session': jdpin,'jdpin':jdpin}
    result = requests.get(url=url, params=params)
    print('result==>\n', result.json())
