import time
import logging
import os
from common.pathutil import PathUtil

class MyLog(object):
    def __init__(self):
        logfile=PathUtil().logfilepath
        # log_path = os.path.dirname(os.getcwd()) + '/logs/'
        # if not os.path.exists(log_path):
        #     os.mkdir(log_path)
        rq = time.strftime('%Y%m%d', time.localtime(time.time()))
        logfilename=rq + '.log'
        # 第一步，创建一个logger
        logger = logging.getLogger()
        self.logger=logger
        logger.setLevel(logging.INFO)  # Log等级总开关
        # 第二步，创建一个handler，用于写入日志文件
        # log_name = os.path.join(log_path,logfilename )
        # logfile = log_name
        fh = logging.FileHandler(logfile, mode='w',encoding='utf-8')
        fh.setLevel(logging.INFO)  # 输出到file的log等级的开关
        # 第三步，定义handler的输出格式
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        fh.setFormatter(formatter)
        # 第四步，将logger添加到handler里面
        logger.addHandler(fh)
    def info(self,str_in):
        self.logger.info(str_in)
    def debug(self,str_in):
        self.logger.debug(str_in)
        self.logger.info(str_in)
    def error(self,str_in):
        self.logger.error(str_in)
mylog=MyLog()
if __name__=='__main__':
    mylog=MyLog()
    mylog.info('你好啊')
