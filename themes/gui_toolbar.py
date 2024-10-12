import copy
import gradio as gr
from themes.theme import advanced_css
from toolbox import get_conf
from shared_utils.scholar_navis.user_custom_manager import DEFAULT_USER_CUSTOM,SUPPORT_API_PROVIDER,get_api_key,get_url_redirect_domain,get_url_redirect_path

ALLOW_CUSTOM_API_KEY = get_conf('ALLOW_CUSTOM_API_KEY')

def define_gui_toolbar(AVAIL_LLM_MODELS, LLM_MODEL, INIT_SYS_PROMPT, THEME, AVAIL_THEMES, ADD_WAIFU, help_menu_description):
    with gr.Floating(variant='panel',init_x="0%", init_y="0%", visible=True, width=None, drag="forbidden", elem_id="tooltip",equal_height=True):
        with gr.Row():
            with gr.Tab("上传文件", elem_id="interact-panel"):
                # gr.HTML(value='1',elem_id='local_pdf_optimizer',label='pdf优化器')
                # gr.Markdown('------------------------------------------')
                gr.Markdown("请上传本地文件/压缩包供“函数插件区”功能调用。请注意: 上传文件后会自动把输入区修改为相应路径。")
                file_upload_2 = gr.Files(label="任何文件, 推荐上传压缩文件(zip, tar)", file_count="multiple", elem_id="elem_upload_float")
            with gr.Tab("更换模型", elem_id="interact-panel") as model_switch_tab:
                md_dropdown = gr.Dropdown(AVAIL_LLM_MODELS, value=LLM_MODEL, elem_id="elem_model_sel", label="更换LLM模型/请求源").style(container=False)
                top_p = gr.Slider(minimum=-0, maximum=1.0, value=1.0, step=0.01,interactive=True, label="Top-p (nucleus sampling)",)
                temperature = gr.Slider(minimum=-0, maximum=2.0, value=1.0, step=0.01, interactive=True, label="Temperature", elem_id="elem_temperature")
                max_length_sl = gr.Slider(minimum=256, maximum=1024*32, value=4096, step=128, interactive=True, label="Local LLM MaxLength",)
                system_prompt = gr.Textbox(show_label=True, lines=2, placeholder=f"System Prompt", label="System prompt", value=INIT_SYS_PROMPT, elem_id="elem_prompt")
                temperature.change(None, inputs=[temperature], outputs=None,
                    _js="""(temperature)=>gpt_academic_gradio_saveload("save", "elem_prompt", "js_temperature_cookie", temperature)""")
                system_prompt.change(None, inputs=[system_prompt], outputs=None,
                    _js="""(system_prompt)=>gpt_academic_gradio_saveload("save", "elem_prompt", "js_system_prompt_cookie", system_prompt)""")
                md_dropdown.change(None, inputs=[md_dropdown], outputs=None,
                    _js="""(md_dropdown)=>gpt_academic_gradio_saveload("save", "elem_model_sel", "js_md_dropdown_cookie", md_dropdown)""")

            with gr.Tab("API-KEY", elem_id="interact-panel"):
                user_custom_data = gr.JSON(value=DEFAULT_USER_CUSTOM,interactive=False,visible=False,elem_id='user_custom_data')
                with gr.Row():
                    with gr.Column():
                        # ! 格式检验啥的以后再说吧，反正输入错了不能用是自己的问题（，有的地方也不是很优雅啊
                        if ALLOW_CUSTOM_API_KEY:
                            _provider_key_json = gr.JSON(value=SUPPORT_API_PROVIDER,visible=False)
                            
                            provider_dropdown = gr.Dropdown(choices=SUPPORT_API_PROVIDER,value='OpenAI',type='value',label='选择服务商',info='仅用于api自定义，不影响模型选择',allow_custom_value=False).style(container=False)
                            api_key_field = gr.Textbox(value='',max_lines=1,placeholder='不输入则使用内置API KEY',label='自定义API-KEY',elem_id='api_key_field')
                            with gr.Row():
                                url_redirect_domain_field = gr.Textbox(value='',max_lines=1,placeholder='不输入则使用OpenAI服务',label='自定义重定向',info='形如：https://api.openai.com',elem_id='url_redirect_domain')
                                url_redirect_path_field = gr.Textbox(value='',max_lines=1,placeholder='不输入则使用OpenAI服务',label='重定向路径',info='留空则使用默认值',elem_id='url_redirect_path')

                            custom_model_input = gr.TextArea(visible=True,label='自定义模型',placeholder='此处输入非内置模型（一行一个，刷新后生效）'+'\ne.g.\nQwen/Qwen2-72B-Instruct\nclaude-instant-1.2',lines=5,elem_id='custom_model_input')
                                
                            
                            # 每次下拉也要更新值
                            provider_dropdown.input(fn=None,inputs=[user_custom_data,provider_dropdown,_provider_key_json],_js='(user_custom_data,provider_dropdown,_provider_to_key_name)=>update_api_and_url_redirect_field(user_custom_data,provider_dropdown,_provider_to_key_name)')
                            provider_dropdown.input(fn=None,inputs=[provider_dropdown],_js='(provider_dropdown)=>update_field_visible(provider_dropdown)')# 保留provider_dropdown
                            
                            # 记录输入（先这么堆着吧xd）
                            api_key_field.input(fn=None,inputs=[user_custom_data,provider_dropdown,_provider_key_json,api_key_field],_js='(user_custom_data,provider_dropdown,_provider_key_json,api_key_field)=>set_api_key(user_custom_data,provider_dropdown,_provider_key_json,api_key_field)')
                            url_redirect_domain_field.input(fn=None,inputs=[user_custom_data,provider_dropdown,url_redirect_domain_field],_js='(user_custom_data,provider_dropdown,url_redirect_domain_field)=>set_url_domain(user_custom_data,provider_dropdown,url_redirect_domain_field)')
                            url_redirect_path_field.input(fn=None,inputs=[user_custom_data,provider_dropdown,url_redirect_path_field],_js='(user_custom_data,provider_dropdown,url_redirect_path_field)=>set_url_path(user_custom_data,provider_dropdown,url_redirect_path_field)')
                            custom_model_input.input(fn=None,inputs=[user_custom_data,custom_model_input],_js="(user_custom_data,custom_model_input)=>set_other(user_custom_data,'CUSTOM_MODELS',custom_model_input)")
                            
                            # 动态载入自定义模型
                            model_switch_tab.select(fn=lambda user_custom_data:_add_custom_model(user_custom_data,AVAIL_LLM_MODELS),inputs=[user_custom_data],outputs=[md_dropdown])
                    gr.HTML(value='',elem_id='custom_api_help_msg')
        
            with gr.Tab("界面外观", elem_id="interact-panel"):
                theme_dropdown = gr.Dropdown(AVAIL_THEMES, value=THEME, label="更换UI主题").style(container=False)
                checkboxes = gr.CheckboxGroup(["基础功能区", "函数插件区", "浮动输入区", "输入清除键", "插件参数区"], value=["基础功能区", "函数插件区"], label="显示/隐藏功能区", elem_id='cbs').style(container=False)
                opt = ["自定义菜单"]
                value=[]
                if ADD_WAIFU: opt += ["添加Live2D形象"]; value += ["添加Live2D形象"]
                checkboxes_2 = gr.CheckboxGroup(opt, value=value, label="显示/隐藏自定义菜单", elem_id='cbsc').style(container=False)
                dark_mode_btn = gr.Button("切换界面明暗 ☀", variant="secondary").style(size="sm")
                dark_mode_btn.click(None, None, None, _js='js_code_for_toggle_darkmode()')
                open_new_tab = gr.Button("打开新对话", variant="secondary").style(size="sm")
                open_new_tab.click(None, None, None, _js=f"""()=>duplicate_in_new_window()""")

            with gr.Tab("帮助", elem_id="interact-panel"):
                gr.Markdown(help_menu_description)

     
    return checkboxes, checkboxes_2, max_length_sl, theme_dropdown, system_prompt, file_upload_2, md_dropdown, top_p, temperature,user_custom_data


def _add_custom_model(user_custom_data: dict,AVAIL_LLM_MODELS: list):# 后面象个方法把这个换成JS emm
    custom_model_list = user_custom_data.get('CUSTOM_MODELS',[])
    new_list = copy.deepcopy(AVAIL_LLM_MODELS)
    for model in custom_model_list:
        if not model.startswith('custom-'): model = 'custom-' + model
        if model not in new_list:
            new_list.append(model)
    return gr.Dropdown.update(choices=new_list)

