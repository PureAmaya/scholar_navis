'''
Original Author: gpt_academic@binary-husky

Modified by PureAmaya on 2025-03-06
- Remove unnecessary print.
- Due to Alibaba Cloud's introduction of a new inference model, the Qwen series models have been moved here. User-friendly names have also been added for distinction.

Modified by PureAmaya on 2025-02-21
- Compatible with DeepSeek's inference model(R1)

Modified by PureAmaya on 2024-12-28
- Compatible with custom API functionality on the web.
- Add localization support.
'''

import json
import time
import logging
import traceback
import requests
from shared_utils.config_loader import get_conf
from multi_language import init_language
from dependencies.i18n.gradio_i18n import HTML
from shared_utils.advanced_markdown_format import md2html

_ = init_language

# config_private.py放自己的秘密如API和代理网址
# 读取时首先看是否存在私密的config_private配置文件（不受git管控），如果有，则覆盖原config文件
from toolbox import (
    update_ui,
    is_the_upload_folder,
)

proxies, TIMEOUT_SECONDS, MAX_RETRY = get_conf(
    "proxies", "TIMEOUT_SECONDS", "MAX_RETRY"
)

timeout_bot_msg = (
    "[Local Message] Request timeout. Network error. Please check proxy settings in config.py."
    + "网络错误，检查代理服务器是否可用，以及代理设置的格式是否正确，格式须是[协议]://[地址]:[端口]，缺一不可。"
)


def get_full_error(chunk, stream_response):
    """
    尝试获取完整的错误信息
    """
    while True:
        try:
            chunk += next(stream_response)
        except:
            break
    return chunk


def decode_chunk(chunk):
    """
    用于解读"content"和"finish_reason"的内容
    """
    chunk = chunk.decode()
    response = ""
    reasoning_content = ""
    finish_reason = "False"
    try:
        chunk = json.loads(chunk[6:])
    except:
        response = ""
        finish_reason = chunk
    # 错误处理部分
    if "error" in chunk:
        response = "API_ERROR"
        try:
            chunk = json.loads(chunk)
            finish_reason = chunk["error"]["code"]
        except:
            finish_reason = "API_ERROR"
        return response, reasoning_content, finish_reason

    try:
        response = chunk["choices"][0]["delta"]["content"]
    except:
        pass
    try:
        reasoning_content = chunk["choices"][0]["delta"]["reasoning_content"]
    except:
        pass
    try:
        finish_reason = chunk["choices"][0]["finish_reason"]
    except:
        pass

    if not response:response = ""
    if not reasoning_content:reasoning_content = ""

    return response, reasoning_content, finish_reason


def generate_message(input, model, key, history, max_output_token, system_prompt, temperature):
    """
    整合所有信息，选择LLM模型，生成http请求，为发送请求做准备
    """
    api_key = f"Bearer {key}"

    headers = {"Content-Type": "application/json", "Authorization": api_key}

    conversation_cnt = len(history) // 2

    messages = [{"role": "system", "content": system_prompt}]
    if conversation_cnt:
        for index in range(0, 2 * conversation_cnt, 2):
            what_i_have_asked = {}
            what_i_have_asked["role"] = "user"
            what_i_have_asked["content"] = history[index]
            what_gpt_answer = {}
            what_gpt_answer["role"] = "assistant"
            what_gpt_answer["content"] = history[index + 1]
            if what_i_have_asked["content"] != "":
                if what_gpt_answer["content"] == "":
                    continue
                if what_gpt_answer["content"] == timeout_bot_msg:
                    continue
                messages.append(what_i_have_asked)
                messages.append(what_gpt_answer)
            else:
                messages[-1]["content"] = what_gpt_answer["content"]
    what_i_ask_now = {}
    what_i_ask_now["role"] = "user"
    what_i_ask_now["content"] = input
    messages.append(what_i_ask_now)
    playload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": True,
        "max_tokens": max_output_token,
    }

    return headers, playload


