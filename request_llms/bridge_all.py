'''
Original Author: gpt_academic@binary-husky

Modified by PureAmaya on 2025-04-11
- Add the Grok3 series models.
- Updated information for the Gemini series models and added support for customization.
- Compatible with the new multilingual feature.

Modified by PureAmaya on 2025-03-10
- Add model: qwq-plus, claude-3-7-sonnet-latest

Modified by PureAmaya on 2025-02-27
- Remove models: qianfan, taichu, newbing, yi, spark
- Add model: grok-2, gpt-4.5-preview
- Update most of the model's information to the latest status.
- Due to the current preference for text-based models, some multimodal models have not been included.
- Fix: When the history is an odd number (e.g., 1), historical records are missing when requesting LLM.
- Add a 1-second delay to predict_no_ui_long_connection to address the issue where certain services can only be accessed once per second.
- Since not all requests pass through the entry point (regular conversations do), a null input correction has been specifically added for predict_no_ui_long_connection.
- Add validation for history (must be a list)

Modified by PureAmaya on 2024-12-28
- Compatible with custom API functionality on the web.
- Add localization support.
'''


"""
    该文件中主要包含2个函数，是所有LLM的通用接口，它们会继续向下调用更底层的LLM模型，处理多模型并行等细节

    不具备多线程能力的函数：正常对话时使用，具备完备的交互功能，不可多线程
    1. predict(...)

    具备多线程调用能力的函数：在函数插件中被调用，灵活而简洁
    2. predict_no_ui_long_connection(...)
"""
import tiktoken
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from toolbox import trimmed_format_exc,update_ui
from shared_utils.text_mask import apply_gpt_academic_string_mask
from shared_utils.map_names import read_one_api_model_name
from shared_utils.config_loader import get_conf
from multi_language import init_language
import threading, time, copy
from .scholar_navis.model_info import model_info_class

from .bridge_chatgpt import predict_no_ui_long_connection as chatgpt_noui
from .bridge_chatgpt import predict as chatgpt_ui

from .bridge_chatglm import predict_no_ui_long_connection as chatglm_noui
from .bridge_chatglm import predict as chatglm_ui

from .bridge_chatglm3 import predict_no_ui_long_connection as chatglm3_noui
from .bridge_chatglm3 import predict as chatglm3_ui

from .bridge_zhipu import predict_no_ui_long_connection as zhipu_noui
from .bridge_zhipu import predict as zhipu_ui

from .bridge_cohere import predict as cohere_ui
from .bridge_cohere import predict_no_ui_long_connection as cohere_noui

from .oai_std_model_template import get_predict_function


colors = ['#FF00FF', '#00FFFF', '#FF0000', '#990099', '#009999', '#990044']

_= init_language

class LazyloadTiktoken(object):



    def __init__(self, model):
        self.model = model

    @staticmethod
    @lru_cache(maxsize=128)
    def get_encoder(model):

        print(_('正在加载tokenizer，如果是第一次运行，可能需要一点时间下载参数'))
        tmp = tiktoken.encoding_for_model(model)
        print(_('加载tokenizer完毕'))
        return tmp

    def encode(self, *args, **kwargs):
        encoder = self.get_encoder(self.model)
        return encoder.encode(*args, **kwargs)

    def decode(self, *args, **kwargs):
        encoder = self.get_encoder(self.model)
        return encoder.decode(*args, **kwargs)

# Endpoint 重定向
API_URL_REDIRECT, AZURE_ENDPOINT, AZURE_ENGINE = get_conf("API_URL_REDIRECT", "AZURE_ENDPOINT", "AZURE_ENGINE")
openai_endpoint = "https://api.openai.com/v1/chat/completions"
api2d_endpoint = "https://openai.api2d.net/v1/chat/completions"
newbing_endpoint = "wss://sydney.bing.com/sydney/ChatHub"
gemini_endpoint = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
claude_endpoint = "https://api.anthropic.com/v1/messages"
cohere_endpoint = "https://api.cohere.ai/v1/chat"
ollama_endpoint = "http://localhost:11434/api/chat"
yimodel_endpoint = "https://api.lingyiwanwu.com/v1/chat/completions"
deepseekapi_endpoint = "https://api.deepseek.com/v1/chat/completions"

if not AZURE_ENDPOINT.endswith('/'): AZURE_ENDPOINT += '/'
azure_endpoint = AZURE_ENDPOINT + f'openai/deployments/{AZURE_ENGINE}/chat/completions?api-version=2023-05-15'
# 兼容旧版的配置
try:
    API_URL = get_conf("API_URL")
    if API_URL != "https://api.openai.com/v1/chat/completions":
        openai_endpoint = API_URL
        print(_("警告！API_URL配置选项将被弃用，请更换为API_URL_REDIRECT配置"))
except:
    pass
