'''
Original Author: gpt_academic@binary-husky

Modified by PureAmaya on 2025-03-06
- Add models: qwen-long and qwq-plus.

Modified by PureAmaya on 2025-02-28
- New models have been configured.
- Add grok support
- Since some models have been removed, the related configurations have also been removed here.
- Since delays have been added to both multi-threaded and single-threaded tasks, the default value of DEFAULT_WORKER_NUM has been appropriately increased to speed up the process.

Modified by PureAmaya on 2024-12-28
- Add some new configurations.
- Remove some unnecessary configurations.
- Add English annotations.
'''

"""
    以下所有配置也都支持利用环境变量覆写，环境变量配置格式见docker-compose.yml。
    读取优先级：环境变量 > config_private.py > config.py
    --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
    All the following configurations also support using environment variables to override,
    and the environment variable configuration format can be seen in docker-compose.yml.
    Configuration reading priority: environment variable > config_private.py > config.py
"""

# [step 1]>> API_KEY = "sk-123456789xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx123456789"。极少数情况下，还需要填写组织（格式如org-123456789abcdefghijklmno的），请向下翻，找 API_ORG 设置项
# 可同时填写多个API-KEY，用英文逗号分割，例如API_KEY = "sk-openaikey1,sk-openaikey2,fkxxxx-api2dkey3,azure-apikey4"
# In very few cases, you need to fill in the organization (formatted as org-123456789abcdefghijklmno), please scroll down to find the API_ORG setting item.
# Multiple API-KEYs can be filled in simultaneously, separated by English commas, for example: API_KEY = "sk-openaikey1,sk-openaikey2,fkxxxx-api2dkey3,azure-apikey4"
API_KEY = "此处填API密钥"   


# [step 2]>> 改为True应用代理，如果直接在海外服务器部署，此处不修改；如果使用本地或无地域限制的大模型时，此处也不需要修改
# [step 2]>> Change to True to apply the proxy, if deployed directly on a server overseas, no modification here; if using a local or region-agnostic large model, no modification is needed here either.
USE_PROXY = False
if USE_PROXY:
    """
    代理网络的地址，打开你的代理软件查看代理协议(socks5h / http)、地址(localhost)和端口(11284)
    填写格式是 [协议]://  [地址] :[端口]，填写之前不要忘记把USE_PROXY改成True，如果直接在海外服务器部署，此处不修改
            <配置教程&视频教程> https://github.com/binary-husky/gpt_academic/issues/1>
    [协议] 常见协议无非socks5h/http; 例如 v2**y 和 ss* 的默认本地协议是socks5h; 而cl**h 的默认本地协议是http
    [地址] 填localhost或者127.0.0.1（localhost意思是代理软件安装在本机上）
    [端口] 在代理软件的设置里找。虽然不同的代理软件界面不一样，但端口号都应该在最显眼的位置上
    """
    proxies = {
        #          [协议]://  [地址]  :[端口]
        "http":  "socks5h://localhost:11284",  # 再例如  "http":  "http://127.0.0.1:7890",
        "https": "socks5h://localhost:11284",  # 再例如  "https": "http://127.0.0.1:7890",
    }
else:
    proxies = None

# [step 3]>> 模型选择是 (注意: LLM_MODEL是默认选中的模型, 它*必须*被包含在AVAIL_LLM_MODELS列表中 )
# [step 3]>> Model selection is (Note: LLM_MODEL is the default selected model and it must be included in the AVAIL_LLM_MODELS list)
LLM_MODEL = "deepseek-chat" # 可选 / Optional ↓↓↓
AVAIL_LLM_MODELS = ["gpt-4o", "gpt-4o-mini", "o1",'o1-mini','o1-preview','o3-mini','gpt-4.5-preview',
                    "grok-2",
                    "glm-4-plus","glm-4-airx","glm-4-air","glm-4-flashx","glm-zero-preview",
                    "moonshot-v1-8k","moonshot-v1-32k","moonshot-v1-128k", 
                    'qwq-plus',"qwen-max","qwen-plus","qwen-turbo",'qwen-long',
                    "deepseek-chat","deepseek-reasoner"
                    ]
