'''
Original Author: gpt_academic@binary-husky

Modified by PureAmaya on 2025-04-11
- Add language switch option.
- Hide local max_token_length option


Modified by PureAmaya on 2025-03-19
- Restrict file upload types. Only allow csv, rar, zip, and pdf.

Modified by PureAmaya on 2025-03-12
- Add certain encryption measures for users' custom information and large model parameters.

Modified by PureAmaya on 2025-02-24
- Remove redundant features: warm_up_modules()
- Add information about SiliconFlow and Alibaba Cloud Bailian.
- Add prompt information: The inference model is slow; it is recommended to use a high-concurrency service provider.

Modified by PureAmaya on 2024-12-28
- Add i18n support
- Significant modifications for updating to Gradio 5.
- To ensure compatibility, support and interfaces for existing features have been removed.
- Added custom model functionality
- Some features (e.g., temperature value adjustment) have deprecated their JS implementation and replaced them with Gradio components.
- Add simple user account information management.
'''

import copy
import json
from dependencies import gradio_compatibility_layer  as gr
from shared_utils.scholar_navis.sqlite import SQLiteDatabase
from shared_utils.config_loader import get_conf
from shared_utils.scholar_navis.user_account_manager import change_password
from shared_utils.scholar_navis.encrypt import encrypt,decrypt
from shared_utils.scholar_navis.user_custom_manager import DEFAULT_USER_CUSTOM,SUPPORT_API_PROVIDER,splice_config_url_direct
from gradio_modal import Modal
from multi_language import init_language,LANGUAGE_DISPLAY,MULTILINGUAL
from dependencies.i18n import SUPPORT_DISPLAY_LANGUAGE_TUPLE

# ! JS那边现在也确实没有必要传递全部user_custom_data了，后面再改吧（


# 这里很傻逼，先这样子写吧
LLM_MODEL, AVAIL_LLM_MODELS,INIT_SYS_PROMPT,SECRET = get_conf('LLM_MODEL','AVAIL_LLM_MODELS','INIT_SYS_PROMPT','SECRET')


