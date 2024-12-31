import gradio_compatibility_layer as gr
import json
from toolbox import ArgsGeneralWrapper, HotReload
from gradio_modal import Modal
from shared_utils.scholar_navis.multi_lang import _

# 这里后续可以再优化一下，添加一些自定义组件什么的

def define_gui_advanced_plugin_class(plugins):
    # 定义新一代插件的高级参数区
    with Modal(visible=False, elem_id="plugin_arg_menu",elem_classes='modal',allow_user_close=True) as plugin_arg_menu:
        
        # 这个隐藏textbox负责装入当前弹出插件的属性
        usr_editing_arg = gr.Textbox(show_label=False, placeholder=_("请输入"), lines=1, visible=False,
                elem_id="invisible_current_pop_up_plugin_arg")
        usr_confirmed_arg = gr.Textbox(label='final',show_label=False, placeholder=_("请输入"), lines=1, visible=False,
                elem_id=f"invisible_current_pop_up_plugin_arg_final")
        
        with gr.Tab(_('选择插件参数')):
            plugin_arg_list = [];
            with gr.Column():
                for u in range(8):
                    _textbox_btn = gr.Textbox('.',show_label=True, label="T1", placeholder=_("请输入"), lines=1, visible=False, elem_id=f"plugin_arg_txt_{u}",interactive=True)
                    _textbox_btn.change(None,inputs=usr_editing_arg,outputs=usr_confirmed_arg,js='(usr_editing_arg)=>execute_current_pop_up_plugin(usr_editing_arg)')
                    plugin_arg_list.append(_textbox_btn)
            
                for u in range(8):
                    _dp = gr.Dropdown(label="T1", value=".", choices=['.'], visible=True, elem_id=f"plugin_arg_drop_{u}", interactive=True,elem_classes='dropdown_in_modal')
                    # 添加独立JS事件，防止意外关闭modal
                    _dp.blur(None,None,None,js='BanModalPointEvents')
                    _dp.change(None,inputs=usr_editing_arg,outputs=usr_confirmed_arg,js='(usr_editing_arg)=>execute_current_pop_up_plugin(usr_editing_arg)')
                    plugin_arg_list.append(_dp)
        with gr.Tab(_('使用说明')):
            gr.Markdown(_('在 <b>辅助指令</b> 中，可以看到每个功能根据不同需求而写的详细说明'))
        with gr.Row():

            arg_confirm_btn = gr.Button(_("确认参数并执行"), variant="primary")
            arg_confirm_btn.style(size="sm")

            arg_cancel_btn = gr.Button(_("取消"), variant="primary")
            arg_cancel_btn.click(fn=lambda:gr.update(visible=False),inputs=None,outputs=plugin_arg_menu)
            arg_cancel_btn.style(size="sm")

            arg_confirm_btn.click(fn=lambda:gr.update(visible=False), inputs=None, outputs=plugin_arg_menu, js='function abbrgigr(){document.getElementById("invisible_callback_btn_for_plugin_exe").click();}')
            invisible_callback_btn_for_plugin_exe = gr.Button(_("未选定任何插件"), variant="secondary", visible=False, elem_id="invisible_callback_btn_for_plugin_exe",size='sm')
            # 随变按钮的回调函数注册
            def route_switchy_bt_with_arg(request: gr.Request, input_order, *arg):
                arguments = {k:v for k,v in zip(input_order, arg)}      # 重新梳理输入参数，转化为kwargs字典
                which_plugin = arguments.pop('new_plugin_callback')     # 获取需要执行的插件名称
                if which_plugin in [_("未选定任何插件")]: return
                usr_confirmed_arg = arguments.pop('usr_confirmed_arg')  # 获取插件参数
                arg_confirm: dict = {}
                usr_confirmed_arg_dict = json.loads(usr_confirmed_arg)  # 读取插件参数
                for arg_name in usr_confirmed_arg_dict:
                    arg_confirm.update({arg_name: str(usr_confirmed_arg_dict[arg_name]['user_confirmed_value'])})

                if plugins[which_plugin].get("Class", None) is not None:  # 获取插件执行函数
                    plugin_obj = plugins[which_plugin]["Class"]
                    if plugins[which_plugin].get('ClassHotReload',False):# 让所谓的新一代也支持热更新，不太优雅，先自己凑合用吧
                        plugin_exe = HotReload(plugin_obj.execute)
                    else:plugin_exe = plugin_obj.execute
                else:
                    plugin_exe = plugins[which_plugin]["Function"]

                arguments['plugin_advanced_arg'] = arg_confirm          # 更新高级参数输入区的参数
                if arg_confirm.get('main_input', None) is not None:     # 更新主输入区的参数
                    arguments['txt'] = arg_confirm['main_input']

                # 万事俱备，开始执行
                yield from ArgsGeneralWrapper(plugin_exe)(request, *arguments.values())

    return plugin_arg_menu,invisible_callback_btn_for_plugin_exe, route_switchy_bt_with_arg, usr_confirmed_arg,usr_editing_arg,plugin_arg_list