# --- --- --- ---
# P.S. 其他可用的模型还包括 / Other available models include:
# AVAIL_LLM_MODELS = [
#   'azure-gpt-3.5',"azure-gpt-4",
#   "chatglm","chatglm2","chatglm3","chatglmft","chatglm_onnx"
#   "jittorllms_rwkv","jittorllms_llama","jittorllms_pangualpha",
#   "moss","stack-claude","internlm","qwen-local",'llama2',"deepseekcoder"
#   "gemini-2.0-flash","gemini-1.5-pro","gemini-1.5-flash","gemini-1.5-flash-8b", # 目前还不支持自定义 / Currently not supported
#   "cohere-command-r-plus","cohere-command-r","cohere-command","cohere-command-light","cohere-c4ai-aya-expanse-8b","cohere-c4ai-aya-expanse-32b",  # 目前还不支持自定义 / Currently not supported
#   'claude-3-5-sonnet-latest','claude-3-5-haiku-latest','claude-3-opus-latest', # 目前还不支持自定义 / Currently not supported
#   

# --- --- --- ---
# 此外，您还可以在接入one-api/vllm/ollama时，
# 使用"one-api-*","vllm-*","ollama-*"前缀直接使用非标准方式接入的模型，例如
# Additionally, when accessing one-api/vllm/ollama, 
# you can directly use models accessed via non-standard methods with the prefixes "one-api-", "vllm-", "ollama-*", 
# for example:
# AVAIL_LLM_MODELS = ["one-api-claude-3-sonnet-20240229(max_token=100000)", "ollama-phi3(max_token=4096)"]
# --- --- --- ---


# --------------- 以下配置可以优化体验 ---------------

# 重新URL重新定向，实现更换API_URL的作用（高危设置! 常规情况下不要修改! 通过修改此设置，您将把您的API-KEY和对话隐私完全暴露给您设定的中间人！）
# Re-redirecting the URL to achieve the effect of changing the API_URL 
# (High-risk setting! Do not modify under normal circumstances! By modifying this setting, you will expose your API-KEY and conversation privacy completely to the intermediary you set!)
# 格式: API_URL_REDIRECT = {"https://api.openai.com/v1/chat/completions": "在这里填写重定向的api.openai.com的URL"}
# 举例: API_URL_REDIRECT = {"https://api.openai.com/v1/chat/completions": "https://reverse-proxy-url/v1/chat/completions", "http://localhost:11434/api/chat": "在这里填写您ollama的URL"}
API_URL_REDIRECT = {}


# 多线程函数插件中，默认允许多少路线程同时访问OpenAI。Free trial users的限制是每分钟3次，Pay-as-you-go users的限制是每分钟3500次
# 一言以蔽之：免费（5刀）用户填3，OpenAI绑了信用卡的用户可以填 16 或者更高。提高限制请查询：https://platform.openai.com/docs/guides/rate-limits/overview
# In the multi-threading function plugin, the default allows how many threads to access OpenAI simultaneously. Free trial users are limited to 3 requests per minute, while Pay-as-you-go users are limited to 3,500 requests per minute.
# In short: Free ($5) users fill in 3, and users with a credit card linked to OpenAI can fill in 16 or higher. To increase the limit, please check: https://platform.openai.com/docs/guides/rate-limits/overview
DEFAULT_WORKER_NUM = 5

# 默认的系统提示词（system prompt）
INIT_SYS_PROMPT = "Serve me as a writing and programming assistant."


# 对话窗的高度 （仅在LAYOUT="TOP-DOWN"时生效）
# Dialogue window height (only effective when LAYOUT="TOP-DOWN")
CHATBOT_HEIGHT = 1115

# 窗口布局 / layout
LAYOUT = "LEFT-RIGHT"   # "LEFT-RIGHT"（左右布局） # "TOP-DOWN"（上下布局）


# 发送请求到OpenAI后，等待多久判定为超时
# The timeout duration after sending a request to OpenAI is determined after how long.
TIMEOUT_SECONDS = 30


# 网页的端口, -1代表随机端口
# The port of a web page, -1 represents a random port.
WEB_PORT = -1


# 是否自动打开浏览器页面
# Is the browser page automatically opened?
AUTO_OPEN_BROWSER = True


# 如果OpenAI不响应（网络卡顿、代理失败、KEY失效），重试的次数限制
# If OpenAI does not respond (due to network lag, proxy failure, or KEY expiration),  the limit on the number of retries
MAX_RETRY = 2


