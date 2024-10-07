Scholar Navis 使用 GPL-3.0 license 许可证

----------------------------

下面是**在 gpt_academic 基础上，额外添加的**第三方项目（除gpt_academic外，均未发生任何源码的修改）：

| 第三方库或工具                                                                                 | 许可证                | 使用策略                                                             |
| --------------------------------------------------------------------------------------- | ------------------ | ---------------------------------------------------------------- |
| <a href="https://github.com/binary-husky/gpt_academic" target="_blank">GPT Academic</a> | GPL-3.0 license    | 作为该工具的插件，无法独立运行。针对gpt_academic详细的修改内容和使用策略请见下文。                  |
| <a href="https://pypi.org/project/PyYAML" target="_blank">PyYAML</a>                    | MIT License        | 使用库，yaml文件解析                                                     |
| <a href="https://pypi.org/project/beautifulsoup4" target="_blank">beautifulsoup4</a>    | MIT License        | 使用库，网络请求处理                                                       |
| <a href="https://pypi.org/project/requests/" target="_blank">requests</a>               | Apache-2.0 license | 使用库，网络请求                                                         |
| <a href="https://pypi.org/project/python-docx" target="_blank">python-docx</a>          | MIT License        | 使用库，解析docx并获取文本内容，将makrdown转换为word（所所属功能仍在测试，目前不可用）              |
| <a href="https://pypi.org/project/PyMuPDF/" target="_blank">PyMuPDF</a>                 | AGPL-3.0 license   | 使用库，将HTML转换为pdf                                                  |
| <a href="https://github.com/marktext/marktext" target="_blank">MarkText</a>             | MIT License        | 使用该软件将markdown转换为HTML，并对HTML进行了修改                                |
| <a href="https://github.com/mozilla/pdf.js" target="_blank">PDF.js</a>                  | Apache-2.0 license | 直接使用其Prebuilt软件包。源码没有发生修改，用于在线浏览PDF。完整的内容位于`web_services\pdf.js` |

**gpt_academic中产生修改的部分如下：**

- 原则上是尽可能减少对于 gpt_academic 的修改，以方便移植或使用其他的版本。

- 因为对 gpt_academic 的源码产生了修改（主要是使其能够调用 Scholar Navis 并使用一些新加的功能或机制），受限于GPL-3.0的约束，需要将 gpt_academic 的源码一并发布，并且亦需注明修改内容。

- 通常情况下，新添加的代码**文件**，如果没有对原有代码产生修改，则不列出。

- 删除了所有与docker有关的文件，因为目前Scholar Navis 还不支持docker。

- `main.py`: 60行，发生修改。
  
  ```python
   # original
  from themes.theme import js_code_for_toggle_darkmode, js_code_for_persistent_cookie_init
   # motified
  from themes.theme import js_code_for_persistent_cookie_init
  ```

- `main.py`: 约63行处添加了以下内容。这样做可以实现简易的通知显示。
  
  ```python
  # SCHOAR NAVIS 
  sn_version_fp = os.path.join(os.path.dirname(__file__),'crazy_functions','scholar_navis','version')
  if os.path.exists(sn_version_fp):
      with open(sn_version_fp,'r',encoding='utf-8') as f:
          title_html = f"<h1 align=\"center\">GPT 学术优化 {get_current_version()} (Scholar Navis {f.read()})</h1>{theme_declaration}"
  else:title_html = f"<h1 align=\"center\">GPT 学术优化 {get_current_version()}</h1>{theme_declaration}"
  
  notification_fp = os.path.join(os.path.dirname(__file__),'notification','notification.txt')
  if os.path.exists(notification_fp):
      with open(notification_fp,'r',encoding='utf-8') as f:
          title_html = title_html + f'<p style="text-align: left; margin-left: 20px; margin-right: 20px;">{f.read()}</p>'
  ```

- `main.py`: 约67行，添加下述内容，用于 scholar navis版本号显示。
  
  ```python
     ... 上略 ...
           title_html = f"<br><h1 align=\"center\">GPT 学术优化 {get_current_version()} (Scholar Navis {f.read()})</h1>{theme_declaration}"
      else:title_html = f"<br><h1 align=\"center\">GPT 学术优化 {get_current_version()}</h1>{theme_declaration}"
  ```

