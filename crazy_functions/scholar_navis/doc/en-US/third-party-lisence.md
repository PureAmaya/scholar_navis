Scholar Navis is licensed under the GPL-3.0 license.

**A translated version for reference only. In case of conflict, the Simplified Chinese version shall be considered as the authoritative one.**

----------------------------

In addition to gpt_academic, the following third-party projects are included (none of which have made any source code modifications):

| Third-party Library or Tool                                                             | License                              | Usage Strategy                                                                                                                              |
| --------------------------------------------------------------------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| <a href="https://github.com/binary-husky/gpt_academic" target="_blank">GPT Academic</a> | GPL-3.0 license                      | Used as a plugin for this tool; cannot run independently. Detailed modifications and usage strategies for gpt_academic are described below. |
| <a href="https://pypi.org/project/PyYAML" target="_blank">PyYAML</a>                    | MIT License                          | Library used for parsing YAML files                                                                                                         |
| <a href="https://pypi.org/project/beautifulsoup4" target="_blank">beautifulsoup4</a>    | MIT License                          | Library used for web request processing                                                                                                     |
| <a href="https://pypi.org/project/requests/" target="_blank">requests</a>               | Apache Software License (Apache-2.0) | Library used for web requests                                                                                                               |
| <a href="https://pypi.org/project/python-docx" target="_blank">python-docx</a>          | MIT License                          | Library used to parse docx files and extract text content, and to convert markdown to word (these features are still in testing)            |
| <a href="https://pypi.org/project/PyMuPDF/" target="_blank">PyMuPDF</a>                 | AGPL-3.0 license                     | Library used to convert HTML to PDF                                                                                                         |
| <a href="https://github.com/marktext/marktext" target="_blank">MarkText</a>             | MIT License                          | Used the software to convert markdown to HTML, and modifications were made to the HTML                                                      |
| <a href="https://github.com/Stuk/jszip" target="_blank">JSZip</a>                       | MIT license                          | Using a library for local ZIP compression package processing in the browser (the feature is still in testing and currently unavailable).    |
| <a href="https://github.com/jquery/jquery" target="_blank">jQuery</a>                   | MIT license                          | Using a library that supports the $ syntax and other extensions (the feature is still in testing and currently unavailable).                |
| <a href="https://github.com/mozilla/pdf.js" target="_blank">PDF.js</a>                  | Apache-2.0 license                   | Using a library to enable HTML5 support for processing PDF files(the feature is still in testing and currently unavailable).                |
| <a href="https://github.com/eligrey/FileSaver.js/" target="_blank">FileSaver.js</a>     | MIT license                          | Using libraries, HTML5 saveAs() to save a compressed package (the feature is still in testing and currently unavailable).                   |

**The modified parts in gpt_academic are as follows:**

- The principle is to make as few modifications to gpt_academic as possible to facilitate portability or the use of other versions.

- Because modifications have been made to the source code of gpt_academic (mainly to enable it to call Scholar Navis and use some new features or mechanisms), due to the constraints of the GPL-3.0 license, it is necessary to release the source code of gpt_academic along with it, and also to note the details of the modifications.

- Generally speaking, new code **files** that do not make any modifications to the existing code are not listed.

- `main.py`: line 60, has been modified.
  
  ```python
   # original
  from themes.theme import js_code_for_toggle_darkmode, js_code_for_persistent_cookie_init
   # motified
  from themes.theme import js_code_for_persistent_cookie_init
  ```

- `main.py`: At around line 63, the following content was added. This will enable a simple notification display.
  
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

- `main.py`: approximately line 67, the following content has been added for displaying the version number of Scholar Navis.
  
  ```python
     ... Briefly above ...
           title_html = f"<br><h1 align=\"center\">GPT 学术优化 {get_current_version()} (Scholar Navis {f.read()})</h1>{theme_declaration}"
      else:title_html = f"<br><h1 align=\"center\">GPT 学术优化 {get_current_version()}</h1>{theme_declaration}"
  ```

- `main.py`: around line 111, there has been a modification to distinguish this as a modified version.
  
  ```python
   # original
   with gr.Blocks(title="GPT 学术优化", theme=set_theme, analytics_enabled=False, css=advanced_css) as app_block:
   # motified
   with gr.Blocks(title="GPT 学术优化 (Scholar Navis 修改版)", theme=set_theme, analytics_enabled=False, css=advanced_css) as app_block:
  ```