def define_gui_toolbar(chatbot,help_menu_description,lang):

    _ = lambda text: init_language(text, lang)


    # 进行一些参数检查
    if not LLM_MODEL:
        raise ValueError(_('LLM_MODEL 没有设定，需要一个默认的模型'))
    if not INIT_SYS_PROMPT:
        raise ValueError(_('INIT_SYS_PROMPT 没有设定，需要一个默认的系统提示'))
    if not AVAIL_LLM_MODELS:    
        raise ValueError(_('AVAIL_LLM_MODELS 没有设定，需要一个可用模型列表'))
    
    init_event_list = []

    NORMAL_HELP_MSG = _('''
    <p>在此处自定义您的api-key，访问更多模型。</p>
    <p>
    目前仅OpenAI支持使用其他重定向服务<br>
    其他提供商均使用的是官方服务<br></p>

    <p>
    OpenAI重定向服务只适用于OpenAI的大部分模型<br>
    如果要重定向使用其他模型，请使用 <em>自定义</em> 功能
    </p>

    <details>
    <summary>点击查看 API-KEY 获取地址</summary>
    <ul>
    <li><a href="https://platform.openai.com/api-keys" target="_blank">OpenAI</a>：GPT系列模型</li>
    <li><a href="https://console.x.ai/" target="_blank">Grok</a>：Grok系列模型</li>
    <li><a href="https://aistudio.google.com/" target="_blank">Gemini</a>：Gemini系列模型</li>
    <li><a href="https://open.bigmodel.cn/usercenter/apikeys" target="_blank">智谱(Zhipu)</a>：GLM系列模型</li>
    <li><a href="https://bailian.console.aliyun.com/?apiKey=1#/api-key" target="_blank">通义千问(Qwen)</a>：qwen系列模型</li>
    <li><a href="https://platform.moonshot.cn/console/api-keys" target="_blank">月之暗面(Moonshot)</a>：moonshot系列模型</li>
    <li><a href="https://platform.deepseek.com/api_keys" target="_blank">深度求索(Deepseek)</a>：deepseek系列模型</li>
    </ul>
    </details>
    ''')

    CUSTOM_HELP_MSG = _('''
    <p>使用该功能添加自定义模型或使用openAI重定向服务。
    <br>自定义模型将使用 custom- 前缀，并使用本页面的信息发送请求
    如果仅需使用openAI重定向服务，请在 <em>OpenAI</em> 项目中修改重定向地址
    </p>

    <details>
    <summary>点击查看 第三方中转服务</summary>
    <em>使用前请阅读中转服务的帮助文档</em>
    <ul>
    <li><a href="https://api2d.com/" target="_blank">API2d</a>：支持多功能接口，中国大陆优化</li>
    <li><a href="https://aiproxy.io/" target="_blank">AI Proxy</a>：位于新加坡，支持英文页面，支持大部分支付方式</li>
    <li><a href="https://aihubmix.com/" target="_blank">AI HUB MIX</a>：中国大陆优化</li>
    <li><a href="https://bailian.console.aliyun.com/#/model-market" target="_blank">阿里云百炼</a>：支持多种模型，有英文界面</li>
    <li><a href="https://cloud.siliconflow.cn/models" target="_blank">硅基流动</a>：支持多种模型，有英文界面</li>
    <li>使用其他第三方<a href="https://github.com/songquanpeng/one-api" target="_blank">oneapi</a>服务</li>
    <li>使用其他第三方<a href="https://github.com/open-webui/open-webui" target="_blank">llama</a>服务</li>
    </ul>
    </details>
    ''')


    
    with Modal(visible=False, elem_id="tooltip",elem_classes='modal',allow_user_close=True) as tooltip_panel:
        with gr.Tab(_("上传文件"), elem_id="interact-panel",visible=True):
            # gr.HTML(value='1',elem_id='local_pdf_optimizer',label='pdf优化器')
            # gr.Markdown('------------------------------------------')
            gr.Markdown(_("请上传本地文件 / 压缩包以供使用。请注意: 上传文件后会自动把输入区修改为相应路径"))
            file_upload_2 = gr.Files(label=_("支持 zip, rar, pdf, csv"), file_count="multiple", elem_id="elem_upload_float",file_types=['.zip','.rar','.pdf','.csv'])
        with gr.Tab(_("模型与语言"), elem_id="interact-panel") as model_switch_tab:
            gr.HTML(_('<p>推荐使用高并发服务商 (即速率限制较为宽松)</p>'))

            md_dropdown:gr.Dropdown = gr.Dropdown(AVAIL_LLM_MODELS, value=LLM_MODEL, 
                                                elem_id="elem_model_sel",elem_classes='dropdown_in_modal',
                                                label=_("更换LLM模型/请求源"),info=_('推理模型(o1,o3,r1等)速度较慢，但是效果较好')).style(container=False)

            lang_dropdown = gr.Dropdown(value=_get_user_language, info=f"<b>{_('会重新加载网页')}</b>",
                                        inputs=[md_dropdown], choices=SUPPORT_DISPLAY_LANGUAGE_TUPLE,
                                        label=_('选择语言'),interactive=MULTILINGUAL)
            # inputs=[md_dropdown] 没有任何实际意义，只是为了把gr.Request传过去

            top_p = gr.Slider(minimum=-0, maximum=1.0, value=1.0, step=0.01,interactive=True, label="Top-p (nucleus sampling)",elem_id="elem_top")
            temperature = gr.Slider(minimum=-0, maximum=2.0, value=1.0, step=0.01, interactive=True, label="Temperature", elem_id="elem_temperature")
            max_length_sl = gr.Slider(minimum=256, maximum=1024*32, value=4096, step=128, interactive=True, label="Local LLM MaxLength",visible=False)
            system_prompt = gr.Textbox(show_label=True, lines=2, placeholder=_('留空时使用默认prompt: {}').format(INIT_SYS_PROMPT), label="System prompt", value=INIT_SYS_PROMPT, elem_id="elem_prompt")
            llm_kwargs_storage = gr.BrowserState(default_value={'model':LLM_MODEL,'top_p':1.0,'temperature':1.0,'max_length':4096,'prompt':INIT_SYS_PROMPT},
                                                storage_key='llm_kwargs',secret=SECRET)
            '''
            temperature.change(None, inputs=[temperature], outputs=None,
                js="""(temperature)=>gpt_academic_gradio_saveload("save", "elem_temperature", "js_temperature_cookie", temperature)""")
            system_prompt.change(None, inputs=[system_prompt], outputs=None,
                js="""(system_prompt)=>gpt_academic_gradio_saveload("save", "elem_prompt", "js_system_prompt_cookie", system_prompt)""")
            md_dropdown.change(None, inputs=[md_dropdown], outputs=None,
                js="""(md_dropdown)=>gpt_academic_gradio_saveload("save", "elem_model_sel", "js_md_dropdown_cookie", md_dropdown)""")
            '''
            
            temperature.change(_save_llm_kwargs,inputs=[md_dropdown,top_p,temperature,max_length_sl,system_prompt],outputs=[chatbot,llm_kwargs_storage])
            top_p.change(_save_llm_kwargs,inputs=[md_dropdown,top_p,temperature,max_length_sl,system_prompt],outputs=[chatbot,llm_kwargs_storage])
            max_length_sl.change(_save_llm_kwargs,inputs=[md_dropdown,top_p,temperature,max_length_sl,system_prompt],outputs=[chatbot,llm_kwargs_storage])
            system_prompt.change(_save_llm_kwargs,inputs=[md_dropdown,top_p,temperature,max_length_sl,system_prompt],outputs=[chatbot,llm_kwargs_storage])
            md_dropdown.change(_save_llm_kwargs,inputs=[md_dropdown,top_p,temperature,max_length_sl,system_prompt],outputs=[chatbot,llm_kwargs_storage])

            if MULTILINGUAL:
                lang_dropdown.input(fn=None,
                                    inputs=[lang_dropdown],
                                    outputs=None,
                                    js= ''' (lang_dropdown)=> {setCookie("lang",lang_dropdown,365); window.location.href = "/"; }''')


            # 尝试修复选择modal以外的内容时，界面意外关闭的情况
            md_dropdown.blur(None,None,None,js='BanModalPointEvents')# 这样子写没有括号的js就能用...
            md_dropdown.change()
            
            top_p.change(None, inputs=[top_p], outputs=None,
                js="""(top_p)=>gpt_academic_gradio_saveload("save", "elem_top", "js_top_cookie", top_p)""")

        with gr.Tab("API-KEY", elem_id="interact-panel"):
            user_custom_data = gr.JSON(value=DEFAULT_USER_CUSTOM,visible=False,elem_id='user_custom_data')
            _provider_key_json = gr.JSON(value=SUPPORT_API_PROVIDER,visible=False)
            custom_local_storage = gr.BrowserState(default_value=DEFAULT_USER_CUSTOM,storage_key='user_custom_data',secret=SECRET)
            with gr.Row():
                helper = gr.HTML(value=NORMAL_HELP_MSG,elem_id='custom_api_help_msg')
                with gr.Column():
                    provider_dropdown = gr.Dropdown(choices=SUPPORT_API_PROVIDER,value='OpenAI',type='value',label=_('选择服务商'),info=_('仅用于api自定义，不影响模型选择'),allow_custom_value=False).style(container=False)
                    api_key_field = gr.Textbox(value='',max_lines=1,placeholder=_('不输入则使用内置API KEY'),label=_('自定义API-KEY'),elem_id='api_key_field')
                    with gr.Row():
                        domain,path = splice_config_url_direct()
                        url_redirect_domain_field = gr.Textbox(value='',max_lines=1,placeholder=domain,label=_('自定义重定向'),elem_id='url_redirect_domain')
                        url_redirect_path_field = gr.Textbox(value='',max_lines=1,placeholder=path,label=_('重定向路径'),elem_id='url_redirect_path')

                    custom_model_input = gr.TextArea(visible=True,label=_('自定义模型'),placeholder=_('此处输入非内置模型（一行一个）')+'\ne.g.\nQwen/Qwen2-72B-Instruct\nclaude-instant-1.2',lines=5,elem_id='custom_model_input')  

                    # 每次下拉也要更新值
                    provider_dropdown.input(fn=None,inputs=[user_custom_data,provider_dropdown,_provider_key_json],outputs=[api_key_field,url_redirect_domain_field,url_redirect_path_field],js='(user_custom_data,provider_dropdown,_provider_to_key_name)=>update_api_and_url_redirect_field(user_custom_data,provider_dropdown,_provider_to_key_name)')
                    provider_dropdown.input(fn=None,inputs=[provider_dropdown],outputs=[helper],js=f'(provider_dropdown)=>update_field_visible(provider_dropdown,{[NORMAL_HELP_MSG,CUSTOM_HELP_MSG]})')# 保留provider_dropdown
                    # 虽然现在用不到，但是以防万一，也给他加上
                    provider_dropdown.blur(None,None,None,js='BanModalPointEvents')
                    
                    # 用户输入的修改储存在user_custom_data中，程序使用自定义数据时直接使用的是user_custom_data
                    
                    # 记录输入（先这么堆着吧xd）
                    api_key_field.input(fn=check_input_invaild,inputs=api_key_field).success(fn=None,
                                                inputs=[user_custom_data,provider_dropdown,_provider_key_json,api_key_field],
                                                outputs=[user_custom_data],
                                                js='(user_custom_data,provider_dropdown,_provider_key_json,api_key_field)=>set_api_key(user_custom_data,provider_dropdown,_provider_key_json,api_key_field)')
                    url_redirect_domain_field.input(fn=check_input_invaild,inputs=url_redirect_domain_field).success(fn=None,
                                                            inputs=[user_custom_data,provider_dropdown,url_redirect_domain_field],
                                                            outputs=[user_custom_data],
                                                            js='(user_custom_data,provider_dropdown,url_redirect_domain_field)=>set_url_domain(user_custom_data,provider_dropdown,url_redirect_domain_field)')
                    url_redirect_path_field.input(fn=check_input_invaild,inputs=url_redirect_path_field).success(fn=None,
                                                                                inputs=[user_custom_data,provider_dropdown,url_redirect_path_field],outputs=[user_custom_data],
                                                                                js='(user_custom_data,provider_dropdown,url_redirect_path_field)=>set_url_path(user_custom_data,provider_dropdown,url_redirect_path_field)')
                    custom_model_input.input(fn=None,inputs=[user_custom_data,custom_model_input],outputs=[user_custom_data],js="(user_custom_data,custom_model_input)=>set_other(user_custom_data,'CUSTOM_MODELS',custom_model_input)")
                    user_custom_data.change(fn=_save_user_custom_data,inputs=user_custom_data,outputs=custom_local_storage)
                    
        with gr.Tab(_("帮助"), elem_id="interact-panel"):
            gr.Markdown(help_menu_description)
            
        with gr.Tab(_('更改密码')) as change_pwd_tab:
            username = gr.Textbox(label=_('当前登录用户'),value='',interactive=False)
            gr.HTML('<span style="color:red; font-weight:bold;">{}</span>'.format(_("请注意，点击确认后立即生效")))
            current_pwd = gr.Textbox(label=_('当前密码'),value='',type='password',max_lines=1,placeholder=_('请输入当前密码'))
            new_pwd = gr.Textbox(label=_('修改密码'),value='',type='password',max_lines=1,placeholder=_('请输入新密码'))
            confirm_pwd = gr.Textbox(label=_('确认修改的密码'),value='',type='password',max_lines=1,placeholder=_('请再次输入新密码'))
            with gr.Row():
                confirm_btn = gr.Button(value=_('确认修改'))
                cancel_btn = gr.Button(value=_('取消'))
            logout_btn = gr.Button(value=_('退出登录'),variant='primary')
            account_msg = gr.BrowserState(storage_key='msg',secret=SECRET)
            confirm_btn.click(fn=change_pwd_event,inputs=[current_pwd,new_pwd,confirm_pwd],outputs=account_msg).success(None,None,None,js='window.location.href = "/"')
            cancel_btn.click(fn=None,inputs=None,outputs=[current_pwd,new_pwd,confirm_pwd],js='["","",""]')
            logout_btn.click(fn=None,inputs=None,outputs=None,js='()=>{setCookie("user_token","0",0);\nwindow.location.href = "/"}')
        

            # 动态载入自定义模型
            model_switch_tab.select(fn=lambda user_custom_data:_load_custom_model(user_custom_data),
                                    inputs=[user_custom_data],outputs=md_dropdown)
            
            # block 初始化事件
            custom_tab_init = {
                "fn": _init_custom_function,
                "inputs": [custom_local_storage],# ! js的输出结果会根据顺序，放到这里作为fn的输入
                "outputs": [user_custom_data,api_key_field, url_redirect_domain_field, url_redirect_path_field, custom_model_input,md_dropdown],
            } # 这里就先这样吧，也没必要换成gr.BrowseState了
            # 决定是否显示修改密码的这个东西（顺便显示一下用户名）
            decide_allow_change_pwd_init = {"fn": decide_allow_change_pwd,'inputs':[], "outputs": [change_pwd_tab,username]}
            
            load_llm_kwargs = {
                'fn':_load_llm_kwargs,
                'inputs':llm_kwargs_storage,
                'outputs':[chatbot,md_dropdown,top_p,temperature,max_length_sl,system_prompt]
            }
            
            init_event_list.append(decide_allow_change_pwd_init) # 先拿到用户名
            init_event_list.append(custom_tab_init) # 初始化自定义
            init_event_list.append(load_llm_kwargs) # 加载参数

    return tooltip_panel,init_event_list, max_length_sl,system_prompt, file_upload_2, md_dropdown, top_p, temperature,user_custom_data


