import os
import yaml
from .article_library_ctrl import SCHOLAR_NAVIS_ROOT_PATH


version_file_fp = os.path.join(SCHOLAR_NAVIS_ROOT_PATH,'version')
config_file_fp = os.path.join(SCHOLAR_NAVIS_ROOT_PATH,'config.yml')


VERSION = '1.0.0_release'

CONFIG = {
            'GPT_prefer_language':'简体中文',
            'display_language':'zh-Hans',
        }

SUPPORT_DISPLAY_LANGUAGE = {'zh-Hans','zh-Hant','en-US'}
GPT_SUPPORT_LAMGUAGE = ('简体中文','繁體中文','English','日本語','Français','Deutsch','Русский','العربية','Español')


def _load():
    
    try:
        with open(version_file_fp,'r') as f:
            verison = f.read().strip()
    except:
        verison = ''
    
    try:
        with open(config_file_fp,'r') as f:
            config = yaml.safe_load(f)
            
            if not config['GPT_prefer_language'] in GPT_SUPPORT_LAMGUAGE or not config['display_language'] in SUPPORT_DISPLAY_LANGUAGE:
                raise RuntimeError('Error config. Use default settings')

    except:
            write_config()
            config = CONFIG
            
    return verison,config

def write_config():
    # 该插件的根目录
    with open(config_file_fp,'w') as f:
        f.write(yaml.safe_dump(CONFIG))
        

VERSION,CONFIG = _load()