- `main.py`: 约111行，发生修改，用于区别这是修改版。
  
  ```python
   # original
   with gr.Blocks(title="GPT 学术优化", theme=set_theme, analytics_enabled=False, css=advanced_css) as app_block:
   # motified
   with gr.Blocks(title="GPT 学术优化 (Scholar Navis 修改版)", theme=set_theme, analytics_enabled=False, css=advanced_css) as app_block:
  ```

- `main.py`：120行添加AI警告  
  
  ```python
  gr.HTML('<strong>下方内容为 AI 生成，不代表任何立场，可能存在片面甚至错误。仅供参考，开发者及其组织不负任何责任。</strong>')
  ```

- `main.py`: 约196行，发生修改，接入自定义API-KEY功能，把一些js移出.py合并入相应的.js中。
  
  ```python
  # original
  checkboxes, checkboxes_2, max_length_sl, theme_dropdown, system_prompt, file_upload_2, md_dropdown, top_p, temperature = \
              define_gui_toolbar(AVAIL_LLM_MODELS, LLM_MODEL, INIT_SYS_PROMPT, THEME, AVAIL_THEMES, ADD_WAIFU, help_menu_description, js_code_for_toggle_darkmode)
   # motified
  checkboxes, checkboxes_2, max_length_sl, theme_dropdown, system_prompt, file_upload_2, md_dropdown, top_p, temperature,custom_api_key = \
              define_gui_toolbar(AVAIL_LLM_MODELS, LLM_MODEL, INIT_SYS_PROMPT, THEME, AVAIL_THEMES, ADD_WAIFU, help_menu_description)
  ```

- `main.py`: 约229行，发生修改，接入自定义API-KEY功能，把一些js移出.py合并入相应的.js中。
  
  ```python
   # original
   input_combo = [cookies, max_length_sl, md_dropdown, txt, txt2, top_p, temperature, chatbot, history, system_prompt, plugin_advanced_arg]
          input_combo_order = ["cookies", "max_length_sl", "md_dropdown", "txt", "txt2", "top_p", "temperature", "chatbot", "history", "system_prompt", "plugin_advanced_arg"]
    # motified
   input_combo = [cookies, max_length_sl, md_dropdown, txt, txt2, top_p, temperature, chatbot, history, system_prompt, plugin_advanced_arg,custom_api_key]
          input_combo_order = ["cookies", "max_length_sl", "md_dropdown", "txt", "txt2", "top_p", "temperature", "chatbot", "history", "system_prompt", "plugin_advanced_arg",'custom_api_key']
  ```

- `main.py`：362行，注释掉了自动更新程序
  
  ```python
  def auto_updates(): time.sleep(0); # auto_update() scholar naivs由于修改了代码，所以需要禁用自动更新
  ```

- `config.py`：第65行添加新内容:
  
  ```python
  # 允许用户自行设定API和URL重定向（储存在localstorage中）
  ALLOW_CUSTOM_API_KEY = True
  ```

- `config.py`：默认模型（LLM_MODEL）更改为“glm-4-flash”；为AVAIL_LLM_MODELS添加了GLM系列、qwen系列、moonshot系列和deepseek系列模型，并补充了一些gpt模型（均为原gpt_academic已经支持的模型）；询问多个模型（MULTI_QUERY_LLM_MODELS）更改为更廉价的模型“gpt-3.5-turbo&glm-4-flash”

- `config_private.py`：约118行处产生了以下修改内容。`setup.py`亦可以产生下述修改，或产生一个含有下述修改内容的config_private.py。这样子修改是为了用户可以通过gpt_academic的web服务使用 Scholar Navis
  
  ```python
  # 原始内容：
  DEFAULT_FN_GROUPS = ['对话', '编程', '学术', '智能体']
  
  # 修改后的内容：
  DEFAULT_FN_GROUPS = ['Scholar Navis']
  
  # 有的时候修改后的内容可能会包含原始的内容，例如：
  DEFAULT_FN_GROUPS = ['Scholar Navis','对话', '编程', '学术', '智能体']
  ```