def _get_user_language(request:gr.Request,de):
    user_code = request.cookies.get('lang')

    if not user_code:
        user_code = LANGUAGE_DISPLAY
    try:
        for name,code in SUPPORT_DISPLAY_LANGUAGE_TUPLE:
            if user_code == code:
                return code
        return LANGUAGE_DISPLAY
    except:return LANGUAGE_DISPLAY

def _init_custom_function(request:gr.Request,local_storage):

    lang = request.cookies.get('lang')
    _ = lambda txt:init_language(txt,lang)

    try:
        if not request.username or request.username == 'default_user':
            # 匿名登录，选择用LocalStorage保存
            user_custom_data = local_storage
        else:
            # 登录了，选择用数据库保存
            with SQLiteDatabase('user_account') as db:
                user_custom_data :str = db.easy_select(request.username,'user_custom_data')
                user_custom_data = decrypt(user_custom_data)
                user_custom_data = json.loads(user_custom_data)
    except: 
        gr.Warning(_('自定义数据加载失败，使用默认值'))  
        user_custom_data = DEFAULT_USER_CUSTOM            
        
    new_list_gr_updater = _load_custom_model(user_custom_data) # 载入自定义模型
    return user_custom_data,user_custom_data['API_KEY'], user_custom_data['API_URL_REDIRECT'][0], user_custom_data['API_URL_REDIRECT'][1],'\n'.join(user_custom_data['CUSTOM_MODELS']),new_list_gr_updater

