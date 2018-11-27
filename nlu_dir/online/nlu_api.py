import sys

sys.path.append('../')
import web
from online.utils.logdiy import mylog
import time
import json
flag_version='new'
if flag_version=='old':
    from online.response_manage_old import ResponseManage
elif flag_version=='new':
    from online.response_manage_new import ResponseManage
else:
    raise ValueError('flag_version 不正确')

urls = (
    '/nlu/(.*)', 'Query',
)
app = web.application(urls, globals())

class Query:
    _response_manage_class = ResponseManage()

    def POST(self, name):
        if not name:
            input = web.input(name=None)
            web.header('Content-Type', 'application/json,charset=UTF-8')
            return input.name

    def GET(self, name):
        # print('name==>',name)
        web.header('Content-Type', 'application/json,charset=UTF-8')
        ts=time.time()
        input_ = web.input(name=None)
        # for key,value in input_.items():
        #     print(key,value)
        # data_return={'status':0,'data':{},'msg':None}
        # print('input==>',input)
        _data_return = self._response_manage_class.distribute(name_in=name, input_in=input_)
        mylog.info('输入字段信息{}'.format(str(input_)))
        mylog.info('get 返回字段信息  {}\n'.format(str(_data_return)))
        cost_time=time.time()-ts
        mylog.info('此次请求耗时\t{}'.format(str(cost_time)))
        return json.dumps(_data_return)


if __name__ == "__main__":
    app.run()