- `crazy_functional.py`：约400行处添加了下面的内容。`setup.py`亦可以产生下述修改。这样修改是为了gpt_academic能够使用 Scholar Navis
  
  ```python
  ###### SCHOLAR NAVIS START ########
  from crazy_functions.scholar_navis.scripts.tools.gpt_academic_handler import registrator
  function_plugins = registrator(function_plugins)
  ##### SCHOLAR NAVIS END - UNINSTALL: DELETE THESE ######
  ```

- `toolbox.py`：添加import
  
  ```python
  from shared_utils.user_custom_manager import get_api_key,get_url_redirect
  ```

- `toolbox.py`：decorated 方法添加参数 user_custom_data: dict  

- `toolbox.py`：第40行，添加  from shared_utils.statistics import user_useage_log

- `toolbox.py`：98行添加如下内容：
  
  ```python
    # 获取openai用的api
   api_key = get_api_key(user_custom_data,"API_KEY",True)
   url_redirect = get_url_redirect('API_URL_REDIRECT',user_custom_data)
   # 方便获取其他供应商的api_key
   def get_other_provider_api_key(provider_api_type:str):return get_api_key(user_custom_data,provider_api_type,True)
  
      if llm_model.startswith('custom-'):
         # 自定义模型使用openai兼容方案，覆盖一些openai的设定
         api_key = get_api_key(user_custom_data,"CUSTOM_API_KEY")
         url_redirect = get_url_redirect('CUSTOM_REDIRECT',user_custom_data)
  
      # 空输入会报错
      if not txt_passon:txt_passon = ' ' 
  ```

- `toolbox.py`：第147行，添加下述内容：
  
  ```python
  # 记录日志
  user_useage_log(request,user_name,llm_model,f.__name__,system_prompt,txt_passon)
  ```

- `toolbox.py`:对cookies和llm_kwargs的键值进行了修改，并且为llm_kwargs添加了新的键值对 

- `toolbox.py`：约517行添加了修正文字编码的内容，用于修复解压后产生的乱码
  
  ```python
  def correct_code_error(str:str):
      try:
          cp437_code = str.encode('cp437')
          try:
              return cp437_code.decode('gbk')
          except:
              try:
                  return cp437_code.decode('utf-8')
              except:return str
      except:
          return str
  ```

- `multi_language.py`：具体修改如下。这里添加这些内容是为了在翻译gpt_academic后，Scholar Navis 可以正常运行
  
  ```python
  # 43行
  # 原始
  blacklist = ['multi-language', CACHE_FOLDER, '.git', 'private_upload', 'multi_language.py', 'build', '.github', '.vscode', '__pycache__', 'venv']
  # 修改后
  blacklist = ['multi-language', CACHE_FOLDER, '.git', 'private_upload', 'multi_language.py', 'build', '.github', '.vscode', '__pycache__', 'venv','scholar_navis']
  
  # 约526行，添加了如下内容
  def  step_ex_scholar_navis():
      ```添加的代码```
  
  # 588行，添加了如下内容
  step_ex_scholar_navis()
  
  # 此外为了适应开发环境，还添加了一些有关于开发版本的多语言策略，基本上在源码中有注明修改
  ```

- `themes/init.js`：第六行添加 scholar_navis_init(); 约第九行处，注释掉了有关welcomeMessage的内容（因为这些内容可能会引发bug）
  
  ```js
  // 以下被注释掉的部分则为修改的部分
  
      // 加载欢迎页面
      // 因为欢迎界面有BUG，所以就暂时去掉了
      //const welcomeMessage = new WelcomeMessage();
      //welcomeMessage.begin_render();
      chatbotIndicator = gradioApp().querySelector('#gpt-chatbot > div.wrap');
      var chatbotObserver = new MutationObserver(() => {
          chatbotContentChanged(1);
          //welcomeMessage.update();
      });
  ```

- `themes/common.css`：末尾添加了用于HTML的summary的样式内容，已经在源码中注明

- `themes/common.js`：约758行，发生修改：
  
  ```js
  // original
  const always_preserve = 2;
  // motified
  const always_preserve = btn_list.length;
  ```

- `themes/common.js`：约1340行，将原来在theme.py中的黑暗模式代码（function js_code_for_toggle_darkmode）移动至此