# 新版配置
if openai_endpoint in API_URL_REDIRECT: openai_endpoint = API_URL_REDIRECT[openai_endpoint]
if api2d_endpoint in API_URL_REDIRECT: api2d_endpoint = API_URL_REDIRECT[api2d_endpoint]
if newbing_endpoint in API_URL_REDIRECT: newbing_endpoint = API_URL_REDIRECT[newbing_endpoint]
if gemini_endpoint in API_URL_REDIRECT: gemini_endpoint = API_URL_REDIRECT[gemini_endpoint]
if claude_endpoint in API_URL_REDIRECT: claude_endpoint = API_URL_REDIRECT[claude_endpoint]
if cohere_endpoint in API_URL_REDIRECT: cohere_endpoint = API_URL_REDIRECT[cohere_endpoint]
if ollama_endpoint in API_URL_REDIRECT: ollama_endpoint = API_URL_REDIRECT[ollama_endpoint]
if yimodel_endpoint in API_URL_REDIRECT: yimodel_endpoint = API_URL_REDIRECT[yimodel_endpoint]
if deepseekapi_endpoint in API_URL_REDIRECT: deepseekapi_endpoint = API_URL_REDIRECT[deepseekapi_endpoint]

# 获取tokenizer
tokenizer_gpt35 = LazyloadTiktoken("gpt-3.5-turbo")
tokenizer_gpt4 = LazyloadTiktoken("gpt-4")
get_token_num_gpt35 = lambda txt: len(tokenizer_gpt35.encode(txt, disallowed_special=()))
get_token_num_gpt4 = lambda txt: len(tokenizer_gpt4.encode(txt, disallowed_special=()))

# 开始初始化模型
AVAIL_LLM_MODELS, LLM_MODEL = get_conf("AVAIL_LLM_MODELS", "LLM_MODEL")
AVAIL_LLM_MODELS = AVAIL_LLM_MODELS + [LLM_MODEL]


# -=-=-=-=-=-=- 以下这部分是最早加入的最稳定的模型 -=-=-=-=-=-=-
model_info = {
    # openai
    "gpt-4.5-preview": {
        "fn_with_ui": chatgpt_ui,
        "fn_without_ui": chatgpt_noui,
        "endpoint": openai_endpoint,
        "max_token": 128000,
        "tokenizer": tokenizer_gpt4,
        "token_cnt": get_token_num_gpt4,
    },


    "gpt-4o": {
        "fn_with_ui": chatgpt_ui,
        "fn_without_ui": chatgpt_noui,
        "endpoint": openai_endpoint,
        "max_token": 128000,
        "tokenizer": tokenizer_gpt4,
        "token_cnt": get_token_num_gpt4,
    },

    "gpt-4o-mini": {
        "fn_with_ui": chatgpt_ui,
        "fn_without_ui": chatgpt_noui,
        "endpoint": openai_endpoint,
        "max_token": 128000,
        "tokenizer": tokenizer_gpt4,
        "token_cnt": get_token_num_gpt4,
    },

    "o1": {
        "fn_with_ui": chatgpt_ui,
        "fn_without_ui": chatgpt_noui,
        "endpoint": openai_endpoint,
        "max_token": 200000,
        "tokenizer": tokenizer_gpt4,
        "token_cnt": get_token_num_gpt4,
    },

    "o1-mini": {
        "fn_with_ui": chatgpt_ui,
        "fn_without_ui": chatgpt_noui,
        "endpoint": openai_endpoint,
        "max_token": 128000,
        "tokenizer": tokenizer_gpt4,
        "token_cnt": get_token_num_gpt4,
    },

    "o1-preview": {
        "fn_with_ui": chatgpt_ui,
        "fn_without_ui": chatgpt_noui,
        "endpoint": openai_endpoint,
        "max_token": 128000,
        "tokenizer": tokenizer_gpt4,
        "token_cnt": get_token_num_gpt4,
    },

    "o3-mini": {
        "fn_with_ui": chatgpt_ui,
        "fn_without_ui": chatgpt_noui,
        "endpoint": openai_endpoint,
        "max_token": 200000,
        "tokenizer": tokenizer_gpt4,
        "token_cnt": get_token_num_gpt4,
    },


    # azure openai
    "azure-gpt-3.5":{
        "fn_with_ui": chatgpt_ui,
        "fn_without_ui": chatgpt_noui,
        "endpoint": azure_endpoint,
        "max_token": 4096,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },

    "azure-gpt-4":{
        "fn_with_ui": chatgpt_ui,
        "fn_without_ui": chatgpt_noui,
        "endpoint": azure_endpoint,
        "max_token": 8192,
        "tokenizer": tokenizer_gpt4,
        "token_cnt": get_token_num_gpt4,
    },

    # 智谱AI
    "glm-4-plus": {
        "fn_with_ui": zhipu_ui,
        "fn_without_ui": zhipu_noui,
        "endpoint": None,
        "max_token": 128000,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },

    "glm-4-air": {
        "fn_with_ui": zhipu_ui,
        "fn_without_ui": zhipu_noui,
        "endpoint": None,
        "max_token": 128000,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },

    "glm-4-long": {
        "fn_with_ui": zhipu_ui,
        "fn_without_ui": zhipu_noui,
        "endpoint": None,
        "max_token": 1000000,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },
    
    "glm-zero-preview": {
        "fn_with_ui": zhipu_ui,
        "fn_without_ui": zhipu_noui,
        "endpoint": None,
        "max_token": 16000,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },

    "glm-4-airx": {
        "fn_with_ui": zhipu_ui,
        "fn_without_ui": zhipu_noui,
        "endpoint": None,
        "max_token": 8000,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },

    "glm-4-flashx": {
        "fn_with_ui": zhipu_ui,
        "fn_without_ui": zhipu_noui,
        "endpoint": None,
        "max_token": 128000,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },

    # 将 chatglm 直接对齐到 chatglm2
    "chatglm": {
        "fn_with_ui": chatglm_ui,
        "fn_without_ui": chatglm_noui,
        "endpoint": None,
        "max_token": 1024,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },
    "chatglm2": {
        "fn_with_ui": chatglm_ui,
        "fn_without_ui": chatglm_noui,
        "endpoint": None,
        "max_token": 1024,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },
    "chatglm3": {
        "fn_with_ui": chatglm3_ui,
        "fn_without_ui": chatglm3_noui,
        "endpoint": None,
        "max_token": 8192,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },

    # cohere
    "cohere-command-r-plus": {
        "fn_with_ui": cohere_ui,
        "fn_without_ui": cohere_noui,
        "can_multi_thread": True,
        "endpoint": cohere_endpoint,
        "max_token": 128000,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },

    "cohere-command-r": {
        "fn_with_ui": cohere_ui,
        "fn_without_ui": cohere_noui,
        "can_multi_thread": True,
        "endpoint": cohere_endpoint,
        "max_token": 128000,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },

    "cohere-command": {
        "fn_with_ui": cohere_ui,
        "fn_without_ui": cohere_noui,
        "can_multi_thread": True,
        "endpoint": cohere_endpoint,
        "max_token": 4096,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },

    "cohere-command-light": {
        "fn_with_ui": cohere_ui,
        "fn_without_ui": cohere_noui,
        "can_multi_thread": True,
        "endpoint": cohere_endpoint,
        "max_token": 4096,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },

    "cohere-c4ai-aya-expanse-8b": {
        "fn_with_ui": cohere_ui,
        "fn_without_ui": cohere_noui,
        "can_multi_thread": True,
        "endpoint": cohere_endpoint,
        "max_token": 1024 * 8,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },

    "cohere-c4ai-aya-expanse-32b": {
        "fn_with_ui": cohere_ui,
        "fn_without_ui": cohere_noui,
        "can_multi_thread": True,
        "endpoint": cohere_endpoint,
        "max_token": 1280000,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },

}
# -=-=-=-=-=-=- 月之暗面 -=-=-=-=-=-=-
from request_llms.bridge_moonshot import predict as moonshot_ui
from request_llms.bridge_moonshot import predict_no_ui_long_connection as moonshot_no_ui
model_info.update({
    "moonshot-v1-8k": {
        "fn_with_ui": moonshot_ui,
        "fn_without_ui": moonshot_no_ui,
        "can_multi_thread": True,
        "endpoint": None,
        "max_token": 1024 * 8,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },
    "moonshot-v1-32k": {
        "fn_with_ui": moonshot_ui,
        "fn_without_ui": moonshot_no_ui,
        "can_multi_thread": True,
        "endpoint": None,
        "max_token": 32768,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },
    "moonshot-v1-128k": {
        "fn_with_ui": moonshot_ui,
        "fn_without_ui": moonshot_no_ui,
        "can_multi_thread": True,
        "endpoint": None,
        "max_token": 131072,
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    }
})
# -=-=-=-=-=-=- api2d 对齐支持 -=-=-=-=-=-=-
for model in AVAIL_LLM_MODELS:
    if model.startswith('api2d-') and (model.replace('api2d-','') in model_info.keys()):
        mi = copy.deepcopy(model_info[model.replace('api2d-','')])
        mi.update({"endpoint": api2d_endpoint})
        model_info.update({model: mi})

