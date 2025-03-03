'''
Original Author: gpt_academic@binary-husky

Modified by PureAmaya on 2025-02-21
- Compatible with DeepSeek's inference model(R1)

Modified by PureAmaya on 2024-12-28
- Added support for API-key type determination in custom models  
- Added internationalization
'''

import re
import os
from shared_utils.scholar_navis.multi_lang import _

pj = os.path.join
default_user_name = 'default_user'

def _is_openai_model(model_name):
    model_name = model_name.strip().lower()
    return model_name == 'o1' or model_name == 'o3' or model_name.startswith('gpt-') or model_name.startswith('o1-') or model_name.startswith('o3-')

def is_openai_api_key(key):
    CUSTOM_API_KEY_PATTERN = '' # get_conf('CUSTOM_API_KEY_PATTERN') 暂时无用
    if len(CUSTOM_API_KEY_PATTERN) != 0:
        API_MATCH_ORIGINAL = re.match(CUSTOM_API_KEY_PATTERN, key)
    else:
        API_MATCH_ORIGINAL = re.match(r"sk-[a-zA-Z0-9_-]+|sess-[a-zA-Z0-9]", key)
    return bool(API_MATCH_ORIGINAL)


def is_azure_api_key(key):
    API_MATCH_AZURE = re.match(r"[a-zA-Z0-9]{32}$", key)
    return bool(API_MATCH_AZURE)


def is_api2d_key(key):
    API_MATCH_API2D = re.match(r"fk[a-zA-Z0-9]{6}-[a-zA-Z0-9]{32}$", key)
    return bool(API_MATCH_API2D)


def is_cohere_api_key(key):
    API_MATCH_AZURE = re.match(r"[a-zA-Z0-9]{40}$", key)
    return bool(API_MATCH_AZURE)


def is_any_api_key(key):
    if ',' in key:
        keys = key.split(',')
        for k in keys:
            if is_any_api_key(k): return True
        return False
    else:
        return is_openai_api_key(key) or is_api2d_key(key) or is_azure_api_key(key) or is_cohere_api_key(key)


def what_keys(keys):
    avail_key_list = {'OpenAI Key': 0, "Azure Key": 0, "API2D Key": 0}
    key_list = keys.split(',')

    for k in key_list:
        if is_openai_api_key(k):
            avail_key_list['OpenAI Key'] += 1

    for k in key_list:
        if is_api2d_key(k):
            avail_key_list['API2D Key'] += 1

    for k in key_list:
        if is_azure_api_key(k):
            avail_key_list['Azure Key'] += 1

    return _("检测到： OpenAI Key {} 个, Azure Key {} 个, API2D Key {} 个").format(avail_key_list['OpenAI Key'],avail_key_list['Azure Key'],avail_key_list['API2D Key'])


def select_api_key(keys, llm_model):
    import random
    avail_key_list = []
    key_list = keys.split(',')

    if _is_openai_model(llm_model) or llm_model.startswith('one-api-') or llm_model.startswith('custom-'):
        for k in key_list:
            if is_openai_api_key(k): avail_key_list.append(k)
            if is_api2d_key(k): avail_key_list.append(k) # api2d用的不是标准openai，自定义的时候会找不到api

    if llm_model.startswith('api2d-'):
        for k in key_list:
            if is_api2d_key(k): avail_key_list.append(k)

    if llm_model.startswith('azure-'):
        for k in key_list:
            if is_azure_api_key(k): avail_key_list.append(k)

    if llm_model.startswith('cohere-'):
        for k in key_list:
            if is_cohere_api_key(k): avail_key_list.append(k)

    if len(avail_key_list) == 0:
        raise RuntimeError(_("您提供的api-key不满足要求，不包含任何可用于{}的api-key。您可能选择了错误的模型或请求源（左上角更换模型菜单中可切换其他模型或请求源）").format(llm_model))

    api_key = random.choice(avail_key_list) # 随机负载均衡
    return api_key