- `themes/common.py`：约3行，添加用户启用自定义功能的获取方法
  
  ```python
  # original
  CODE_HIGHLIGHT, ADD_WAIFU, LAYOUT = get_conf("CODE_HIGHLIGHT", "ADD_WAIFU", "LAYOUT")
  # motified
  CODE_HIGHLIGHT, ADD_WAIFU, LAYOUT,ALLOW_CUSTOM_API_KEY = get_conf("CODE_HIGHLIGHT", "ADD_WAIFU", "LAYOUT",'ALLOW_CUSTOM_API_KEY')
  ```

- `themes/common.py`：约35行，注释掉"themes/welcome.js",取消欢迎界面（有bug）

- `themes/common.py`：约35和38行，添加载入scholar_navis初始化js和自定义API-KEY功能的js
  
  ```python
  "themes/scholar_navis/scholar_navis_init.js"
  if ALLOW_CUSTOM_API_KEY:common_js_path_list.append("themes/scholar_navis/custom_api_key.js")
  ```

- `themes/gui_advanced_plugin_class.py`：约3、45行，添加高级插件热加载功能支持（热加载为gpt_acadmic自有功能）
  
  ```python
  # line 3: HotReload added
  from toolbox import format_io, find_free_port, on_file_uploaded, on_report_generated, get_conf, ArgsGeneralWrapper, DummyWith,HotReload
  # line 45 original:
  plugin_exe = plugin_obj.execute
  # line 45 motified:
  if plugins[which_plugin].get('ClassHotreload',False):
  ```

- `themes/gui_toolbar.py`：添加import；第9行定义的define_gui_toolbar去除js_code_for_toggle_darkmode参数；第7行，添加 ALLOW_CUSTOM_API_KEY = get_conf('ALLOW_CUSTOM_API_KEY')；define_gui_toolbar的返回值添加user_custom_data参数

- `themes/gui_toolbar.py`：17行添加 as model_switch_tab，用于显示添加的自定义模型：
  
  ```python
  with gr.Tab("更换模型", elem_id="interact-panel") as model_switch_tab:
  ```

- `themes/gui_toolbar.py`：第30行添加 新的gradio.tab：API-KEY；末尾定义新的方法_add_custom_model用于添加自定义模型

- `themes/theme.py`：移除原有的黑暗模式代码（js_code_for_toggle_darkmode），并入common.js中

- `request_llms/bridge_all.py`：引入了model_info_class取代了以往的model_info，并提供自定义的功能（兼容原有功能）；引入了extend_llm_support函数，取代旧有的api2d、llama、vllm对齐，并为自定义模型提供支持。

- `request_llms/bridge_chatgpt.py`：约31行，添加_get_url_redirect_and_check，用于决定是否能够使用API自定义重定向功能，并且该功能取代了原有的verify_endpoint

- `request_llms/bridge_chatgpt.py`：约218行，发生修改，给用户提示添加自定义模型/api的提醒
  
  ```python
  # original
  chatbot.append((inputs, "缺少api_key。\n\n1. 临时解决方案：直接在输入区键入api_key，然后回车提交。\n\n2. 长效解决方案：在config.py中配置。"))
  # motified
  chatbot.append((inputs, "缺少api_key。\n\n1. 临时解决方案：直接在输入区键入api_key，然后回车提交。\n\n2. 长效解决方案：在上方的`API_KEY`中输入您的api-key。"))
  ```

- `request_llms/bridge_chatgpt.py`：约478行，添加自定义模型便签裁剪
  
  ```python
  if llm_kwargs['llm_model'].startswith('custom-'):
          model = llm_kwargs['llm_model'][len('custom-'):]
  ```

- `request_llms/bridge_moonshot.py`：约18-21行、158行、175行，添加api_key参数，用于使用自定义api-key。

- `request_llms/bridge_moonshot.py`：约153行、174行，修复原有的空输入报错问题
  
  ```python
  if not inputs:inputs = ' ' # 空白输入报错
  ```

- `request_llms/bridge_qwen.py`：约18行、35行、46行、56行，添加api_key参数，用于使用自定义api-key。