def _load_custom_model(user_custom_data):
    custom_model_list = user_custom_data.get('CUSTOM_MODELS',[])
    new_list = copy.deepcopy(AVAIL_LLM_MODELS)
    for model in custom_model_list:
        model = model.strip()
        if not model.startswith('custom-'): model = 'custom-' + model
        if model not in new_list:
            new_list.append(model)
    return gr.update(choices=new_list)

def _save_user_custom_data(request:gr.Request,user_custom_data:dict):
    if not request.username or request.username == 'default_user':
        # 匿名登录，选择用LocalStorage保存
        return user_custom_data
    else:
        # 登录了，选择用数据库保存，localStorage不做任何修改
        with SQLiteDatabase('user_account') as db:
            db.update(request.username,'user_custom_data',encrypt(json.dumps(user_custom_data)))
            return gr.update()

def _load_llm_kwargs(request:gr.Request,local_storage):

    lang = request.cookies.get('lang')
    _ = lambda txt:init_language(txt,lang)

    try:
        if not request.username or request.username == 'default_user':
            llm_kwargs = local_storage
            
        else:
            # 登录了，读取数据库内的用户数据
            with SQLiteDatabase('user_account') as db:
                llm_kwargs = db.easy_select(request.username,'llm_kwargs')
                llm_kwargs = decrypt(llm_kwargs)
                llm_kwargs = json.loads(llm_kwargs)
    except: 
        llm_kwargs = {'model':LLM_MODEL,'top_p':1.0,'temperature':1.0,'max_length':4096,'prompt':INIT_SYS_PROMPT}
        gr.Warning(_('参数加载失败，使用默认值'))  
    return gr.update(label=_("当前模型: {}").format(llm_kwargs['model'])),llm_kwargs['model'],llm_kwargs['top_p'],llm_kwargs['temperature'],llm_kwargs['max_length'],llm_kwargs['prompt']
                
