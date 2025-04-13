'''
Original Author: gpt_academic@binary-husky

Modified by PureAmaya on 2025-04-11
- The JS events for the reset and stop buttons have been removed from the py file.
- Compatible with the new multilingual feature.

Modified by PureAmaya on 2025-03-18
- The initialization of JS is handed over to JS itself for execution.

Modified by PureAmaya on 2025-03-07
- Add the temporary environment variable GRADIO_TEMP_DIR.
- The deletion of the Gradio cache has been canceled. However, as a result, the Gradio cache folder is now located in the working directory for easier management.
- Remove some unnecessary settings.


Modified by PureAmaya on 2025-02-27
- Remove redundant features: warm_up_modules()
- Added privacy and security tips.
- Remove the loading of common functions.(core_functional.py)
- Remove log privacy reminder (as user input and output content have not been recorded for a long time).

Modified by PureAmaya on 2024-12-28
- Add i18n support
- Significant modifications for updating to Gradio 5.
- To ensure compatibility, support and interfaces for existing features have been removed.
- Adjust HTML footer, title, copyright, help documentation, AI warning, etc.
'''

from crazy_functional import get_crazy_functions
import os, json; os.environ['no_proxy'] = '*' # 避免代理网络产生意外污染
from shared_utils.scholar_navis.gpt_academic_handler import common_functions_panel_registrator,extract_useful_sentenses_panel
from themes.html_head_manager import head
from themes.common import run_advanced_plugin_launch_code
from multi_language import init_language,LANGUAGE_DISPLAY,MULTILINGUAL
from shared_utils.scholar_navis.const_and_singleton import footer,NOTIFICATION_ROOT_DIR
from dependencies.i18n import SUPPORT_DISPLAY_LANGUAGE
from dependencies import gradio_compatibility_layer  as gr
from shared_utils.fastapi_server import start_app
from shared_utils.cookie_manager import make_cookie_cache, make_history_cache
from themes.common import theme
from shared_utils.config_loader import get_conf
from toolbox import find_free_port, on_file_uploaded, ArgsGeneralWrapper, DummyWith
from request_llms.bridge_all import predict
from themes.theme import assign_user_uuid
import threading, webbrowser, time
from old_file_auto_cleaner import start_clear_old_files

# 统一读取配置
proxies, WEB_PORT, LLM_MODEL, CONCURRENT_COUNT, AUTHENTICATION = get_conf('proxies', 'WEB_PORT', 'LLM_MODEL',
                                                                          'CONCURRENT_COUNT', 'AUTHENTICATION')
CHATBOT_HEIGHT, LAYOUT, AVAIL_LLM_MODELS, AUTO_CLEAR_TXT = get_conf('CHATBOT_HEIGHT', 'LAYOUT', 'AVAIL_LLM_MODELS',
                                                                    'AUTO_CLEAR_TXT')
AUTO_CLEAR_TXT = get_conf('AUTO_CLEAR_TXT')
SSL_KEYFILE, SSL_CERTFILE = get_conf('SSL_KEYFILE', 'SSL_CERTFILE')


def main():

    # 非gradio部分，使用固定语言
    _ = lambda text:init_language(text,LANGUAGE_DISPLAY)


    global AVAIL_LLM_MODELS
    if LLM_MODEL not in AVAIL_LLM_MODELS: AVAIL_LLM_MODELS += [LLM_MODEL]

    # 如果WEB_PORT是-1, 则随机选取WEB端口
    PORT = find_free_port() if WEB_PORT <= 0 else WEB_PORT

    # 代理与自动更新
    from check_proxy import check_proxy
    proxy_info = check_proxy(proxies)

    # 构建gradio（多语言）
    apps = {}
    if MULTILINGUAL:
        for lang in SUPPORT_DISPLAY_LANGUAGE:
            apps.update(build_gradio(lang))
    else:
        apps.update(build_gradio(LANGUAGE_DISPLAY))

    # 运行一些异步任务：自动更新、打开浏览器页面、预热tiktoken模块
    run_delayed_tasks()

     # 启用清理进程
    start_clear_old_files()

    # 最后，正式开始服务
    start_app(apps,CONCURRENT_COUNT, AUTHENTICATION, PORT, SSL_KEYFILE, SSL_CERTFILE)