# -=-=-=-=-=-=- azure 对齐支持 -=-=-=-=-=-=-
for model in AVAIL_LLM_MODELS:
    if model.startswith('azure-') and (model.replace('azure-','') in model_info.keys()):
        mi = copy.deepcopy(model_info[model.replace('azure-','')])
        mi.update({"endpoint": azure_endpoint})
        model_info.update({model: mi})

# -=-=-=-=-=-=- 以下部分是新加入的模型，可能附带额外依赖 -=-=-=-=-=-=-
# claude家族
claude_models = ['claude-3-5-sonnet-latest','claude-3-5-haiku-latest','claude-3-7-sonnet-latest']
if any(item in claude_models for item in AVAIL_LLM_MODELS):
    from .bridge_claude import predict_no_ui_long_connection as claude_noui
    from .bridge_claude import predict as claude_ui
    model_info.update({
        "claude-3-7-sonnet-latest": {
            "fn_with_ui": claude_ui,
            "fn_without_ui": claude_noui,
            "endpoint": claude_endpoint,
            "max_token": 200000,
            "tokenizer": tokenizer_gpt35,
            "token_cnt": get_token_num_gpt35,
        },
    })
    model_info.update({
        "claude-3-5-sonnet-latest": {
            "fn_with_ui": claude_ui,
            "fn_without_ui": claude_noui,
            "endpoint": claude_endpoint,
            "max_token": 200000,
            "tokenizer": tokenizer_gpt35,
            "token_cnt": get_token_num_gpt35,
        },
    })
    model_info.update({
        "claude-3-5-haiku-latest": {
            "fn_with_ui": claude_ui,
            "fn_without_ui": claude_noui,
            "endpoint": claude_endpoint,
            "max_token": 200000,
            "tokenizer": tokenizer_gpt35,
            "token_cnt": get_token_num_gpt35,
        },
    })
