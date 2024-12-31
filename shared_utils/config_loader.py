import importlib
import time
import os
from functools import lru_cache
from shared_utils.colorful import print亮红, print亮绿, print亮蓝

pj = os.path.join
default_user_name = 'default_user'

def read_env_variable(arg, default_value):
    """
    环境变量可以是 `GPT_ACADEMIC_CONFIG`(优先)，也可以直接是`CONFIG`
    例如在windows cmd中，既可以写：
        set USE_PROXY=True
        set API_KEY=sk-j7caBpkRoxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        set proxies={"http":"http://127.0.0.1:10085", "https":"http://127.0.0.1:10085",}
        set AVAIL_LLM_MODELS=["gpt-3.5-turbo", "chatglm"]
        set AUTHENTICATION=[("username", "password"), ("username2", "password2")]
    也可以写：
        set GPT_ACADEMIC_USE_PROXY=True
        set GPT_ACADEMIC_API_KEY=sk-j7caBpkRoxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        set GPT_ACADEMIC_proxies={"http":"http://127.0.0.1:10085", "https":"http://127.0.0.1:10085",}
        set GPT_ACADEMIC_AVAIL_LLM_MODELS=["gpt-3.5-turbo", "chatglm"]
        set GPT_ACADEMIC_AUTHENTICATION=[("username", "password"), ("username2", "password2")]
    """
    arg_with_prefix = "GPT_ACADEMIC_" + arg
    if arg_with_prefix in os.environ:
        env_arg = os.environ[arg_with_prefix]
    elif arg in os.environ:
        env_arg = os.environ[arg]
    else:
        raise KeyError
    print(f"[ENV_VAR] Loding environment variable: {arg}, default value: {default_value} --> actual value: {env_arg}")
    try:
        if isinstance(default_value, bool):
            env_arg = env_arg.strip()
            if env_arg == 'True': r = True
            elif env_arg == 'False': r = False
            else: print('Enter True or False, but have:', env_arg); r = default_value
        elif isinstance(default_value, int):
            r = int(env_arg)
        elif isinstance(default_value, float):
            r = float(env_arg)
        elif isinstance(default_value, str):
            r = env_arg.strip()
        elif isinstance(default_value, dict):
            r = eval(env_arg)
        elif isinstance(default_value, list):
            r = eval(env_arg)
        elif default_value is None:
            assert arg == "proxies"
            r = eval(env_arg)
        else:
            print亮红(f"[ENV_VAR] environment variable {arg} not support! ")
            raise KeyError
    except:
        print亮红(f"[ENV_VAR] environment variable {arg} loading failed! ")
        raise KeyError(f"[ENV_VAR] environment variable {arg} loading failed! ")

    print亮绿(f"[ENV_VAR] environment variable {arg} loading success.")
    return r


@lru_cache(maxsize=128)
def read_single_conf_with_lru_cache(arg):
    # from shared_utils.key_pattern_manager import is_any_api_key
    try:
        # 优先级1. 获取环境变量作为配置
        default_ref = getattr(importlib.import_module('config'), arg) # 读取默认值作为数据类型转换的参考
        r = read_env_variable(arg, default_ref)
    except:
        try:
            # 优先级2. 获取config_private中的配置
            r = getattr(importlib.import_module('config_private'), arg)
        except:
            # 优先级3. 获取config中的配置
            r = getattr(importlib.import_module('config'), arg)

    return r


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


def set_conf(key, value):
    from toolbox import read_single_conf_with_lru_cache
    read_single_conf_with_lru_cache.cache_clear()
    get_conf.cache_clear()
    os.environ[key] = str(value)
    altered = get_conf(key)
    return altered


def set_multi_conf(dic):
    for k, v in dic.items(): set_conf(k, v)
    return