def build_gradio(lang:str):

    # gradio部分，使用偏好语言
    _ = lambda text: init_language(text, lang)

    help_menu_description = \
        _("""
    ## gpt_academic：
    Github源代码开源和更新[地址](https://github.com/binary-husky/gpt_academic),
    感谢热情的[开发者们](https://github.com/binary-husky/gpt_academic/graphs/contributors).


    ## Scholar Navis：
    **[Scholar Navis](https://github.com/PureAmaya/scholar_navis)为 gpt_academic的衍生作品**<br>
    关于对gpt_acadmic的修改和使用帮助，请阅读[README](https://github.com/PureAmaya/scholar_navis/blob/main/README.md).

    </br>普通对话使用说明: 1. 输入问题; 2. 点击提交
    </br></br>基础功能区使用说明: 1. 输入文本; 2. 点击任意基础功能区按钮
    </br></br>函数插件区使用说明: 1. 输入路径/问题, 或者上传文件; 2. 点击任意函数插件区按钮
    </br></br>如何保存对话: 点击保存当前的对话按钮
    </br></br>如何语音对话: 请阅读Wiki
    </br></br>要使用大模型，请在左上角的 API-KEY 中输入您的密钥。
    """)

    # 高级函数插件
    DEFAULT_FN_GROUPS = [] #get_conf('DEFAULT_FN_GROUPS') 目前用不到分组了
    plugins = get_crazy_functions(lang)
    all_plugin_groups = list(set([g for m, plugin in plugins.items() for g in plugin['Group'].split('|')]))
    if 'Scholar Navis' in all_plugin_groups: all_plugin_groups.remove('Scholar Navis')
    match_group = lambda tags, groups: any([g in groups for g in tags.split('|')])

    cancel_handles = []
    customize_btns = {}
    predefined_btns = {}

    # SCHOAR NAVIS
    title_html = f"<h1 align=\"center\">Scholar Navis</h1>"

    notification_lang_fp = os.path.join(NOTIFICATION_ROOT_DIR,lang,'notification.txt')
    notification_fp = os.path.join(NOTIFICATION_ROOT_DIR, 'notification.txt')

    if os.path.isfile(notification_lang_fp):
        path = notification_lang_fp
    else: path = notification_fp

    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            title_html = title_html + f'<p style="text-align: left; margin-left: 20px; margin-right: 20px;">{f.read()}</p>'

    with gr.Blocks(title="Scholar Navis", head=head(), theme=theme,analytics_enabled=False) as app_block:

        with gr.Row():
            floating_panel_switch_btn = gr.Button(value=_("上传与设置"),icon=os.path.join('themes','svg','gear.svg'),elem_id='floating_panel_switch_btn') # 的新浮动面板按钮
            dark_mode_btn = gr.Button(value=_('暗黑模式'),icon=os.path.join('themes','svg','dark_mode_toggle.svg'), elem_id='dark_mode_toggle')
            
        gr.HTML(title_html)
        gr.HTML('<strong>{}</strong>'.format(_("下方内容为 AI 生成，不代表任何立场，可能存在片面甚至错误。仅供参考，开发者及其组织不负任何责任")))
        gr.HTML('<strong>{}</strong>'.format(_('联网系统信息安全无法得到充分保证，最好是个人、小组织内使用，保证服务提供者可信，并且敏感信息最好不要上传。另外，当启用登录功能时，服务商能够储存您api-key，不推荐使用来路不明、不受信任的服务商')))

        cookies, web_cookie_cache = make_cookie_cache() # 定义 后端state（cookies）、前端（web_cookie_cache）两兄弟

        # 切换布局
        global CHATBOT_HEIGHT
        gr_L1 = lambda: gr.Row()
        gr_L2 = lambda scale, elem_id: gr.Column(scale=scale, elem_id=elem_id, min_width=400)
        if LAYOUT == "TOP-DOWN":
            gr_L1 = lambda: DummyWith()
            gr_L2 = lambda scale, elem_id: gr.Row()
            CHATBOT_HEIGHT /= 2

        with gr.Tab(label=_('对话功能'),id = '0',elem_classes='main_tab'):
            with gr_L1():
                with gr_L2(scale=2, elem_id="gpt-chat"):
                    chatbot = gr.Chatbot(type='messages',label=_("当前模型: {}").format(LLM_MODEL),
                                        elem_id="gpt-chatbot",show_copy_button=True,show_copy_all_button=True,
                                        height=580,sanitize_html=False)
                    if LAYOUT == "TOP-DOWN":  chatbot.height = CHATBOT_HEIGHT/3
                    history, history_cache, history_cache_update = make_history_cache() # 定义 后端state（history）、前端（history_cache）、后端setter（history_cache_update）三兄弟
                with gr_L2(scale=1, elem_id="gpt-panel"):
                    with gr.Accordion(label = _("输入区"), open=True, elem_id="input-panel") as area_input_primary:
                        with gr.Row():
                            txt = gr.Textbox(show_label=False, placeholder="Input question here.", elem_id='user_input_main',show_copy_button=True).style(container=False)
                        with gr.Row(elem_id="gpt-submit-row"):
                            multiplex_submit_btn = gr.Button(value=_("提交"), elem_id="elem_submit_visible", variant="primary")
                            multiplex_sel = gr.Dropdown(
                                choices=[
                                    "常规对话", # 应该是无用了
                                    "多模型对话", 
                                    # "智能上下文", 
                                    # "智能召回 RAG",
                                ], value="常规对话",
                                interactive=False, label='', show_label=False,visible=False,
                                elem_classes='normal_mut_select', elem_id="gpt-submit-dropdown").style(container=False)
                            submit_btn = gr.Button(value=_("提交"), elem_id="elem_submit", variant="primary", visible=False)
                        with gr.Row():
                            resetBtn = gr.Button(value=_("重置"), elem_id="elem_reset", variant="secondary"); resetBtn.style(size="sm")
                            stopBtn = gr.Button(value=_("停止"), elem_id="elem_stop", variant="secondary"); stopBtn.style(size="sm")
                            clearBtn = gr.Button(value =_("清除"), elem_id="elem_clear", variant="secondary", visible=True); clearBtn.style(size="sm")
                        with gr.Row():
                            status = gr.Markdown(value= _("Tip: 按Enter提交, 按Shift+Enter换行"), elem_id="state-panel")
                    
                    with gr.Accordion(label = _("Scholar Navis 功能区"), open=True, elem_id="sn-panel"):
                        plugins = common_functions_panel_registrator(plugins,lang)
                    


                    with gr.Accordion("函数插件区", open=False, elem_id="plugin-panel",visible=False):# 给按钮加功能
                        with gr.Row():
                            for index, (k, plugin) in enumerate(plugins.items()):
                                if not plugin.get("AsButton", True) or plugin.get("Group") == 'Scholar Navis': continue
                                visible = True if match_group(plugin['Group'], DEFAULT_FN_GROUPS) else False
                                variant = plugins[k]["Color"] if "Color" in plugin else "secondary"
                                info = plugins[k].get("Info", k)
                                btn_elem_id = f"plugin_btn_{index}"
                                plugin['Button'] = plugins[k]['Button'] = gr.Button(k, variant=variant,
                                    visible=visible, info_str=f'函数插件区: {info}', elem_id=btn_elem_id).style(size="sm")
                                plugin['ButtonElemId'] = btn_elem_id
                        with gr.Row():
                            with gr.Accordion("更多函数插件", open=True,visible=False,render=False):# 也有必要的东西，不敢删
                                dropdown_fn_list = ["点击这里输入「关键词」搜索插件"]
                                for k, plugin in plugins.items():
                                    if not match_group(plugin['Group'], DEFAULT_FN_GROUPS): continue
                                    if not plugin.get("AsButton", True): dropdown_fn_list.append(k)     # 排除已经是按钮的插件
                                    elif plugin.get('AdvancedArgs', False): dropdown_fn_list.append(k)  # 对于需要高级参数的插件，亦在下拉菜单中显示
                                with gr.Row():
                                    dropdown = gr.Dropdown(dropdown_fn_list, value=r"点击这里输入「关键词」搜索插件", label="", show_label=False).style(container=False)
                                with gr.Row():
                                    plugin_advanced_arg = gr.Textbox(show_label=True, label="高级参数输入区", visible=False, elem_id="advance_arg_input_legacy",
                                                                    placeholder="这里是特殊函数插件的高级参数输入区").style(container=False)
                                with gr.Row():
                                    switchy_bt = gr.Button(r"请先从插件列表中选择", variant="secondary", elem_id="elem_switchy_bt").style(size="sm")
                        #with gr.Row():
        t = gr.Tab(label = _('摘取有用语句'),id=1,elem_classes='main_tab')

        # 左上角工具栏定义
        from themes.gui_toolbar import define_gui_toolbar
        tooltip_panel,init_event_list, max_length_sl, system_prompt, file_upload_2, md_dropdown, top_p, temperature,user_custom_data = \
            define_gui_toolbar(chatbot, help_menu_description,lang)

        # 插件二级菜单的实现
        from themes.gui_advanced_plugin_class import define_gui_advanced_plugin_class
        plugin_arg_menu,new_plugin_callback, route_switchy_bt_with_arg, usr_confirmed_arg,usr_editing_arg,plugin_arg_list= \
            define_gui_advanced_plugin_class(plugins,lang)
        
        t.__enter__()
        # 在这里注册摘取功能
        extract_useful_sentenses_panel(cookies,md_dropdown,temperature,top_p,user_custom_data,lang)
        t.__exit__()

        gr.HTML(footer)

        # 整理反复出现的控件句柄组合
        input_combo = [cookies, max_length_sl, md_dropdown, txt,  top_p, temperature, chatbot, history, system_prompt, plugin_advanced_arg,user_custom_data]
        input_combo_order = ["cookies", "max_length_sl", "md_dropdown", "txt", "top_p", "temperature", "chatbot", "history", "system_prompt", "plugin_advanced_arg",'custom_api_key']
        output_combo = [cookies, chatbot, history, status]
        predict_args = dict(fn=ArgsGeneralWrapper(predict), inputs=[*input_combo, gr.State(True)], outputs=output_combo)
        
        # 提交按钮、重置按钮
        multiplex_submit_btn.click(
            None, [multiplex_sel], None, js="""(multiplex_sel)=>multiplex_function_begin(multiplex_sel)""")
        txt.submit(
            None, [multiplex_sel], None, js="""(multiplex_sel)=>multiplex_function_begin(multiplex_sel)""")
        multiplex_sel.select(
            None, [multiplex_sel], None, js="""(multiplex_sel)=>run_multiplex_shift(multiplex_sel)""")
        cancel_handles.append(submit_btn.click(**predict_args))
        resetBtn.click(None, None, [chatbot, history, status], js='reset_conversation')   # 先在前端快速清除chatbot&status
        reset_server_side_args = (lambda history: ('',[], [], _("已重置"), json.dumps(history)), [history], [txt,chatbot, history, status, history_cache])
        resetBtn.click(*reset_server_side_args)    # 再在后端清除history，把history转存history_cache备用
        clearBtn.click(None, None, [txt,txt], js='''()=>{return ["", ""];}''')
        if AUTO_CLEAR_TXT:
            submit_btn.click(None, None, [txt,txt], js='''()=>{return ["", ""];}''')

        for btn in customize_btns.values():
            click_handle = btn.click(fn=ArgsGeneralWrapper(predict), inputs=[*input_combo, gr.State(True), gr.State(btn.value)], outputs=output_combo)
            cancel_handles.append(click_handle)
        # 文件上传区，接收文件后与chatbot的互动
        file_upload_2.upload(on_file_uploaded, [file_upload_2, chatbot, txt, cookies], [chatbot, txt, cookies])
        
        # 函数插件-固定按钮区
        for item in plugins.items():
            k = item[0]
            if plugins[k].get("Class", None):
                plugins[k]["JsMenu"] = plugins[k]["Class"]().get_js_code_for_generating_menu(lang)
            if not plugins[k].get("AsButton", True): continue

            def aaa(txt,plugin_advanced_arg,gr_button):
                plugin_content = plugins[gr_button]
                return run_advanced_plugin_launch_code(gr_button,plugin_content,txt,plugin_advanced_arg)
            
            plugins[k]["Button"].click(fn=aaa,inputs=[txt,plugin_advanced_arg,plugins[k]["Button"]], 
                                                    outputs=[plugin_arg_menu,new_plugin_callback,usr_editing_arg] + plugin_arg_list)
            
            
        # 函数插件-下拉菜单与随变按钮的互动（新版-更流畅）
        dropdown.select(None, [dropdown], None, js="""(dropdown)=>run_dropdown_shift(dropdown)""")

        # 模型切换时的回调
        def on_md_dropdown_changed(request:gr.Request,k):
            lang = request.cookies.get('lang')
            _ = lambda txt: init_language(txt, lang)
            return {chatbot: gr.update(label=_("当前模型: {}").format(k))}
        md_dropdown.select(on_md_dropdown_changed, [md_dropdown], [chatbot])

        # switchy_bt.click(None, [switchy_bt], None, js="(switchy_bt)=>on_flex_button_click(switchy_bt)")
        
        # 新一代插件的高级参数区确认按钮（隐藏）
        click_handle_ng = new_plugin_callback.click(route_switchy_bt_with_arg,
            [
                gr.State(["new_plugin_callback", "usr_confirmed_arg"] + input_combo_order), # 第一个参数: 指定了后续参数的名称
                new_plugin_callback, usr_confirmed_arg, *input_combo                        # 后续参数: 真正的参数
            ], output_combo)
        cancel_handles.append(click_handle_ng)
        
        # 终止按钮的回调函数注册
        stopBtn.click(fn=None, inputs=None, outputs=None, cancels=cancel_handles)
        plugins_as_btn = {name:plugin for name, plugin in plugins.items() if plugin.get('Button', None)}


        # 生成当前浏览器窗口的uuid（刷新失效）
        app_block.load(assign_user_uuid, inputs=[cookies], outputs=[cookies])

        # 左上角设定与面板开关按钮
        floating_panel_switch_btn.click(fn=lambda:gr.update(visible=True),outputs=tooltip_panel)
        
        # 暗黑模式切换
        dark_mode_btn.click(None,None,None,js="""dark_mode_toggle""")

        # i8n （该方案暂时废弃）
        # 获取所有已追踪的组件列表 (在定义完所有追踪组件之后!)
        # 用 list() 创建一个快照，因为 WeakSet 不能直接用于 outputs
        #tracked_components_list = list(gr.TRACKED_COMPONENTS_FOR_I18N)

        #_init_language = {
        #    'fn':lambda x,y:change_language_for_gradio(x, y, tracked_components_list),
        #    'inputs':[language_state,lang_dropdown],
        #    'outputs':[language_state] + tracked_components_list
        #}
        #lang_dropdown.change(**_init_language)
        # 初始化的时候，顺便初始化一下语言
        #init_event_list.append(_init_language)

        # 初始化的脚本
        for event in init_event_list:app_block.load(**event)

    return {lang:app_block}

    # Gradio的inbrowser触发不太稳定，回滚代码到原始的浏览器打开函数

def run_delayed_tasks():
    # 非gradio部分，使用固定语言
    _ = lambda text: init_language(text, LANGUAGE_DISPLAY)


    print()
    print(_("如果浏览器没有自动打开，请复制并转到以下URL:"))
    print(f"http://localhost:{WEB_PORT}\n")

    def open_browser(): time.sleep(2); webbrowser.open_new_tab(f"http://localhost:{WEB_PORT}")

    if get_conf('AUTO_OPEN_BROWSER'):
        threading.Thread(target=open_browser, name="open-browser", daemon=True).start() # 打开浏览器页面


if __name__ == "__main__":
    main()