if "jittorllms_rwkv" in AVAIL_LLM_MODELS:
    from .bridge_jittorllms_rwkv import predict_no_ui_long_connection as rwkv_noui
    from .bridge_jittorllms_rwkv import predict as rwkv_ui
    model_info.update({
        "jittorllms_rwkv": {
            "fn_with_ui": rwkv_ui,
            "fn_without_ui": rwkv_noui,
            "endpoint": None,
            "max_token": 1024,
            "tokenizer": tokenizer_gpt35,
            "token_cnt": get_token_num_gpt35,
        },
    })
if "jittorllms_llama" in AVAIL_LLM_MODELS:
    from .bridge_jittorllms_llama import predict_no_ui_long_connection as llama_noui
    from .bridge_jittorllms_llama import predict as llama_ui
    model_info.update({
        "jittorllms_llama": {
            "fn_with_ui": llama_ui,
            "fn_without_ui": llama_noui,
            "endpoint": None,
            "max_token": 1024,
            "tokenizer": tokenizer_gpt35,
            "token_cnt": get_token_num_gpt35,
        },
    })
if "jittorllms_pangualpha" in AVAIL_LLM_MODELS:
    from .bridge_jittorllms_pangualpha import predict_no_ui_long_connection as pangualpha_noui
    from .bridge_jittorllms_pangualpha import predict as pangualpha_ui
    model_info.update({
        "jittorllms_pangualpha": {
            "fn_with_ui": pangualpha_ui,
            "fn_without_ui": pangualpha_noui,
            "endpoint": None,
            "max_token": 1024,
            "tokenizer": tokenizer_gpt35,
            "token_cnt": get_token_num_gpt35,
        },
    })
if "moss" in AVAIL_LLM_MODELS:
    from .bridge_moss import predict_no_ui_long_connection as moss_noui
    from .bridge_moss import predict as moss_ui
    model_info.update({
        "moss": {
            "fn_with_ui": moss_ui,
            "fn_without_ui": moss_noui,
            "endpoint": None,
            "max_token": 1024,
            "tokenizer": tokenizer_gpt35,
            "token_cnt": get_token_num_gpt35,
        },
    })
if "stack-claude" in AVAIL_LLM_MODELS:
    from .bridge_stackclaude import predict_no_ui_long_connection as claude_noui
    from .bridge_stackclaude import predict as claude_ui
    model_info.update({
        "stack-claude": {
            "fn_with_ui": claude_ui,
            "fn_without_ui": claude_noui,
            "endpoint": None,
            "max_token": 8192,
            "tokenizer": tokenizer_gpt35,
            "token_cnt": get_token_num_gpt35,
        }
    })

if "chatglmft" in AVAIL_LLM_MODELS:   # same with newbing-free
    try:
        from .bridge_chatglmft import predict_no_ui_long_connection as chatglmft_noui
        from .bridge_chatglmft import predict as chatglmft_ui
        model_info.update({
            "chatglmft": {
                "fn_with_ui": chatglmft_ui,
                "fn_without_ui": chatglmft_noui,
                "endpoint": None,
                "max_token": 4096,
                "tokenizer": tokenizer_gpt35,
                "token_cnt": get_token_num_gpt35,
            }
        })
    except:
        print(trimmed_format_exc())
# -=-=-=-=-=-=- 上海AI-LAB书生大模型 -=-=-=-=-=-=-
if "internlm" in AVAIL_LLM_MODELS:
    try:
        from .bridge_internlm import predict_no_ui_long_connection as internlm_noui
        from .bridge_internlm import predict as internlm_ui
        model_info.update({
            "internlm": {
                "fn_with_ui": internlm_ui,
                "fn_without_ui": internlm_noui,
                "endpoint": None,
                "max_token": 4096,
                "tokenizer": tokenizer_gpt35,
                "token_cnt": get_token_num_gpt35,
            }
        })
    except:
        print(trimmed_format_exc())
if "chatglm_onnx" in AVAIL_LLM_MODELS:
    try:
        from .bridge_chatglmonnx import predict_no_ui_long_connection as chatglm_onnx_noui
        from .bridge_chatglmonnx import predict as chatglm_onnx_ui
        model_info.update({
            "chatglm_onnx": {
                "fn_with_ui": chatglm_onnx_ui,
                "fn_without_ui": chatglm_onnx_noui,
                "endpoint": None,
                "max_token": 4096,
                "tokenizer": tokenizer_gpt35,
                "token_cnt": get_token_num_gpt35,
            }
        })
    except:
        print(trimmed_format_exc())
# -=-=-=-=-=-=- 通义-本地模型 -=-=-=-=-=-=-
if "qwen-local" in AVAIL_LLM_MODELS:
    try:
        from .bridge_qwen_local import predict_no_ui_long_connection as qwen_local_noui
        from .bridge_qwen_local import predict as qwen_local_ui
        model_info.update({
            "qwen-local": {
                "fn_with_ui": qwen_local_ui,
                "fn_without_ui": qwen_local_noui,
                "can_multi_thread": False,
                "endpoint": None,
                "max_token": 4096,
                "tokenizer": tokenizer_gpt35,
                "token_cnt": get_token_num_gpt35,
            }
        })
    except:
        print(trimmed_format_exc())
