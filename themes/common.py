'''
Original Author: gpt_academic@binary-husky

Modified by PureAmaya on 2025-03-18
- Change the local JS to defer loading to ensure the correct loading sequence.

Modified by PureAmaya on 2024-12-28
- Add Gradio 5 theme
- Remove some redundant features
- Add scholar_naivs js
- Some JS functionalities have been moved here (and implemented using Gradio components).
'''

from shared_utils.config_loader import get_conf
from functools import lru_cache
import base64
import json
import gradio as gr

theme = gr.themes.Base(
        secondary_hue="indigo",
        neutral_hue="gray",
        radius_size="xxl",
        font=['Source Han Sans', 'Source Han Sans', 'Source Han Sans', 'Source Han Sans'],
        font_mono=['Source Han Sans', 'Source Han Sans', 'Source Han Sans', 'Source Han Sans'],
    ).set(
        code_background_fill='*neutral_300',
        code_background_fill_dark='*neutral_600',
        shadow_drop='0 1px 5px 0 rgb(0 0 0 / 0.1)',
        shadow_drop_lg='0 2px 5px 0 rgb(0 0 0 / 0.1)',
        checkbox_border_width='*panel_border_width',
        input_background_fill='white',
        input_border_color='*neutral_300',
        input_border_width='1px'
    )


def minimize_js(common_js_path):
    try:
        import rjsmin
        import hashlib
        import glob
        import os
        # clean up old minimized js files, matching `common_js_path + '.min.*'`
        for old_min_js in glob.glob(common_js_path + '.min.*.js'):
            os.remove(old_min_js)
        # use rjsmin to minimize `common_js_path`
        c_jsmin = rjsmin.jsmin
        with open(common_js_path, "r") as f:
            js_content = f.read()
        minimized_js_content = c_jsmin(js_content)
        # compute sha256 hash of minimized js content
        sha_hash = hashlib.sha256(minimized_js_content.encode()).hexdigest()[:8]
        minimized_js_path = common_js_path + '.min.' + sha_hash + '.js'
        # save to minimized js file
        with open(minimized_js_path, "w") as f:
            f.write(minimized_js_content)
        # return minimized js file path
        return minimized_js_path
    except:
        return common_js_path

@lru_cache
def get_common_html_javascript_code():
    js = "\n"
    common_js_path_list = [
        "themes/common.js",
        "themes/scholar_navis/notify.js",
        "themes/scholar_navis/custom_api_key.js",
        "themes/scholar_navis/scholar_navis_init.js",
        "themes/init.js",
    ]
    # 解释：除init.js外，其余的js要么是第三方的独立库，要么就是封装的方法

    for common_js_path in common_js_path_list:
        if '.min.' not in common_js_path:
            minimized_js_path = minimize_js(common_js_path)
        else:
            minimized_js_path = common_js_path
        jsf = f"/file={minimized_js_path}"
        js += f"""<script defer src="{jsf}"></script>\n"""

    return js


########### 下面是从 common.js 转移到python的部分 ##########


def register_advanced_plugin_init_code(key, code):
    # 检查 key 是否在插件初始化信息库中
    if key not in plugin_init_info_lib:
        plugin_init_info_lib[key] = {}

    # 将代码存储在字典中
    plugin_init_info_lib[key]['secondary_menu_code'] = code
    

plugin_init_info_lib = {}


def call_plugin(plugin,advance_arg_input_legacy):
    gui_args = {}

    if len(advance_arg_input_legacy) != 0:
        gui_args["advanced_arg"] = {
            'user_confirmed_value': advance_arg_input_legacy
        }

    # 执行插件
    # usr_confirmed_arg
    #push_data_to_gradio_component(json.dumps(gui_args), "invisible_current_pop_up_plugin_arg_final", "string")
    # invisible_callback_btn_for_plugin_exe
    #push_data_to_gradio_component(current_btn_name, "invisible_callback_btn_for_plugin_exe", "string")
    
    # plugin_arg_menu,usr_confirmed_arg,invisible_callback_btn_for_plugin_exe
    return gr.update(visible=False),json.dumps(gui_args),plugin[0]
    

def run_advanced_plugin_launch_code(name,plugin_content,txt,plugin_advanced_arg):

    # 分配按钮和菜单数据
    # usr_confirmed_arg
    #push_data_to_gradio_component(gui_base64_string, "invisible_current_pop_up_plugin_arg", "string")
    # new_plugin_callback
    #push_data_to_gradio_component(btn_name, "invisible_callback_btn_for_plugin_exe", "string")
    usr_editing_arg = base64.b64encode(plugin_content['JsMenu'].encode('utf-8')).decode('utf-8') # JSMenu生成那边已经没有base64编码了
    gui_json_data = json.loads(plugin_content['JsMenu'])
    
    # 使参数菜单显现
    text_cnt = 0
    dropdown_cnt = 8
    
    output_gr = [gr.update(visible=False,render=False) for i in range(16)]
    
    for key in gui_json_data:
        gui_args = json.loads(gui_json_data[key])

        if (gui_args['type'] == 'string'):
            edit_para ={}
            
            if (key == "main_input"):
                #为了与旧插件兼容，生成菜单时，自动加载输入栏的值
                edit_para.update({'value': txt})

            elif (key == "advanced_arg") :
                # 为了与旧插件兼容，生成菜单时，自动加载旧高级参数输入区的值
                edit_para.update({'value': plugin_advanced_arg})
            
            else:
                edit_para.update({'value': gui_args['default_value']})
            
            output_gr[text_cnt] = gr.update(visible=True,render=True,label=gui_args['title'] ,info = gui_args['description'] ,placeholder=gui_args['description'],**edit_para)
            text_cnt += 1;

        if (gui_args['type'] == 'dropdown'):
            output_gr[dropdown_cnt].update(visible=True,render=True,choices=gui_args['options'],label=gui_args['title'],info = gui_args['description'],value=gui_args['default_value'])
            dropdown_cnt += 1;

    # plugin_arg_menu,  invisible_callback_btn_for_plugin_exe （new_plugin_callback）,usr_editing_arg , 浮动面板上的组件
    return gr.update(visible=True),name,usr_editing_arg,*output_gr
