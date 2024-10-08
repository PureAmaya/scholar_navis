import os
import yaml
from .const import SCHOLAR_NAVIS_ROOT_PATH


version_file_fp = os.path.join(SCHOLAR_NAVIS_ROOT_PATH,'version')
config_file_fp = os.path.join(SCHOLAR_NAVIS_ROOT_PATH,'config.yml')


VERSION = '1.0.0_release'

CONFIG = {
            'language_GPT_prefer':'简体中文',
            'language_display':'zh-Hans',
            'auto_clear_tmp':False,
            'auto_clear_summary_lib':False,
            #'auto_clear_gpt_log':False,
            'auto_clear_private_upload':False,
            'enable_simple_translator':False,
            'enable_pubmed_downloader':True,
            'enable_user_usage_log':False,
            'prioritize_use_AI_assistance':True
        }

SUPPORT_DISPLAY_LANGUAGE = {'zh-Hans','zh-Hant','en-US'}
GPT_SUPPORT_LAMGUAGE = ('简体中文','繁體中文','English','日本語','Français','Deutsch','Русский','العربية','Español')


def _load():
    
    try:
        with open(version_file_fp,'r',encoding='utf-8') as f:
            verison = f.read().strip()
    except:
        verison = ''
    
    
    if not os.path.exists(config_file_fp):
        return verison,CONFIG,True
    try:
        with open(config_file_fp,'r',encoding='utf-8') as f:
            config:dict = yaml.safe_load(f)
            # 获取字典中的实际键
            actual_keys = config.keys()
    except:return verison,CONFIG,True
        
    # 期望有的键
    expected_keys = CONFIG.keys()

    # 判断是否少键值
    missing_keys = any(expected_key not in actual_keys for expected_key in expected_keys)
    
    wrong_type = False
    
    # 使用默认值填充，顺便检查类型是否错误
    for expected_key in expected_keys:
        config[expected_key] = config.get(expected_key,CONFIG[expected_key])
        if type(config[expected_key]) is not type(CONFIG[expected_key]):
            config[expected_key] = CONFIG[expected_key]
            wrong_type = True
    
    return verison,config,wrong_type or missing_keys

def write_config():
    # 该插件的根目录
    with open(config_file_fp,'w',encoding='utf-8') as f:
        f.write(yaml.safe_dump(CONFIG))
        

VERSION,CONFIG,config_need_write = _load()
if config_need_write:write_config()