# -=-=-=-=-=-=- 通义-在线模型 -=-=-=-=-=-=-
try:
    qwen_noui, qwen_ui = get_predict_function(
    api_key_conf_name="DASHSCOPE_API_KEY",friendly_name='通义千问(dashscope/qwen)', max_output_token=8192, disable_proxy=False
        )
    if 'qwq-plus' in AVAIL_LLM_MODELS:
        model_info.update({
            "qwq-plus": {
                "fn_with_ui": qwen_ui,
                "fn_without_ui": qwen_noui,
                "can_multi_thread": True,
                "endpoint": 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
                "max_token": 98304,
                "tokenizer": tokenizer_gpt35,
                "token_cnt": get_token_num_gpt35,
            }})
    if 'qwen-max' in AVAIL_LLM_MODELS:
        model_info.update({
        "qwen-max": {
            "fn_with_ui": qwen_ui,
            "fn_without_ui": qwen_noui,
            "can_multi_thread": True,
            "endpoint": 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
            "max_token": 30720,
            "tokenizer": tokenizer_gpt35,
            "token_cnt": get_token_num_gpt35,
        }})
    if 'qwen-plus' in AVAIL_LLM_MODELS:
        model_info.update({
        "qwen-plus": {
            "fn_with_ui": qwen_ui,
            "fn_without_ui": qwen_noui,
            "can_multi_thread": True,
            "endpoint": 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
            "max_token": 131072,
            "tokenizer": tokenizer_gpt35,
            "token_cnt": get_token_num_gpt35,
        }})
    if 'qwen-turbo' in AVAIL_LLM_MODELS:
        model_info.update({
        "qwen-turbo": {
            "fn_with_ui": qwen_ui,
            "fn_without_ui": qwen_noui,
            "can_multi_thread": True,
            "endpoint": 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
            "max_token": 1000000,
            "tokenizer": tokenizer_gpt35,
        }})
    if 'qwen-long' in AVAIL_LLM_MODELS:
        model_info.update({
        "qwen-long": {
            "fn_with_ui": qwen_ui,
            "fn_without_ui": qwen_noui,
            "can_multi_thread": True,
            "endpoint": 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
            "max_token": 1000000,
            "tokenizer": tokenizer_gpt35,
            "token_cnt": get_token_num_gpt35,
        }})
except:
    print(trimmed_format_exc())

if "llama2" in AVAIL_LLM_MODELS:   # llama2
    try:
        from .bridge_llama2 import predict_no_ui_long_connection as llama2_noui
        from .bridge_llama2 import predict as llama2_ui
        model_info.update({
            "llama2": {
                "fn_with_ui": llama2_ui,
                "fn_without_ui": llama2_noui,
                "endpoint": None,
                "max_token": 4096,
                "tokenizer": tokenizer_gpt35,
                "token_cnt": get_token_num_gpt35,
            }
        })
    except:
        print(trimmed_format_exc())

# -=-=-=-=-=-=- 幻方-深度求索大模型 -=-=-=-=-=-=-
if "deepseekcoder" in AVAIL_LLM_MODELS:   # deepseekcoder
    try:
        from .bridge_deepseekcoder import predict_no_ui_long_connection as deepseekcoder_noui
        from .bridge_deepseekcoder import predict as deepseekcoder_ui
        model_info.update({
            "deepseekcoder": {
                "fn_with_ui": deepseekcoder_ui,
                "fn_without_ui": deepseekcoder_noui,
                "endpoint": None,
                "max_token": 2048,
                "tokenizer": tokenizer_gpt35,
                "token_cnt": get_token_num_gpt35,
            }
        })
    except:
        print(trimmed_format_exc())
# -=-=-=-=-=-=- 幻方-深度求索大模型在线API -=-=-=-=-=-=-
if "deepseek-chat" in AVAIL_LLM_MODELS or "deepseek-reasoner" in AVAIL_LLM_MODELS:
    try:
        deepseekapi_noui, deepseekapi_ui = get_predict_function(
            api_key_conf_name="DEEPSEEK_API_KEY", friendly_name='深度求索(deepseek)',max_output_token=8192, disable_proxy=False
            )
        model_info.update({
            "deepseek-chat":{
                "fn_with_ui": deepseekapi_ui,
                "fn_without_ui": deepseekapi_noui,
                "endpoint": deepseekapi_endpoint,
                "can_multi_thread": True,
                "max_token": 64000,
                "tokenizer": tokenizer_gpt35,
                "token_cnt": get_token_num_gpt35,
            },
            "deepseek-reasoner":{
                "fn_with_ui": deepseekapi_ui,
                "fn_without_ui": deepseekapi_noui,
                "endpoint": deepseekapi_endpoint,
                "can_multi_thread": True,
                "max_token": 64000,
                "tokenizer": tokenizer_gpt35,
                "token_cnt": get_token_num_gpt35,
            },
        })
    except:
        print(trimmed_format_exc())


