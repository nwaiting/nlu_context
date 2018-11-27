import os
import platform
import shutil
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
upper_dirpath = os.path.join(os.path.dirname(project_path), 'upper_dir')
nlu_log_dirpath = os.path.join(os.path.dirname(project_path), 'nlu_log_dir')
data_dirpath = os.path.join(project_path, 'data')
files_dirpath = os.path.join(data_dirpath, 'userdict')
entity_dirpath = os.path.join(files_dirpath, 'entity')
pattern_classification_dirpath=os.path.join(files_dirpath,'pattern_classification')
user = 'longzai'
import time

class PathUtil(object):
    def __init__(self):
        pass
    @property
    def stopwords_filepath(self):
        # path=os.path.join(files_dirpath,'stop_words.txt')
        path=os.path.join(files_dirpath,'stopWord_new.txt')
        return path
    @property
    def diy_words_filepath(self):
        path = os.path.join(files_dirpath, 'jieba_UserWord_new.txt')
        return path

    @property
    def similiar_words_filepath(self):
        path = os.path.join(files_dirpath, 'similary_word.txt')
        return path

    @property
    def domain_filepath(self):
        path = os.path.join(entity_dirpath, 'entity_domain.txt')
        return path

    @property
    def intent_filepath(self):
        path = os.path.join(entity_dirpath, 'entity_intent.txt')
        return path

    @property
    def property_filepath(self):
        path = os.path.join(entity_dirpath, 'entity_property.txt')
        return path

    @property
    def company_domain_filepath(self):
        path = os.path.join(entity_dirpath, 'company_domain.txt')
        return path

    @property
    def company_property_filepath(self):
        path = os.path.join(entity_dirpath, 'company_property.txt')
        return path
    @property
    def fufilled_company_domain_filepath(self):
        path=os.path.join(entity_dirpath,'fufilled_company_domain.txt')
        return path
    @property
    def similiar_sentences_filepath(self):
        path=os.path.join(entity_dirpath,'similiar_sentences.txt')
        return path
    @property
    def prounoun_filepath(self):
        path = os.path.join(entity_dirpath, 'finger_prouns.txt')
        return path

    @property
    def compare_pronoun_filepath(self):
        path = os.path.join(entity_dirpath, 'compare_pronouns.txt')
        return path

    @property
    def get_logging_config(self):
        if platform.node() == 'JRA1PF18UCM8':
            confpath = os.path.join(project_path, 'config', 'local_logging.config')
        else:
            confpath = os.path.join(project_path, 'config', 'logging.config')
        print('confpath===>\t',confpath)
        return confpath
    @property
    def logfilepath(self):
        rq = time.strftime('%Y%m%d', time.localtime(time.time()))
        logfilename = rq + '.log'
        if platform.node() == 'JRA1PF18UCM8':
            confdir=os.path.join(project_path,'nlu_log_dir')
            confpath = os.path.join(confdir,logfilename)
        else:
            # confpath = os.path.join(project_path, 'config', 'logging.config')
            confdir='/export/longzai/nlu_log/nlu_basic_logdir'
            confpath=os.path.join(confdir,logfilename)
        # print('confpath===>\t',confpath)
        if not os.path.exists(confdir):
            os.mkdir(confdir)
        return confpath
    @property
    def get_multi_corpus_file(self):
        if platform.node() == 'JRA1PF18UCM8':
            save_tfidf_single_dir = os.path.join(upper_dirpath, 'train_corpus', 'multi_merge.txt')
            if not os.path.exists(save_tfidf_single_dir):
                os.mkdir(save_tfidf_single_dir)
        else:
            #
            save_tfidf_single_dir = '/export/chenxiulong/chatlib/poc_anlian/multi_merge.txt'
        return save_tfidf_single_dir

    @property
    def get_save_tfidf_multi_dir(self):
        if platform.node() == 'JRA1PF18UCM8':
            save_tfidf_multi_dir = os.path.join(upper_dirpath, 'models', 'bot_factory_multi')
            if not os.path.exists(save_tfidf_multi_dir):
                os.mkdir(save_tfidf_multi_dir)
        else:
            save_tfidf_multi_dir = '/export/chenxiulong/modelFile/bot_factory_multi'
        return save_tfidf_multi_dir

    @property
    def get_single_corpus_file(self):
        if platform.node() == 'JRA1PF18UCM8':
            single_corpus_file = os.path.join(upper_dirpath, 'train_corpus', 'single_merge.txt')
        else:
            single_corpus_file = '/export/chenxiulong/chatlib/poc_anlian/single_merge.txt'
        return single_corpus_file

    @property
    def get_single_save_model_dir(self):
        if platform.node() == 'JRA1PF18UCM8':
            single_save_model_dir = os.path.join(upper_dirpath, 'models', 'bot_factory_single')
        else:
            single_save_model_dir = '/export/chenxiulong/modelFile/bot_factory_single'
        return single_save_model_dir
    @property
    def get_pattern_with_represent_yamlpath(self):
        yamlpath=os.path.join(pattern_classification_dirpath,'pattern_with_represent.yaml')
        return yamlpath
    @property
    def get_represent_words_map(self):
        filepath=os.path.join(pattern_classification_dirpath,'represent_words_map.txt')
        return filepath
    @property
    def char_represent_map_file(self):
        filepath = os.path.join(files_dirpath, 'represent_chars_map.txt')
        return filepath
    @property
    def reback_file(self):
        filepath=os.path.join(files_dirpath,'reback_str.txt')
        return filepath
    @property
    def abbreviations2entity_words_filepath(self):
        filepath=os.path.join(files_dirpath,'abbreviations2entity.txt')
        return filepath
    @property
    def files_dirpath(self):
        # print('files_dirpath==>',files_dirpath)
        return files_dirpath
# if not os.path.exists(nlu_log_dirpath):
#     os.mkdir(nlu_log_dirpath)