- `main.py`: around line 196, there has been a modification to incorporate a custom API-KEY feature, moving some JavaScript content out and merging it into the corresponding JavaScript files.
  
  ```python
  # original
  checkboxes, checkboxes_2, max_length_sl, theme_dropdown, system_prompt, file_upload_2, md_dropdown, top_p, temperature = \
              define_gui_toolbar(AVAIL_LLM_MODELS, LLM_MODEL, INIT_SYS_PROMPT, THEME, AVAIL_THEMES, ADD_WAIFU, help_menu_description, js_code_for_toggle_darkmode)
   # motified
  checkboxes, checkboxes_2, max_length_sl, theme_dropdown, system_prompt, file_upload_2, md_dropdown, top_p, temperature,custom_api_key = \
              define_gui_toolbar(AVAIL_LLM_MODELS, LLM_MODEL, INIT_SYS_PROMPT, THEME, AVAIL_THEMES, ADD_WAIFU, help_menu_description)
  ```

- `main.py`: around line 229, there has been a modification to integrate a custom API-KEY feature, moving some JavaScript code out of the .py file and merging it into the corresponding .js files.
  
  ```python
   # original
   input_combo = [cookies, max_length_sl, md_dropdown, txt, txt2, top_p, temperature, chatbot, history, system_prompt, plugin_advanced_arg]
          input_combo_order = ["cookies", "max_length_sl", "md_dropdown", "txt", "txt2", "top_p", "temperature", "chatbot", "history", "system_prompt", "plugin_advanced_arg"]
    # motified
   input_combo = [cookies, max_length_sl, md_dropdown, txt, txt2, top_p, temperature, chatbot, history, system_prompt, plugin_advanced_arg,custom_api_key]
          input_combo_order = ["cookies", "max_length_sl", "md_dropdown", "txt", "txt2", "top_p", "temperature", "chatbot", "history", "system_prompt", "plugin_advanced_arg",'custom_api_key']
  ```

- `toolbox.py`: A new import has been added.
  
  ```python
  from shared_utils.user_custom_manager import get_api_key,get_url_redirect
  ```

- `toolbox.py`：第98行添加的内容：
  
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
  
          txt_passon = txt
          if txt == "" and txt2 != "": txt_passon = txt2
  
          # 空输入会报错
          if not txt_passon:txt_passon = '.'sssss
  ```

- `config.py`: New content added on line 65: 
  
  ```python
  # 允许用户自行设定API和URL重定向（储存在localstorage中）
  ALLOW_CUSTOM_API_KEY = True
  ```

- `config.py`: The default model (LLM_MODEL) has been changed to "glm-4-flash"; the AVAIL_LLM_MODELS has been added with the GLM series, Qwen series, Moonshot series, and Deepseek series models, and some GPT models have been supplemented (all of which are models already supported by the original gpt_academic); the MULTI_QUERY_LLM_MODELS has been changed to the cheaper models "gpt-3.5-turbo&glm-4-flash".

- `crazy_functional.py`, the following content was added around line 400. The `setup.py` can also cause the following modifications. These modifications are made to enable gpt_academic to utilize Scholar Navis.
  
  ```python
  ###### SCHOLAR NAVIS START ########
  from crazy_functions.scholar_navis.scripts.tools.gpt_academic_handler import registrator
  function_plugins = registrator(function_plugins)
  ##### SCHOLAR NAVIS END - UNINSTALL: DELETE THESE ######
  ```

- In `config_private.py`, the following modifications were made around line 118. The `setup.py` can also make the following changes, or it can generate a `config_private.py` containing the following modifications. This modification is made so that users can access Scholar Navis through the gpt_academic web service.
  
  ```python
  # original：
  DEFAULT_FN_GROUPS = ['对话', '编程', '学术', '智能体']
  
  # modified：
  DEFAULT_FN_GROUPS = ['Scholar Navis']
  
  # Sometimes the modified content may include the original content
  # for example:
  DEFAULT_FN_GROUPS = ['Scholar Navis','对话', '编程', '学术', '智能体']
  ```

- `toolbox.py`: An import has been added. 
  
  ```python
  from shared_utils.user_custom_manager import get_api_key,get_url_redirect
  ```

- `toolbox.py`: The decorated method has added a parameter user_custom_data: dict

- `toolbox.py`: The following content has been added at line 98:
  
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
  ```

- `toolbox.py`: The following content has been added at line 112:
  
  ```python
   # 空输入会报错
   if not txt_passon:txt_passon = '.'
  ```