def _save_llm_kwargs(request:gr.Request,model,top_p,temperature,max_length,prompt):

    lang = request.cookies.get('lang')
    _ = lambda txt:init_language(txt,lang)

    llm_kwargs = {'model':model,'top_p':top_p,'temperature':temperature,'max_length':max_length,'prompt':prompt}
    if not request.username or request.username == 'default_user':
        # 匿名登录，选择用LocalStorage保存
        return gr.update(label=_("当前模型: {}").format(model)),llm_kwargs
    else:
        # 登录了，选择用数据库保存，localStorage不做更改
        with SQLiteDatabase('user_account') as db:
            db.update(request.username,'llm_kwargs',encrypt(json.dumps(llm_kwargs)))
            return gr.update(label=_("当前模型: {}").format(model)),gr.update()

def check_input_invaild(request:gr.Request,inputs:str):

    lang = request.cookies.get('lang')
    _ = lambda txt:init_language(txt,lang)

    if inputs:
        if not inputs.isascii():raise gr.Error(f'{inputs} {_("包含不可使用的字符，请重新输入")}',duration=5)

def decide_allow_change_pwd(request: gr.Request):
    if not request.username or request.username == 'default_user':return gr.update(visible=False,render=False),None # 没有登录要求的时候不修改密码
    return gr.update(visible=True,render=True),request.username

def change_pwd_event(request: gr.Request,current_pwd,new_pwd,confirm_pwd):
    lang = request.cookies.get('lang')
    change_password(current_pwd,new_pwd,confirm_pwd,request.username,lang)

