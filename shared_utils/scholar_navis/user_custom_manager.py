import re
import json
from typing import Union
from toolbox import get_conf

# 用户储存的数据的默认值
DEFAULT_USER_CUSTOM = {
    'API_KEY':'',
    'API_URL_REDIRECT':['',''], # openai的
    "ZHIPUAI_API_KEY":'',
    "DASHSCOPE_API_KEY":'',
    "MOONSHOT_API_KEY":'',
    "DEEPSEEK_API_KEY":'',
    'CUSTOM_API_KEY':'',
    'CUSTOM_REDIRECT':['',''],
    'CUSTOM_MODELS':[]
    
    }

# 目前还没有用到的api正则表达式判定
api_type_patterns ={
    'openai':r"sk-[a-zA-Z0-9]{48}$|sk-proj-[a-zA-Z0-9]{48}$|sess-[a-zA-Z0-9]{40}$",
    'azure':r"[a-zA-Z0-9]{32}$",
    'api2d':r"fk[a-zA-Z0-9]{6}-[a-zA-Z0-9]{32}$",
    'cohere':r"[a-zA-Z0-9]{40}$",
    'zhipu':r'^[a-zA-Z0-9]{32}\.[a-zA-Z0-9]{16}$',
    'short_openai':r"^sk-[a-zA-Z0-9]{32}$"
}

SUPPORT_API_PROVIDER = { 'OpenAI':'API_KEY',
                        '智谱':'ZHIPUAI_API_KEY',
                        '通义千问':'DASHSCOPE_API_KEY',
                        '月之暗面':'MOONSHOT_API_KEY',
                        '深度求索':'DEEPSEEK_API_KEY',
                        '自定义':'CUSTOM_API_KEY',
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
def get_api_key(user_custom_data:dict,provider_api_type,allow_get_config:bool = False) -> str | list[str] | bool:
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
        
    domain =  dict_.get(redirect_type,DEFAULT_USER_CUSTOM[redirect_type])[0].replace('\\','/')
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
    """获取url重定向 (openai)

    Args:
        user_custom_data (str): 用户自定义数据

    Returns:
        _type_: 自定义重定向 or 配置文件中的重定向
    """
    domain = get_url_redirect_domain(redirect_type,user_custom_data)
    path = get_url_redirect_path(redirect_type,user_custom_data)

    if domain[-1] == '/': domain = domain[:-1]
    if path[0] == '/':path = path[1:] 
        
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


    