- `toolbox.py`: The keys and values of cookies and llm_kwargs have been modified, and new key-value pairs have been added to llm_kwargs.

- `multi_language.py`: The specific modifications are as follow. These contents are added here to ensure that Scholar Navis can operate normally after the translation of gpt_academic.
  
  ```python
  # line 43
  # Original
  blacklist = ['multi-language', CACHE_FOLDER, '.git', 'private_upload', 'multi_language.py', 'build', '.github', '.vscode', '__pycache__', 'venv']
  # Modified
  blacklist = ['multi-language', CACHE_FOLDER, '.git', 'private_upload', 'multi_language.py', 'build', '.github', '.vscode', '__pycache__', 'venv','scholar_navis']
  
  # Approximately line 526, added the following content
  def  step_ex_scholar_navis():
      ```Added code```
  
  # Line 588, added the following content
  step_ex_scholar_navis()
  ```

- `themes/init.js`: Approximately on the ninth line, the content related to `welcomeMessage` has been commented out (because this content might cause bugs).
  
  ```js
  // The following commented out section is the part that has been modified
  
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

- `themes/common.css`: Added style content for HTML's `summary` at the end of the file, which is noted in the source code.

- `themes/common.js`: Around line 758, there has been a modification: 
  
  ```js
  // original
  const always_preserve = 2;
  // motified
  const always_preserve = btn_list.length;
  ```

- `themes/common.js`: Around line 1340, the dark mode code (function js_code_for_toggle_darkmode) that was originally in `theme.py` has been moved here.

- `themes/common.py`: Around line 3, a method to retrieve the user's enable custom feature has been added.  
  
  ```python
  # original
  CODE_HIGHLIGHT, ADD_WAIFU, LAYOUT = get_conf("CODE_HIGHLIGHT", "ADD_WAIFU", "LAYOUT")
  # motified
  CODE_HIGHLIGHT, ADD_WAIFU, LAYOUT,ALLOW_CUSTOM_API_KEY = get_conf("CODE_HIGHLIGHT", "ADD_WAIFU", "LAYOUT",'ALLOW_CUSTOM_API_KEY')
  ```

- `themes/common.py`: Around line 35, "themes/welcome.js" has been commented out, and the welcome interface (has a bug) has been disabled.

- `themes/common.py`: Around lines 35 and 38, added loading of scholar_navis initialization js and js for the custom API-KEY feature.
  
  ```python
  "themes/scholar_navis/scholar_navis_init.js"
  if ALLOW_CUSTOM_API_KEY:common_js_path_list.append("themes/scholar_navis/custom_api_key.js")
  ```

- `themes/gui_advanced_plugin_class.py`: Around lines 3 and 45, added support for advanced plugin hotloading functionality (hotloading is a feature inherent to gpt_acadmic).
  
  ```python
  # line 3: HotReload added
  from toolbox import format_io, find_free_port, on_file_uploaded, on_report_generated, get_conf, ArgsGeneralWrapper, DummyWith,HotReload
  # line 45 original:
  plugin_exe = plugin_obj.execute
  # line 45 motified:
  if plugins[which_plugin].get('ClassHotreload',False):
  ```

- `themes/gui_toolbar.py`: Added import; the `define_gui_toolbar` defined on line 9 no longer takes the `js_code_for_toggle_darkmode` parameter; on line 7, `ALLOW_CUSTOM_API_KEY = get_conf('ALLOW_CUSTOM_API_KEY')` was added; the `define_gui_toolbar` return value now includes the `user_custom_data` parameter

- `themes/gui_toolbar.py`: Line 17 adds `as model_switch_tab`, used to display the added custom models:
  
  ```python
  with gr.Tab("更换模型", elem_id="interact-panel") as model_switch_tab:
  ```

- `themes/gui_toolbar.py`: On line 30, a new `gradio.tab` named "API-KEY" was added; a new method `_add_custom_model` was defined at the end of the file to add custom models

- `themes/theme.py`: The original dark mode code (`js_code_for_toggle_darkmode`) was removed and merged into `common.js`

- `request_llms/bridge_all.py`: `model_info_class` was introduced to replace the previous `model_info`, providing custom features (compatible with existing features); `extend_llm_support` function was introduced to replace the old api2d, llama, vllm alignment, and provide support for custom models.

- `request_llms/bridge_ChatGPT.py`: On line 31, `_get_url_redirect_and_check` was added to determine whether the API custom redirection feature can be used, and this feature replaces the original `verify_endpoint`

- `request_llms/bridge_ChatGPT.py`: On line 218, there was a modification to prompt the user to add custom models/api.
  
  ```python
  # original
  chatbot.append((inputs, "缺少api_key。\n\n1. 临时解决方案：直接在输入区键入api_key，然后回车提交。\n\n2. 长效解决方案：在config.py中配置。"))
  # motified
  chatbot.append((inputs, "缺少api_key。\n\n1. 临时解决方案：直接在输入区键入api_key，然后回车提交。\n\n2. 长效解决方案：在上方的`API_KEY`中输入您的api-key。"))
  ```

- `request_llms/bridge_ChatGPT.py`: Around line 478, added functionality for custom model tag trimming.
  
  ```python
  if llm_kwargs['llm_model'].startswith('custom-'):
          model = llm_kwargs['llm_model'][len('custom-'):]
  ```

- `request_llms/bridge_moonshot.py`: Around lines 18-21, 158, and 175, the api_key parameter was added to use a custom api-key.

- `request_llms/bridge_moonshot.py`: Around lines 153 and 174, the original empty input error reporting issue was fixed.
  
  ```python
  if not inputs:inputs = ' ' # 空白输入报错
  ```

- `request_llms/bridge_qwen.py`: Around lines 18, 35, 46, and 56, the api_key parameter was added to use a custom api-key.

- `request_llms/com_qwenapi.py`: Around lines 9, 16, and 20, the api_key parameter was added to use a custom api-key.

- `request_llms/bridge_zhipu.py`: Around lines 10, 31, 37, 65, and 97, the api_key parameter was added to use a custom api-key.

- `request_llms/com_zhipuglm.py`: Around line 24, the api_key parameter was added to use a custom api-key.

- `request_llms/oai_std_model_template.py`: Around lines 153 and 268, the api_key parameter was added to use a custom api-key.

- `request_llms/oai_std_model_template.py`: Around line 132, the original API-KEY retrieval method was removed.

- `request_llms/model_info.py`: As a replacement component for the mentioned model.info, in addition to supporting the original list functionality, it also supports calling custom models.

- `shared_utils/key_pattern_manager.py`: Around line 70, custom model support was added; around line 73, content was added to allow custom models to also support non-standard api2d's api. 
  
  ```python
  # line 70
  if llm_model.startswith('gpt-') or llm_model.startswith('one-api-') or llm_model.startswith('custom-'):
  # line 73
  if is_api2d_key(k): avail_key_list.append(k) 
  ```

**gpt_academic Usage Strategies**:

- Accessing AI: Multithreading and single-threading for accessing multiple AIs, including network processing, token limitations, and the integration of API required for accessing AI and the necessary text content.

- Web Service (based on gradio): This includes but is not limited to login, multi-user management, user interface, cookie management, plugin selection and parameter modification, markdown parsing, error capture with web page presentation, frontend and backend communication, file upload and download, and HTML links and redirections used by Scholar Navis.

- Convert Markdown to HTML

- File Management: Handling and usage of files/folders belonging to gpt_academic, as well as PDF full-text retrieval.

- Debugging: Console output with colored content.

- Drawing Mind Maps @Menghuan1918

- To ensure compatibility, the logic for handling thread interruption was referenced.

- Hot Module Replacement

**Scholar Navis Functions Independent of gpt_academic**:

- File Management: File management within the plugin folder (scholar_navis) and management of the summary library itself.

- Configuration file and version management

- Communication and Management of Sqlite3 Database

- Independent markdown to PDF conversion functionality from gpt_academic

- Parsing of csv, yaml files

- Installer for Scholar Navis compatible with gpt_academic (including functionality to install dependency libraries)

- Scholar Navis plugin's multilingual (internationalization) display and multilingual translation tool (supports po and mo formats) 

- Retrieval of metadata, first page content, abstract, DOI number, and title of papers (where part obtained through LLM is done via gpt_academic)

- Article polishing processing logic, LLM request logic, markdown to word (still in testing)

- Management of uploaded PDFs as a summary library and setting of keywords

- Batch article summary analysis and LLM request logic based on keywords

- Logic for interacting with AI, including topic formulation, finding article sources, direct communication processing logic, and LLM request logic

- Logic for in-depth analysis of articles and LLM request logic, as well as design of the summary library article list (HTML)

- Multithreaded download of PubMed OA articles (online service disabled, for local deployment only)

- Customization of user-facing APIs and model customization features added

- Scheduled cleanup of uploaded files and generated file 
