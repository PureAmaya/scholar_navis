import time
import os
from toolbox import update_ui, get_conf, update_ui_lastest_msg
from toolbox import check_packages, report_exception, log_chat
from shared_utils.scholar_navis.multi_lang import _

model_name = 'Qwen'

def predict_no_ui_long_connection(inputs:str, llm_kwargs:dict, history:list=[], sys_prompt:str="",
                                  observe_window:list=[], console_slience:bool=False):
    """
        ⭐多线程方法
        函数的说明请见 request_llms/bridge_all.py
    """
    watch_dog_patience = 5
    response = ""

    from .com_qwenapi import QwenRequestInstance
    api_key = llm_kwargs['custom_api_key']("DASHSCOPE_API_KEY")
    sri = QwenRequestInstance(api_key)
    for response in sri.generate(inputs, llm_kwargs, history, sys_prompt):
        if len(observe_window) >= 1:
            observe_window[0] = response
        if len(observe_window) >= 2:
            if (time.time()-observe_window[1]) > watch_dog_patience: raise RuntimeError(_("用户停止"))
    return response

def predict(inputs, llm_kwargs, plugin_kwargs, chatbot, history=[], system_prompt='', stream = True, additional_fn=None):
    """
        ⭐单线程方法
        函数的说明请见 request_llms/bridge_all.py
    """
    chatbot.append((inputs, ""))
    yield from update_ui(chatbot=chatbot, history=history)

    api_key = llm_kwargs['custom_api_key']("DASHSCOPE_API_KEY")
    
    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        check_packages(["dashscope"])
    except:
        yield from update_ui_lastest_msg(_("导入软件依赖失败。使用该模型需要额外依赖，安装方法```pip install --upgrade dashscope```"),
                                         chatbot=chatbot, history=history, delay=0)
        return

    # 检查DASHSCOPE_API_KEY
    if api_key == "":
        yield from update_ui_lastest_msg(_("请配置 DASHSCOPE_API_KEY或自定义 通义千问(Qwen) API-KEY"),
                                         chatbot=chatbot, history=history, delay=0)
        return

    if additional_fn is not None:
        from core_functional import handle_core_functionality
        inputs, history = handle_core_functionality(additional_fn, inputs, history, chatbot)
        chatbot[-1] = (inputs, "")
        yield from update_ui(chatbot=chatbot, history=history)

    # 开始接收回复
    from .com_qwenapi import QwenRequestInstance
    sri = QwenRequestInstance(api_key)
    response = _("[Local Message] 等待 {} 响应中 ...").format(model_name)
    for response in sri.generate(inputs, llm_kwargs, history, system_prompt):
        chatbot[-1] = (inputs, response)
        yield from update_ui(chatbot=chatbot, history=history)

    log_chat(llm_model=llm_kwargs["llm_model"], input_str=inputs, output_str=response)
    # 总结输出
    if response == _("[Local Message] 等待 {} 响应中 ...").format(model_name):
        response = _("[Local Message] {} 响应异常").format(model_name)
    history.extend([inputs, response])
    yield from update_ui(chatbot=chatbot, history=history)