# -=-=-=-=-=-=- Google Gemini -=-=-=-=-=-=-
if any (m.startswith('gemini') for m in AVAIL_LLM_MODELS ) :
    try:
        gemini_noui, gemini_ui = get_predict_function(
            api_key_conf_name="GEMINI_API_KEY", friendly_name='Gemini',max_output_token=8192, disable_proxy=False
            )
        model_info.update({
            "gemini-2.5-pro-preview-03-25":{
                "fn_with_ui": gemini_ui,
                "fn_without_ui": gemini_noui,
                "endpoint": gemini_endpoint,
                "can_multi_thread": True,
                "max_token": 1048576,
                "tokenizer": tokenizer_gpt35,
                "token_cnt": get_token_num_gpt35,
            },
            "gemini-2.0-flash":{
                "fn_with_ui": gemini_ui,
                "fn_without_ui": gemini_noui,
                "endpoint": gemini_endpoint,
                "can_multi_thread": True,
                "max_token": 1048576,
                "tokenizer": tokenizer_gpt35,
                "token_cnt": get_token_num_gpt35,
            },
            "gemini-2.0-flash-lite": {
                "fn_with_ui": gemini_ui,
                "fn_without_ui": gemini_noui,
                "endpoint": gemini_endpoint,
                "can_multi_thread": True,
                "max_token": 1048576,
                "tokenizer": tokenizer_gpt35,
                "token_cnt": get_token_num_gpt35,
            },
        })
    except:
        print(trimmed_format_exc())


# -=-=-=-=-=-=- X.Grok -=-=-=-=-=-=-
if any(m.startswith("grok-") for m in AVAIL_LLM_MODELS):
    try:
        grok_noui, grok_ui = get_predict_function(
            api_key_conf_name="XAI_API_KEY",friendly_name='Grok', max_output_token=8192, disable_proxy=False
            )
        model_info.update({
            "grok-2":{
                "fn_with_ui": grok_ui,
                "fn_without_ui": grok_noui,
                "endpoint": 'https://api.x.ai/v1/chat/completions',
                "can_multi_thread": True,
                "max_token": 131072,
                "tokenizer": tokenizer_gpt35,
                "token_cnt": get_token_num_gpt35,
            },
            "grok-3-mini-fast": {
                "fn_with_ui": grok_ui,
                "fn_without_ui": grok_noui,
                "endpoint": 'https://api.x.ai/v1/chat/completions',
                "can_multi_thread": True,
                "max_token": 131072,
                "tokenizer": tokenizer_gpt35,
                "token_cnt": get_token_num_gpt35,
            },
            "grok-3-mini": {
                "fn_with_ui": grok_ui,
                "fn_without_ui": grok_noui,
                "endpoint": 'https://api.x.ai/v1/chat/completions',
                "can_multi_thread": True,
                "max_token": 131072,
                "tokenizer": tokenizer_gpt35,
                "token_cnt": get_token_num_gpt35,
            },
            "grok-3-fast": {
                "fn_with_ui": grok_ui,
                "fn_without_ui": grok_noui,
                "endpoint": 'https://api.x.ai/v1/chat/completions',
                "can_multi_thread": True,
                "max_token": 131072,
                "tokenizer": tokenizer_gpt35,
                "token_cnt": get_token_num_gpt35,
            },
            "grok-3": {
                "fn_with_ui": grok_ui,
                "fn_without_ui": grok_noui,
                "endpoint": 'https://api.x.ai/v1/chat/completions',
                "can_multi_thread": True,
                "max_token": 131072,
                "tokenizer": tokenizer_gpt35,
                "token_cnt": get_token_num_gpt35,
            },
        })
    except:
        print(trimmed_format_exc())
        
# 拓展模型等支持
def extend_llm_support(models: list,label:str):
    """独立出拓展模型加载（包含聚合LLM平台和本地模型）模块，便于实现用户自定义模型。

    Args:
        models (_type_): 模型们（所有的模型的开头应当具有label）。
            此外，也可以添加 (max_token=1234) 这个token信息
        label (str): 标签，应当为 'custom- / one-api-'、'vllm-'或'ollama-'
        
    Returns:
        dict (dict): {model_name: this_model_info}
    """
    assert label == 'ollama-' or label == 'one-api-' or label == 'custom-' or label == 'vllm-'
    
    if label == 'ollama-':
        from .bridge_ollama import predict_no_ui_long_connection as ollama_noui
        from .bridge_ollama import predict as ollama_ui
    
    dict_ = {}
    for model in models:
        try:
            origin_model_name, max_token_tmp = read_one_api_model_name(model)
            # 如果是已知模型，则尝试获取其信息
            original_model_info = model_info.get(origin_model_name.replace(label, "", 1), None)
        except:
            print(_("one-api模型 {} 的 max_token 配置不是整数，请检查配置文件").format(model))
            continue
        
        this_model_info = {
            "fn_with_ui": chatgpt_ui if label != 'ollama-' else ollama_ui,
            "fn_without_ui": chatgpt_noui if label != 'ollama-'  else ollama_noui,
            "can_multi_thread": True,
            "endpoint": openai_endpoint if label != 'ollama-' else ollama_endpoint,
            "max_token": max_token_tmp,
            "tokenizer": tokenizer_gpt35,
            "token_cnt": get_token_num_gpt35,
        }

        # 同步已知模型的其他信息
        attribute = "has_multimodal_capacity"
        if original_model_info is not None and original_model_info.get(attribute, None) is not None: this_model_info.update({attribute: original_model_info.get(attribute, None)})
        # attribute = "attribute2"
        # if original_model_info is not None and original_model_info.get(attribute, None) is not None: this_model_info.update({attribute: original_model_info.get(attribute, None)})
        # attribute = "attribute3"
        # if original_model_info is not None and original_model_info.get(attribute, None) is not None: this_model_info.update({attribute: original_model_info.get(attribute, None)})
        dict_.update({model: this_model_info})
    return dict_


# -=-=-=-=-=-=- one-api 对齐支持 -=-=-=-=-=-=-
model_info.update(extend_llm_support([m for m in AVAIL_LLM_MODELS if m.startswith("one-api-")],'one-api-'))

