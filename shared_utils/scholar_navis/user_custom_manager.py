'''
Author: scholar_navis@PureAmaya
'''

import re
from functools import lru_cache
import json
from typing import Literal, Union
from shared_utils.config_loader import read_single_conf_with_lru_cache


class callable_dict(dict):
    def __call__(self,key):
        return self[key]


# 用户储存的数据的默认值
DEFAULT_USER_CUSTOM = {
    'API_KEY':'',
    'API_URL_REDIRECT':['',''], # openai的
    'XAI_API_KEY':'',
    "ZHIPUAI_API_KEY":'',
    "DASHSCOPE_API_KEY":'',
    "MOONSHOT_API_KEY":'',
    "DEEPSEEK_API_KEY":'',
    'CUSTOM_API_KEY':'',
    'CUSTOM_REDIRECT':['',''],
    'CUSTOM_MODELS':[]
    
    }


SUPPORT_API_PROVIDER = { 'OpenAI':'API_KEY',
                        'Grok':'XAI_API_KEY',
                        '智谱(zhipu/glm)':'ZHIPUAI_API_KEY',
                        '通义千问(dashscope/qwen)':'DASHSCOPE_API_KEY',
                        '月之暗面(moonshot)':'MOONSHOT_API_KEY',
                        '深度求索(deepseek)':'DEEPSEEK_API_KEY',
                        '自定义(custom)':'CUSTOM_API_KEY',
                        }

'''用户自己自定义的key，不影响config中的设置'''

@staticmethod
def _load_dict_from_str(txt:str):
    if txt:a = json.loads(txt)
    else: a = DEFAULT_USER_CUSTOM
    if not a: a = DEFAULT_USER_CUSTOM
    elif type(a) is not dict:a = DEFAULT_USER_CUSTOM
    return a
    
@staticmethod
def get_api_key(user_custom_data:callable_dict,
                provider_api_type:Literal['API_KEY', 'ZHIPUAI_API_KEY', 'DASHSCOPE_API_KEY', 'MOONSHOT_API_KEY', 'DEEPSEEK_API_KEY'],allow_get_config:bool = False) -> str | list[str] | bool:
    """获取其他提供商的api-key（含自定义的API）

    Args:
        user_custom_data (dict): 用户自定义数据
        provider (str): key的提供商
        allow_get_config (bool, optional): 允许获取默认值吗（如有）. Defaults to False.

    Returns:
        str | list[str] | bool: _description_
    """
    assert provider_api_type in DEFAULT_USER_CUSTOM.keys()
    a = user_custom_data.get(provider_api_type,DEFAULT_USER_CUSTOM[provider_api_type])
    if not allow_get_config or a:return a
    else:return get_conf(provider_api_type)


@staticmethod
def get_url_redirect_domain(redirect_type:str,user_custom_data:Union[str,dict]):
    dict_ = {}
    if type(user_custom_data) is dict:dict_ = user_custom_data
    else:dict_ = _load_dict_from_str(user_custom_data)
        
    domain =  dict_
    if domain:return domain
    else: return 'https://api.openai.com'
        
@staticmethod
def get_url_redirect_path(redirect_type:str,user_custom_data:Union[str,dict]):
    dict_ = {}
    if type(user_custom_data) is dict:dict_ = user_custom_data
    else:dict_ = _load_dict_from_str(user_custom_data)
        
    path = dict_.get(redirect_type,DEFAULT_USER_CUSTOM[redirect_type])[1].replace('\\','/')
    if path:return path
    else:return 'v1/chat/completions'

@staticmethod
def get_url_redirect(redirect_type:str,user_custom_data:dict) -> str:
    """适用于兼容OpenAI的url重定向（支持自定义模型），不支持ollama

    Args:
        redirect_type (str): 重定向API类型，'API_URL_REDIRECT'或'CUSTOM_REDIRECT'
        user_custom_data (dict): _description_

    Returns:
        str: url重定向（空值的话，brigde那边会读取默认值）
    """
    domain :str = user_custom_data.get(redirect_type,DEFAULT_USER_CUSTOM[redirect_type])[0].replace('\\','/')
    path:str = user_custom_data.get(redirect_type,DEFAULT_USER_CUSTOM[redirect_type])[1].replace('\\','/')

    if not domain and not path:
        domain, path = splice_config_url_direct()
    else:
        try:
            if domain[-1] == '/': domain = domain[:-1]
        except:domain = 'https://api.openai.com'
        try:
            if path[0] == '/':path = path[1:] 
        except:path = 'v1/chat/completions'
    
    return f'{domain}/{path}'

@staticmethod
def set_api_key(user_custom_data:dict,key:str,value):
    """设定api_key

    Args:
        user_custom_data (str): 用户自定义数据
        key (str): 键值
        value (_type_): 值

    Returns:
        str: （修改后的）str形式的json
    """
    if key in SUPPORT_API_PROVIDER.keys():
        key = SUPPORT_API_PROVIDER[key]
    
    assert key in DEFAULT_USER_CUSTOM.keys()
    
    if key == 'CUSTOM_MODELS':# 这个是list
        list_ = value.split('\n')
        for i,v in enumerate(list_):
            if v.startswith('one-api-'):list_[i] = v[8:].strip()
            else:list_[i] = v.strip()
        value = list_
        del list_
    if 'REDIRECT' in key:
        raise TypeError('Please use set_url_redirect')
        
    else: # 一般情况下都是str
        if value:value = value.strip() 
        
    user_custom_data.update({key: value})
    return user_custom_data
    
@staticmethod
def set_url_redirect(user_custom_data:dict,redirect_type:str,domain:str,path:str):
    """设定URL重定向

    Args:
        user_custom_data (str):用户自定义数据
        value (str): 值

    Returns:
        str: （修改后的）str形式的json
    """
    
    if domain:domain = domain.strip()
    if path:path = path.strip()
    user_custom_data.update({redirect_type:[domain,path]})
    return user_custom_data

@staticmethod
def vaild_api_key(provider):
    pass
            
# chatgpt和azure用的是llm_kwargs['api_key']，也是获取的cookies['api_key']


# 直接从toolbox那边拿来的（
@lru_cache(maxsize=128)
def get_conf(*args):
    """
    本项目的所有配置都集中在config.py中。 修改配置有三种方法，您只需要选择其中一种即可：
        - 直接修改config.py
        - 创建并修改config_private.py
        - 修改环境变量（修改docker-compose.yml等价于修改容器内部的环境变量）

    注意：如果您使用docker-compose部署，请修改docker-compose（等价于修改容器内部的环境变量）
    """
    res = []
    for arg in args:
        r = read_single_conf_with_lru_cache(arg)
        res.append(r)
    if len(res) == 1: return res[0]
    return res


def splice_config_url_direct():
    redirect_url_config: str = get_conf('API_URL_REDIRECT').get('https://api.openai.com/v1/chat/completions', '')
    pattern = r'^(https?://)?([^/]+)(/.*)?$'
    
    default_domain = 'https://api.openai.com'
    default_path = 'v1/chat/completions'
    
    try:
        if redirect_url_config.startswith('https://'):
            match = re.match(pattern, redirect_url_config)
            if match:
                domain = f"https://{match.group(2)}" if match.group(2) else default_domain
                path = match.group(3) if match.group(3) else default_path
                return domain, path
    except Exception as e:
        print(f"错误发生: {e}")
    
    # 如果没有匹配或发生错误，返回默认值
    return default_domain, default_path

