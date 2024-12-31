import time
import os
from toolbox import update_ui, get_conf, update_ui_lastest_msg, log_chat
from toolbox import check_packages, report_exception, have_any_recent_upload_image_files
from toolbox import ChatBotWithCookies
from shared_utils.scholar_navis.multi_lang import _

model_name = '智谱AI大模型'
zhipuai_default_model = 'glm-4'

def validate_key(api_key):
    if api_key == '': return False
    return True

def make_media_input(inputs, image_paths):
    for image_path in image_paths:
        inputs = inputs + f'<br/><br/><div align="center"><img src="file={os.path.abspath(image_path)}"></div>'
    return inputs

def predict_no_ui_long_connection(inputs:str, llm_kwargs:dict, history:list=[], sys_prompt:str="",
                                  observe_window:list=[], console_slience:bool=False):
    """
        ⭐多线程方法
        函数的说明请见 request_llms/bridge_all.py
    """
    watch_dog_patience = 5
    response = ""

    if llm_kwargs["llm_model"] == "zhipuai":
        llm_kwargs["llm_model"] = zhipuai_default_model

    api_key = llm_kwargs['custom_api_key']("ZHIPUAI_API_KEY")

    if validate_key(api_key) is False:
        raise RuntimeError(_('请配置ZHIPUAI_API_KEY或自定义 智谱(Zhipu) API-KEY'))

    # 开始接收回复
    from .com_zhipuglm import ZhipuChatInit
    zhipu_bro_init = ZhipuChatInit(api_key)
    for chunk, response in zhipu_bro_init.generate_chat(inputs, llm_kwargs, history, sys_prompt):
        if len(observe_window) >= 1:
            observe_window[0] = response
        if len(observe_window) >= 2:
            if (time.time() - observe_window[1]) > watch_dog_patience:
                raise RuntimeError(_("程序终止"))
    return response


def predict(inputs:str, llm_kwargs:dict, plugin_kwargs:dict, chatbot:ChatBotWithCookies,
            history:list=[], system_prompt:str='', stream:bool=True, additional_fn:str=None):
    """
        ⭐单线程方法
        函数的说明请见 request_llms/bridge_all.py
    """
    chatbot.append([inputs, ""])
    yield from update_ui(chatbot=chatbot, history=history)

    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        check_packages(["zhipuai"])
    except:
        yield from update_ui_lastest_msg(_("导入软件依赖失败。使用该模型需要额外依赖，安装方法```pip install --upgrade zhipuai```"),
            chatbot=chatbot, history=history, delay=0)
        return

    api_key = llm_kwargs['custom_api_key']("ZHIPUAI_API_KEY")
    if validate_key(api_key) is False:
        yield from update_ui_lastest_msg(lastmsg=f"[Local Message] {_('请配置ZHIPUAI_API_KEY或自定义 智谱(Zhipu) API-KEY')}", chatbot=chatbot, history=history, delay=0)
        return

    if additional_fn is not None:
        from core_functional import handle_core_functionality
        inputs, history = handle_core_functionality(additional_fn, inputs, history, chatbot)
        chatbot[-1] = [inputs, ""]
        yield from update_ui(chatbot=chatbot, history=history)

    if llm_kwargs["llm_model"] == "zhipuai":
        llm_kwargs["llm_model"] = zhipuai_default_model

    if llm_kwargs["llm_model"] in ["glm-4v"]:
        if (len(inputs) + sum(len(temp) for temp in history) + 1047) > 2000:
            chatbot.append((inputs, _("上下文长度超过glm-4v上限2000tokens，注意图片大约占用1,047个tokens")))
            yield from update_ui(chatbot=chatbot, history=history)
            return
        have_recent_file, image_paths = have_any_recent_upload_image_files(chatbot)
        if not have_recent_file:
            chatbot.append((inputs, _("没有检测到任何近期上传的图像文件，请上传jpg格式的图片，此外，请注意拓展名需要小写")))
            yield from update_ui(chatbot=chatbot, history=history, msg="等待图片") # 刷新界面
            return
        if have_recent_file:
            inputs = make_media_input(inputs, image_paths)
            chatbot[-1] = [inputs, ""]
            yield from update_ui(chatbot=chatbot, history=history)


    # 开始接收回复
    from .com_zhipuglm import ZhipuChatInit
    zhipu_bro_init = ZhipuChatInit(api_key)
    for chunk, response in zhipu_bro_init.generate_chat(inputs, llm_kwargs, history, system_prompt):
        chatbot[-1] = [inputs, response]
        yield from update_ui(chatbot=chatbot, history=history)
    history.extend([inputs, response])
    log_chat(llm_model=llm_kwargs["llm_model"], input_str=inputs, output_str=response)
    yield from update_ui(chatbot=chatbot, history=history)