# -=-=-=-=-=-=- vllm 对齐支持 -=-=-=-=-=-=-
model_info.update(extend_llm_support([m for m in AVAIL_LLM_MODELS if m.startswith("vllm-")],'vllm-'))

# -=-=-=-=-=-=- ollama 对齐支持 -=-=-=-=-=-=-
model_info.update(extend_llm_support([m for m in AVAIL_LLM_MODELS if m.startswith("ollama-")],'ollama-'))

# -=-=-=-=-=-=- azure模型对齐支持 -=-=-=-=-=-=-
AZURE_CFG_ARRAY = get_conf("AZURE_CFG_ARRAY") # <-- 用于定义和切换多个azure模型 -->
if len(AZURE_CFG_ARRAY) > 0:
    for azure_model_name, azure_cfg_dict in AZURE_CFG_ARRAY.items():
        # 可能会覆盖之前的配置，但这是意料之中的
        if not azure_model_name.startswith('azure'):
            raise ValueError(_("AZURE_CFG_ARRAY中配置的模型必须以azure开头"))
        endpoint_ = azure_cfg_dict["AZURE_ENDPOINT"] + \
            f'openai/deployments/{azure_cfg_dict["AZURE_ENGINE"]}/chat/completions?api-version=2023-05-15'
        model_info.update({
            azure_model_name: {
                "fn_with_ui": chatgpt_ui,
                "fn_without_ui": chatgpt_noui,
                "endpoint": endpoint_,
                "azure_api_key": azure_cfg_dict["AZURE_API_KEY"],
                "max_token": azure_cfg_dict["AZURE_MODEL_MAX_TOKEN"],
                "tokenizer": tokenizer_gpt35,   # tokenizer只用于粗估token数量
                "token_cnt": get_token_num_gpt35,
            }
        })
        if azure_model_name not in AVAIL_LLM_MODELS:
            AVAIL_LLM_MODELS += [azure_model_name]


# 给model_info封装一个类，添加一些功能，兼容原版代码和添加的自定义模型
model_info = model_info_class(model_info,extend_llm_support)

# -=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=-=-=
# -=-=-=-=-=-=-=-=-=- ☝️ 以上是模型路由 -=-=-=-=-=-=-=-=-=
# -=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=-=-=

# -=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=-=-=
# -=-=-=-=-=-=-= 👇 以下是多模型路由切换函数 -=-=-=-=-=-=-=
# -=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=-=-=


def LLM_CATCH_EXCEPTION(f):
    """
    装饰器函数，将错误显示出来
    """
    def decorated(inputs:str, llm_kwargs:dict, history:list, sys_prompt:str, observe_window:list, console_slience:bool):
        try:
            return f(inputs, llm_kwargs, history, sys_prompt, observe_window, console_slience)
        except Exception as e:
            tb_str = '\n```\n' + trimmed_format_exc() + '\n```\n'
            observe_window[0] = tb_str
            return tb_str
    return decorated


def predict_no_ui_long_connection(inputs:str, llm_kwargs:dict, history:list, sys_prompt:str, observe_window:list=[], console_slience:bool=False,lang:str = None):
    """
    发送至LLM，等待回复，一次性完成，不显示中间过程。但内部（尽可能地）用stream的方法避免中途网线被掐。
    inputs：
        是本次问询的输入
    sys_prompt:
        系统静默prompt
    llm_kwargs：
        LLM的内部调优参数
    history：
        是之前的对话列表
    observe_window = None：
        用于负责跨越线程传递已经输出的部分，大部分时候仅仅为了fancy的视觉效果，留空即可。observe_window[0]：观测窗。observe_window[1]：看门狗
    """

    _ = lambda txt:init_language(txt,lang)

    if not isinstance(history,list):
        raise ValueError(_("历史记录参数必须是List, 但是现在的类型是{}").format(type(history)))

    # 空输入会报错
    if not inputs:inputs = ' '
    # 有的空prompt也会报错
    if not sys_prompt: sys_prompt = ' '

    time.sleep(1.1) # 部分服务限制每秒一次访问

    inputs = apply_gpt_academic_string_mask(inputs, mode="show_llm")
    model = llm_kwargs['llm_model']
    n_model = 1

    # 修复history奇数时请求缺少历史记录
    if len(history) % 2 == 1:
        history.append('.')

        # 检查输入长度
    accessible,msg1,msg2 = check_actual_inputs_length(inputs=inputs,history=history,
                                            token_cnt = model_info[llm_kwargs['llm_model']]['token_cnt'],
                                            max_token = model_info[llm_kwargs['llm_model']]['max_token'],lang=lang)

    if not accessible:
        raise ConnectionAbortedError(f'{msg1}. {msg2}') # 兼容crazy_utils.py的异常处理
        

    if '&' not in model:
        # 如果只询问“一个”大语言模型（多数情况）：
        method = model_info[model]["fn_without_ui"]
        return method(inputs, llm_kwargs, history, sys_prompt, observe_window, console_slience)
    else:
        # 如果同时询问“多个”大语言模型，这个稍微啰嗦一点，但思路相同，您不必读这个else分支
        executor = ThreadPoolExecutor(max_workers=4)
        models = model.split('&')
        n_model = len(models)

        window_len = len(observe_window)
        assert window_len==3
        window_mutex = [["", time.time(), ""] for _9 in range(n_model)] + [True]

        futures = []
        for i in range(n_model):
            model = models[i]
            method = model_info[model]["fn_without_ui"]
            llm_kwargs_feedin = copy.deepcopy(llm_kwargs)
            llm_kwargs_feedin['llm_model'] = model
            future = executor.submit(LLM_CATCH_EXCEPTION(method), inputs, llm_kwargs_feedin, history, sys_prompt, window_mutex[i], console_slience)
            futures.append(future)

        def mutex_manager(window_mutex, observe_window):
            while True:
                time.sleep(0.25)
                if not window_mutex[-1]: break
                # 看门狗（watchdog）
                for i in range(n_model):
                    window_mutex[i][1] = observe_window[1]
                # 观察窗（window）
                chat_string = []
                for i in range(n_model):
                    color = colors[i%len(colors)]
                    chat_string.append( f"【{str(models[i])}】: <font color=\"{color}\"> {window_mutex[i][0]} </font>" )
                res = '<br/><br/>\n\n---\n\n'.join(chat_string)
                # # # # # # # # # # #
                observe_window[0] = res

        t_model = threading.Thread(target=mutex_manager, args=(window_mutex, observe_window), daemon=True)
        t_model.start()

        return_string_collect = []
        while True:
            worker_done = [h.done() for h in futures]
            if all(worker_done):
                executor.shutdown()
                break
            time.sleep(1)

        for i, future in enumerate(futures):  # wait and get
            color = colors[i%len(colors)]
            return_string_collect.append( f"【{str(models[i])}】: <font color=\"{color}\"> {future.result()} </font>" )

        window_mutex[-1] = False # stop mutex thread
        res = '<br/><br/>\n\n---\n\n'.join(return_string_collect)
        return res