def get_predict_function(
        api_key_conf_name,
        friendly_name,
        max_output_token,
        disable_proxy = False
    ):
    """
    为openai格式的API生成响应函数，其中传入参数：
    api_key_conf_name：
        `config.py`中此模型的APIKEY的名字，例如"YIMODEL_API_KEY"
    max_output_token：
        每次请求的最大token数量，例如对于01万物的yi-34b-chat-200k，其最大请求数为4096
        ⚠️请不要与模型的最大token数量相混淆。
    disable_proxy：
        是否使用代理，True为不使用，False为使用。
    """

    def predict_no_ui_long_connection(
        inputs,
        llm_kwargs,
        history=[],
        sys_prompt="",
        observe_window=None,
        console_slience=True,
    ):
        """
        发送至chatGPT，等待回复，一次性完成，不显示中间过程。但内部用stream的方法避免中途网线被掐。
        inputs：
            是本次问询的输入
        sys_prompt:
            系统静默prompt
        llm_kwargs：
            chatGPT的内部调优参数
        history：
            是之前的对话列表
        observe_window = None：
            用于负责跨越线程传递已经输出的部分，大部分时候仅仅为了fancy的视觉效果，留空即可。observe_window[0]：观测窗。observe_window[1]：看门狗
        """
        APIKEY = llm_kwargs['custom_api_key'](api_key_conf_name)
        watch_dog_patience = 5  # 看门狗的耐心，设置5秒不准咬人(咬的也不是人
        if len(APIKEY) == 0:
            raise RuntimeError(_("APIKEY为空,请检查配置文件的{}。或者可以自定义 {} API-KEY").format(api_key_conf_name,friendly_name))
        if inputs == "":
            inputs = "你好👋"
        headers, playload = generate_message(
            input=inputs,
            model=llm_kwargs["llm_model"],
            key=APIKEY,
            history=history,
            max_output_token=max_output_token,
            system_prompt=sys_prompt,
            temperature=llm_kwargs["temperature"],
        )
        retry = 0
        while True:
            try:
                from .bridge_all import model_info

                endpoint = model_info[llm_kwargs["llm_model"]]["endpoint"]
                if not disable_proxy:
                    response = requests.post(
                        endpoint,
                        headers=headers,
                        proxies=proxies,
                        json=playload,
                        stream=True,
                        timeout=TIMEOUT_SECONDS,
                    )
                else:
                    response = requests.post(
                        endpoint,
                        headers=headers,
                        json=playload,
                        stream=True,
                        timeout=TIMEOUT_SECONDS,
                    )
                break
            except:
                retry += 1
                traceback.print_exc()
                if retry > MAX_RETRY:
                    raise TimeoutError
                if MAX_RETRY != 0:
                    print(f"{_('请求超时，正在重试')} ({retry}/{MAX_RETRY}) ……")

        stream_response = response.iter_lines()
        result = ""
        finish_reason = ""
        while True:
            try:
                chunk = next(stream_response)
            except StopIteration:
                if result == "":
                    raise RuntimeError(f"{_('获得空的回复，可能原因: ')}{finish_reason}")
                break
            except requests.exceptions.ConnectionError:
                chunk = next(stream_response)  # 失败了，重试一次？再失败就没办法了。
            response_text, reasoning_content,finish_reason = decode_chunk(chunk)
            # 返回的数据流第一次为空，继续等待
            if reasoning_content == '' and response_text == "" and finish_reason != "False":
                continue
            if response_text == "API_ERROR" and (
                finish_reason != "False" or finish_reason != "stop"
            ):
                chunk = get_full_error(chunk, stream_response)
                chunk_decoded = chunk.decode()
                print(chunk_decoded)
                raise RuntimeError(
                    _('API异常,请检测终端输出。可能的原因是: {}').format(finish_reason)
                )
            if chunk:
                try:
                    if finish_reason == "stop":
                        logging.info(f"[response] {result}")
                        break
                    if response_text:result += response_text
                    if observe_window is not None:
                        # 观测窗，把已经获取的数据显示出去
                        if len(observe_window) >= 1:
                            observe_window[0] += response_text
                        # 看门狗，如果超过期限没有喂狗，则终止
                        if len(observe_window) >= 2:
                            if (time.time() - observe_window[1]) > watch_dog_patience:
                                raise RuntimeError("用户取消了程序。")
                except Exception as e:
                    traceback.print_exc()
                    chunk = get_full_error(chunk, stream_response)
                    chunk_decoded = chunk.decode()
                    error_msg = chunk_decoded
                    print(error_msg)
                    raise RuntimeError(_("Json解析不合常规"))
        return result

    def predict(
        inputs,
        llm_kwargs,
        plugin_kwargs,
        chatbot,
        history=[],
        system_prompt="",
        stream=True,
        additional_fn=None,
    ):
        """
        发送至chatGPT，流式获取输出。
        用于基础的对话功能。
        inputs 是本次问询的输入
        top_p, temperature是chatGPT的内部调优参数
        history 是之前的对话列表（注意无论是inputs还是history，内容太长了都会触发token数量溢出的错误）
        chatbot 为WebUI中显示的对话列表，修改它，然后yeild出去，可以直接修改对话界面内容
        additional_fn代表点击的哪个按钮，按钮见functional.py
        """
        lang = chatbot.get_language()
        _ = lambda text: init_language(text, lang)
        APIKEY = llm_kwargs['custom_api_key'](api_key_conf_name)

        if len(APIKEY) == 0:
            raise RuntimeError(_("APIKEY为空,请检查配置文件的{}。或者可以自定义 {} API-KEY").format(api_key_conf_name,friendly_name))
        if inputs == "":
            inputs = "你好👋"
        if additional_fn is not None:
            from core_functional import handle_core_functionality

            inputs, history = handle_core_functionality(
                additional_fn, inputs, history, chatbot
            )
        logging.info(f"[raw_input] {inputs}")
        chatbot.append((inputs, ""))
        yield from update_ui(
            chatbot=chatbot, history=history, msg=_("等待响应")
        )  # 刷新界面

        # check mis-behavior
        if is_the_upload_folder(inputs):
            chatbot[-1] = (
                inputs,
                f"[Local Message] 检测到操作错误！当您上传文档之后，需点击“**函数插件区**”按钮进行处理，请勿点击“提交”按钮或者“基础功能区”按钮。",
            )
            yield from update_ui(
                chatbot=chatbot, history=history, msg="正常"
            )  # 刷新界面
            time.sleep(2)

        headers, playload = generate_message(
            input=inputs,
            model=llm_kwargs["llm_model"],
            key=APIKEY,
            history=history,
            max_output_token=max_output_token,
            system_prompt=system_prompt,
            temperature=llm_kwargs["temperature"],
        )

        history.append(inputs)
        history.append("")
        retry = 0
        while True:
            try:
                from .bridge_all import model_info

                endpoint = model_info[llm_kwargs["llm_model"]]["endpoint"]
                if not disable_proxy:
                    response = requests.post(
                        endpoint,
                        headers=headers,
                        proxies=proxies,
                        json=playload,
                        stream=True,
                        timeout=TIMEOUT_SECONDS,
                    )
                else:
                    response = requests.post(
                        endpoint,
                        headers=headers,
                        json=playload,
                        stream=True,
                        timeout=TIMEOUT_SECONDS,
                    )
                break
            except:
                retry += 1
                chatbot[-1] = (chatbot[-1][0], timeout_bot_msg)
                retry_msg = (
                    f", Retrying ({retry}/{MAX_RETRY}) ……" if MAX_RETRY > 0 else ""
                )
                yield from update_ui(
                    chatbot=chatbot, history=history, msg=_("请求超时") + retry_msg
                )  # 刷新界面
                if retry > MAX_RETRY:
                    raise TimeoutError

        gpt_replying_buffer = ""
        gpt_reasoning_buffer = ''

        stream_response = response.iter_lines()
        while True:
            try:
                chunk = next(stream_response)
            except StopIteration:
                break
            except requests.exceptions.ConnectionError:
                chunk = next(stream_response)  # 失败了，重试一次？再失败就没办法了。
            response_text,reasoning_content, finish_reason = decode_chunk(chunk)
            # 返回的数据流第一次为空，继续等待
            if reasoning_content == '' and response_text == "" and finish_reason != "False":
                status_text = f"finish_reason: {finish_reason}"
                yield from update_ui(
                    chatbot=chatbot, history=history, msg=status_text
                )
                continue
            if chunk:
                try:
                    if response_text == "API_ERROR" and (
                        finish_reason != "False" or finish_reason != "stop"
                    ):
                        chunk = get_full_error(chunk, stream_response)
                        chunk_decoded = chunk.decode()
                        chatbot[-1] = (
                            chatbot[-1][0],
                            _("[Local Message] {},获得以下报错信息：\n").format(finish_reason)
                            + chunk_decoded,
                        )
                        yield from update_ui(
                            chatbot=chatbot,
                            history=history,
                            msg=_("API异常: ") + chunk_decoded,
                        )  # 刷新界面
                        print(chunk_decoded)
                        return

                    if finish_reason == "stop":
                        logging.info(f"[response] {gpt_replying_buffer}")
                        break

                    status_text = f"finish_reason: {finish_reason}"
                    if response_text:gpt_replying_buffer += response_text
                    if reasoning_content:gpt_reasoning_buffer += reasoning_content
                    # 如果这里抛出异常，一般是文本过长，详情见get_full_error的输出
                    history[-1] = gpt_replying_buffer

                    # 兼容深度思考
                    if gpt_reasoning_buffer:
                        chatbot_assistant =HTML(''' 
                        <p>
                        <details open>
                        <summary>{}</summary>
                        <blockquote><p>
                        {}
                        </p></blockquote>
                        </details>  
                        </p>
                        {}
                        '''.format(_('深度思考'),md2html(gpt_reasoning_buffer),md2html(gpt_replying_buffer))
                        )

                    else:chatbot_assistant = history[-1]

                    chatbot[-1] = (history[-2], chatbot_assistant)
                    yield from update_ui(
                        chatbot=chatbot, history=history, msg=status_text
                    )  # 刷新界面
                except Exception as e:
                    yield from update_ui(
                        chatbot=chatbot, history=history, msg=_("Json解析不合常规")
                    )  # 刷新界面
                    chunk = get_full_error(chunk, stream_response)
                    chunk_decoded = chunk.decode()
                    chatbot[-1] = (
                        chatbot[-1][0],
                        f"[Local Message] {_('解析错误,获得以下报错信息：')}\n" + chunk_decoded,
                    )
                    yield from update_ui(
                        chatbot=chatbot, history=history, msg=_("Json异常") + e
                    )  # 刷新界面
                    print(chunk_decoded)
                    return

    return predict_no_ui_long_connection, predict