- `request_llms/com_qwenapi.py`：约9行、16行、20行，添加api_key参数，用于使用自定义api-key。

- `request_llms/bridge_zhipu.py`：约10行、31行、37行、65行、97行，添加api_key参数，用于使用自定义api-key。

- `request_llms/com_zhipuglm.py`：约24行，添加api_key参数，用于使用自定义api-key。

- `request_llms/oai_std_model_template.py`：约153行、268行，添加api_key参数，用于使用自定义api-key。

- `request_llms/oai_std_model_template.py`：约132行，删除了原有的API-KEY获取方法。

- `request_llms/model_info.py`：为上文提到的model.info的取代组件，除了支持原list的功能外，还支持自定义模型的调用

- `shared_utils/fastapi_server.py`：约216行，为web添加在线服务功能（目前仅仅是pdf.js的在线浏览功能）  
  
  ```python
      # 不敏感的一些在线服务
      from .const import WEB_SERVICES_ROOT_PATH
      from fastapi.responses import FileResponse,PlainTextResponse
      @gradio_app.get("/services/pdf_viewer/{path:path}")
      async def pdf_viewer(path:str):
  
          if path.startswith('web/gpt_log'):realpath = path[4:]
          else:realpath = os.path.join(WEB_SERVICES_ROOT_PATH,'pdf.js',path)
  
          if os.path.exists(realpath):
              return FileResponse(realpath)
          else: return PlainTextResponse('bad request',status_code=400)
  ```

- `shared_utils/key_pattern_manager.py`：约70行，添加自定义模型支持；约73行，添加内容，让自定义模型也能支持非标准的api2d的api
  
  ```python
  # line 70
  if llm_model.startswith('gpt-') or llm_model.startswith('one-api-') or llm_model.startswith('custom-'):
  # line 73
  if is_api2d_key(k): avail_key_list.append(k)
  ```

**gpt_academic的使用策略**：

- 访问AI：多线程和单线程对于多个AI的访问，以及其中发生的网络处理、token限制、和访问AI所需的API及其所需文本内容的整合。

- web服务（基于gradio）。包含但不限于登录、多用户管理、用户界面、cookie管理、插件选择和参数修改、markdown解析、捕捉错误后网页呈现、前后端通讯、文件上传和下载以及 Scholar Navis 用到的HTML的链接和跳转。

- Markdown转HTML

- 文件管理：gpt_academic所属文件/文件夹的处理和使用、PDF全文获取

- 调试：控制台输出彩色内容。

- 绘制思维导图 @Menghuan1918

- 为了保证兼容性，参考了对于多线程中止的处理逻辑

- 模块热加载

- 保留了gpt_academic几乎全部的功能和插件

**Scholar Navis 独立于 gpt_academic 的功能**：

- 文件管理：插件文件夹（scholar_navis）内部的文件管理、总结库自身的管理

- 配置文件和版本管理

- Sqlite3数据库的通信和管理

- 使用与 gpt_academic 独立的 markdown 转 pdf 功能

- csv、yaml文件解析

- 适用于 gpt_academic 的 Scholar Navis 安装器（含有安装依赖库的功能）

- Scholar Navis插件的多语言（国际化）显示与多语言翻译工具（支持po和mo格式）

- 为一些需要访问LLM或者是需要文献信息、网络请求的部分，设计了缓存机制，减少因为请求而产生的额外耗时

- 获取论文的元数据、第一页内容、摘要、doi号和标题（其中通过LLM获取的部分是通过 gpt_academic 进行的）

- 文章润色处理逻辑及其LLM请求逻辑，markdown转word（仍在测试）

- 将上传的pdf作为总结库进行管理和关键词设定

- 基于关键词的批量文章总结分析和LLM请求逻辑

- 与AI交流的逻辑，包含拟定课题、寻找文章来源、直接交流的处理逻辑和LLM请求逻辑

- 精细分析文章的处理逻辑和LLM请求逻辑、以及总结库文章包含列表（HTML）设计

- PubMed OA 文章的多线程下载（在线服务关闭，仅限本地部署）

- 面向用户的API自定义与模型自定义添加功能

- 上传文件和产生文件的定时清理

- 用户使用请求日志记录

- 在线PDF浏览