# 根据基础功能区 ModelOverride 参数调整模型类型，用于 `predict` 中
import importlib
import core_functional
def execute_model_override(llm_kwargs, additional_fn, method):
    functional = core_functional.get_core_functions()
    if (additional_fn in functional) and 'ModelOverride' in functional[additional_fn]:
        # 热更新Prompt & ModelOverride
        importlib.reload(core_functional)
        functional = core_functional.get_core_functions()
        model_override = functional[additional_fn]['ModelOverride']
        if model_override not in model_info:
            raise ValueError(_("模型覆盖参数 '{}' 指向一个暂不支持的模型，请检查配置文件").fomat(model_override))
        method = model_info[model_override]["fn_with_ui"]
        llm_kwargs['llm_model'] = model_override
        return llm_kwargs, additional_fn, method
    # 默认返回原参数
    return llm_kwargs, additional_fn, method

def predict(inputs:str, llm_kwargs:dict, plugin_kwargs:dict, chatbot,
            history:list=[], system_prompt:str='', stream:bool=True, additional_fn:str=None):
    """
    发送至LLM，流式获取输出。
    用于基础的对话功能。

    完整参数列表：
        predict(
            inputs:str,                     # 是本次问询的输入
            llm_kwargs:dict,                # 是LLM的内部调优参数
            plugin_kwargs:dict,             # 是插件的内部参数
            chatbot:ChatBotWithCookies,     # 原样传递，负责向用户前端展示对话，兼顾前端状态的功能
            history:list=[],                # 是之前的对话列表
            system_prompt:str='',           # 系统静默prompt
            stream:bool=True,               # 是否流式输出（已弃用）
            additional_fn:str=None          # 基础功能区按钮的附加功能
        ):
    """
    lang = chatbot.get_language()
    _ = lambda text: init_language(text, lang)

    if not isinstance(history,list):
        raise ValueError(_("历史记录参数必须是List"))
    
    # 修复history奇数时请求缺少历史记录
    if len(history) % 2 == 1:
        history.append('.')

    # 检查输入长度
    accessible,msg1,msg2 = check_actual_inputs_length(inputs=inputs,history=history,
                                            token_cnt = model_info[llm_kwargs['llm_model']]['token_cnt'],
                                            max_token = model_info[llm_kwargs['llm_model']]['max_token'],lang=lang)

    if not accessible:
        chatbot.append([msg1,msg2])
        yield from update_ui(chatbot, history, msg=_('过长的输入'))
        return

    inputs = apply_gpt_academic_string_mask(inputs, mode="show_llm")

    method = model_info[llm_kwargs['llm_model']]["fn_with_ui"]  # 如果这里报错，检查config中的AVAIL_LLM_MODELS选项

    if additional_fn: # 根据基础功能区 ModelOverride 参数调整模型类型
        llm_kwargs, additional_fn, method = execute_model_override(llm_kwargs, additional_fn, method)

    yield from method(inputs, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, stream, additional_fn)


def check_actual_inputs_length(inputs:str,history:list,token_cnt,max_token,lang):

    _ = lambda text: init_language(text, lang)

    actual_input = f'{inputs}\n{"\n".join(history)}'
    threshold = int(0.95 * max_token)
    if token_cnt(actual_input) > threshold:
        msg1 =  _('输入过长，请使用支持更多token限制的模型，或者是减少/分批输入。程序已终止.')
        msg2 = _('模型的最大允许长度的阈值: {} tokens, 当前输入的长度为: {} tokens').format(threshold,token_cnt(actual_input))
        return False, msg1, msg2
    return True, None, None