# 选择本地模型变体（只有当AVAIL_LLM_MODELS包含了对应本地模型时，才会起作用）
# 如果你选择Qwen系列的模型，那么请在下面的QWEN_MODEL_SELECTION中指定具体的模型
# 也可以是具体的模型路径
# Select the local model variant (this will only take effect if AVAIL_LLM_MODELS includes the corresponding local model)
# If you choose a model from the Qwen series, specify the specific model in the QWEN_MODEL_SELECTION below
# It can also be a specific model path
QWEN_LOCAL_MODEL_SELECTION = "Qwen/Qwen-1_8B-Chat-Int8"


# 接入通义千问在线大模型 https://dashscope.console.aliyun.com/
# QWEN
DASHSCOPE_API_KEY = "" # 阿里灵积云API_KEY


# 如果使用ChatGLM2微调模型，请把 LLM_MODEL="chatglmft"，并在此处指定模型路径
# f using the ChatGLM2 fine-tuned model, set LLM_MODEL="ChatGLMft" and specify the model path here.
CHATGLM_PTUNING_CHECKPOINT = "" # 例如"/home/hmp/ChatGLM2-6B/ptuning/output/6b-pt-128-1e-2/checkpoint-100"


# 本地LLM模型如ChatGLM的执行方式 CPU/GPU
# The execution method for local LLM models like ChatGLM can be CPU or GPU.
LOCAL_MODEL_DEVICE = "cpu" # 可选 / optional: "cuda"
LOCAL_MODEL_QUANT = "FP16" # 默认 "FP16" "INT4" 启用量化INT4版本 "INT8" 启用量化INT8版本


# 设置gradio的并行线程数（不需要修改）
# Set the number of parallel threads for Gradio (no modification required).
CONCURRENT_COUNT = 100


# 是否在提交时自动清空输入框
# Is the input box automatically cleared upon submission?
AUTO_CLEAR_TXT = False


# [step 4] 启用登录功能（不启用时则以default_user身份访问）
# [step 4] Enable login function (disabled by default, default_user access if not enabled)
AUTHENTICATION = False



# HTTPS 秘钥和证书（不需要修改）
# HTTPS Keys and Certificates (no modification required)
SSL_KEYFILE = ""
SSL_CERTFILE = ""


# 极少数情况下，openai的官方KEY需要伴随组织编码（格式如org-xxxxxxxxxxxxxxxxxxxxxxxx）使用
# In very rare cases, OpenAI's official KEY needs to be used with an organization code (formatted as org-xxxxxxxxxxxxxxxxxxxxxxxx).
API_ORG = ""


# 如果需要使用Slack Claude，使用教程详情见 request_llms/README.md
# If you need to use Slack Claude, see the detailed tutorial in request_llms/README.md.
SLACK_CLAUDE_BOT_ID = ''
SLACK_CLAUDE_USER_TOKEN = ''


# 如果需要使用AZURE（方法一：单个azure模型部署）详情请见额外文档 docs\use_azure.md
# If you need to use AZURE (Method 1: Deployment of a Single Azure Model), please refer to the additional document docs\use_azure.md.
AZURE_ENDPOINT = "https://你亲手写的api名称.openai.azure.com/"
# 建议直接在API_KEY处填写，该选项即将被弃用
# It is recommended to fill in the API_KEY directly, as this option will soon be deprecated.
AZURE_API_KEY = "填入azure openai api的密钥"    
# docs\use_azure.md
AZURE_ENGINE = "填入你亲手写的部署名"           


# 如果需要使用AZURE（方法二：多个azure模型部署+动态切换）详情请见额外文档 docs\use_azure.md
# If you need to use AZURE (Method 2: Deployment of Multiple Azure Models + Dynamic Switching), please refer to the additional document docs\use_azure.md.
AZURE_CFG_ARRAY = {}



# 接入讯飞星火大模型 https://console.xfyun.cn/services/iat
# iFLYTEK Xunfei Spark Large Model
XFYUN_APPID = "00000000"
XFYUN_API_SECRET = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
XFYUN_API_KEY = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


# 接入智谱大模型
#ZHIPU (GLM) API KEY
ZHIPUAI_API_KEY = ""
ZHIPUAI_MODEL = "" # 此选项已废弃，不再需要填写


# Claude API KEY
ANTHROPIC_API_KEY = ""


# 月之暗面 API KEY
# MOONSHOT API KEY
MOONSHOT_API_KEY = ""


# 零一万物(Yi Model) API KEY
# Yi Model API KEY
YIMODEL_API_KEY = ""


# 深度求索(DeepSeek) API KEY，默认请求地址为"https://api.deepseek.com/v1/chat/completions"
# DeepSeek API KEY, default request address is "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = ""


# Google Gemini API-Key
GEMINI_API_KEY = ''


# grok API
XAI_API_KEY= ''

# HUGGINGFACE的TOKEN，下载LLAMA时起作用 https://huggingface.co/docs/hub/security-tokens
# Huggingface Token, which is useful when downloading LLAMA (https://huggingface.co/docs/hub/security-tokens)
HUGGINGFACE_ACCESS_TOKEN = "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"


# 在使用AutoGen插件时，是否使用Docker容器运行代码
# Whether to use Docker containers to run code when using the AutoGen plugin.
AUTOGEN_USE_DOCKER = False


# 临时的上传文件夹位置，请尽量不要修改
# The temporary upload folder location, please do not modify.
PATH_PRIVATE_UPLOAD = "private_upload"


# 日志文件夹的位置，请尽量不要修改
# The location of the log folder, please do not modify.
PATH_LOGGING = "gpt_log"


# 存储翻译好的arxiv论文的路径，请尽量不要修改
# The path to store translated arxiv papers, please do not modify.
ARXIV_CACHE_DIR = "gpt_log/arxiv_cache"


# 除了连接OpenAI之外，还有哪些场合允许使用代理，请尽量不要修改
# In addition to connecting to OpenAI, there are other occasions where the use of a proxy is allowed. 
# Please try to avoid making modifications.
WHEN_TO_USE_PROXY = ["Download_LLM", "Download_Gradio_Theme", "Connect_Grobid",
                     "Warmup_Modules", "Nougat_Download", "AutoGen"]


# 启用插件热加载
# Enable plugin hot reloading
PLUGIN_HOT_RELOAD = False


##### Scholar Navis 添加的配置 #####

# [step 5]
# 模型显示偏好语言，通常只要模型支持该语言就可以。用户可以自行选择
# The language preference for displaying models, which is usually only required if the model supports it.
# User can choose their own preference.
# e.g. '简体中文','繁體中文','English','日本語','Français','Deutsch','Русский,"العربية",Español'
LANGUAGE_GPT_PREFER = '简体中文' 

# [step 6]
# WEB和程序的显示语言。基于gettext制作，可以自己修改或添加其他语言
# The language of the WEB and program display. Based on gettext, it can be modified or added to other languages.
# 目前可用：'zh-Hans','zh-Hant','en-US'
LANGUAGE_DISPLAY = 'zh-Hans'

# [step 7]
# 是否自动清理临时文件（tmp）（目前不含gradio的临时文件，仅包含用户产生的）
# Whether to automatically clean up temporary files (tmp) (currently excluding gradio's temporary files
# only including user-generated files).
AUTO_CLEAR_TMP = True

# [step 8]
# 是否自动清理过时用户日志文件（gpt_log/用户名/ ,存在超过5小时）
# Whether to automatically clean up outdated user log files (gpt_log/username/, which exist for more than 5 hours).
AUTO_CLEAR_GPT_LOG_DIR = False

# [step 9]
# 是否自动清理私有上传文件（private_upload/用户名/，存在超过3小时）
# Whether to automatically clean up private upload files (private_upload/username/, which exist for more than 3 hours).
AUTO_CLEAR_PRIVATE_UPLOAD = False

# [step 10]
# 是否启用Pubmed下载器，通过官方API快速下载选定的OA论文。如果担心封禁，请勿开启
# Whether to enable the Pubmed downloader, which can quickly download selected OA papers through the official API.
ENABLE_PUBMED_DOWNLOADER = True

# [step 11]
# 偏好AI辅助获取文章信息的功能（可以通过LLM获取文章标题与doi），用户可自行关闭
# The preferred AI assistance function for obtaining article information (you can get the article title and doi through the LLM).
# Users can turn it off themselves.
PRIORITIZE_USE_AI_ASSISTANCE = True

# [step 12]
# 摘取有用句子的最大线程数，用户可以选择<= 32的值
# The maximum number of threads for extracting useful sentences, users can choose a value <= 32.
EXTRACT_USEFUL_SENTENCES_THREADS_MAX_NUM = 32

# [step 13]
# 目前仅用于匿名登录的自定义和参数储存用的密钥，请修改为自己的最强密钥
# The secret key used for custom and parameter storage for anonymous login, please change it to your own strongest secret key.
SECRET = 'Please change it to your own strongest secret key'
