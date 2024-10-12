Scholar Navis 使用 GPL-3.0 license 授權證

**此為翻譯版本，僅供參考。如有衝突，以簡體中文版為準。**

---

以下是基於**gpt_academic 添加的第三方項目**（除 gpt_academic 外，所有項目均未進行任何源碼修改）：

| 第三方庫或工具                                                                                 | 授權證                | 使用策略                                                              |
| --------------------------------------------------------------------------------------- | ------------------ | ----------------------------------------------------------------- |
| <a href="https://github.com/binary-husky/gpt_academic" target="_blank">GPT Academic</a> | GPL-3.0 license    | 作為該工具的插件，無法獨立運行。關於 gpt_academic 的詳細修改內容和使用策略請見下文。                 |
| <a href="https://pypi.org/project/PyYAML" target="_blank">PyYAML</a>                    | MIT License        | 使用庫，yaml文件解析                                                      |
| <a href="https://pypi.org/project/beautifulsoup4" target="_blank">beautifulsoup4</a>    | MIT License        | 使用庫，網絡請求處理                                                        |
| <a href="https://pypi.org/project/requests/" target="_blank">requests</a>               | Apache-2.0 license | 使用庫，網絡請求                                                          |
| <a href="https://pypi.org/project/python-docx" target="_blank">python-docx</a>          | MIT License        | 使用庫，解析docx並獲取文本內容，將 Markdown 轉換為 Word（所屬功能仍在測試）                   |
| <a href="https://pypi.org/project/PyMuPDF/" target="_blank">PyMuPDF</a>                 | AGPL-3.0 license   | 使用庫，將 HTML 轉換為 PDF                                                |
| <a href="https://github.com/marktext/marktext" target="_blank">MarkText</a>             | MIT License        | 使用該軟件將markdown轉換為HTML，並對HTML進行了修改                                 |
| <a href="https://github.com/mozilla/pdf.js" target="_blank">PDF.js</a>                  | Apache-2.0 license | 直接使用其Prebuilt軟件包。源碼沒有發生修改，用於在線瀏覽PDF。完整的内容位於 `web_services\pdf.js` |
| <a href="https://github.com/MohammadYounes/AlertifyJS" target="_blank">AlertifyJS</a>   | GPL-3.0 license    | 使用庫，用於製作通知                                                        |
| <a href="https://github.com/twbs/bootstrap" target="_blank">Bootstrap</a>               | MIT License        | 使用庫，用於AlertifyJS的CSS樣式                                            |

**gpt_academic 中產生修改的部分如下：**

- 原則上是盡可能減少對 gpt_academic 的修改，以方便移植或使用其他的版本。

- 因為對 gpt_academic 的源碼進行了修改（主要是使其能夠調用 Scholar Navis 並使用一些新增的功能或機制），受到 GPL-3.0 協定的約束，必須將 gpt_academic 的源碼一併發布，並且亦需標明修改內容。

- 通常情況下，新添加的**代碼文件**，如果沒有對原有代碼進行修改，則不會列出。

- 已刪除所有與Docker相關的文件，因為目前Scholar Navis還不支持Docker。 

- `main.py`: 第60行，發生了修改。
  
  ```python
   # original
  from themes.theme import js_code_for_toggle_darkmode, js_code_for_persistent_cookie_init
   # motified
  from themes.theme import js_code_for_persistent_cookie_init
  ```

- `main.py`: 約在第63行添加了以下內容。這樣做可以實現簡易的通知顯示。
  
  ```python
  # SCHOAR NAVIS 
  sn_version_fp = os.path.join(os.path.dirname(__file__),'crazy_functions','scholar_navis','version')
  if os.path.exists(sn_version_fp):
      with open(sn_version_fp,'r',encoding='utf-8') as f:
           title_html = f"<br><h1 align=\"center\">Scholar Navis {f.read()} (GPT 学术优化 {get_current_version()})</h1>{theme_declaration}"
   else:title_html = f"<br><h1 align=\"center\">Scholar Navis</h1>{theme_declaration}"
  
  notification_fp = os.path.join(os.path.dirname(__file__),'notification','notification.txt')
  if os.path.exists(notification_fp):
      with open(notification_fp,'r',encoding='utf-8') as f:
          title_html = title_html + f'<p style="text-align: left; margin-left: 20px; margin-right: 20px;">{f.read()}</p>'
  ```

- `main.py`：約第67行，添加以下內容，用於顯示 Scholar Navis 的版本號。
  
  ```python
     ... 上略 ...
           title_html = f"<br><h1 align=\"center\">GPT 学术优化 {get_current_version()} (Scholar Navis {f.read()})</h1>{theme_declaration}"
      else:title_html = f"<br><h1 align=\"center\">GPT 学术优化 {get_current_version()}</h1>{theme_declaration}"
  ```

- `main.py`：約第111行，發生修改，用於區別這是修改版。
  
  ```python
   # original
   with gr.Blocks(title="GPT 学术优化", theme=set_theme, analytics_enabled=False, css=advanced_css) as app_block:
   # motified
   with gr.Blocks(title="GPT 学术优化 (Scholar Navis 修改版)", theme=set_theme, analytics_enabled=False, css=advanced_css) as app_block:
  ```

- `main.py`：在120行添加AI警告
  
  ```python
  gr.HTML('<strong>下方内容为 AI 生成，不代表任何立场，可能存在片面甚至错误。仅供参考，开发者及其组织不负任何责任。</strong>')
  ```

- `main.py`：約第196行，發生修改，接入自定義API-KEY功能，將一些.js文件內容移出並合併入相應的.js文件中。
  
  ```python
  # original
  checkboxes, checkboxes_2, max_length_sl, theme_dropdown, system_prompt, file_upload_2, md_dropdown, top_p, temperature = \
              define_gui_toolbar(AVAIL_LLM_MODELS, LLM_MODEL, INIT_SYS_PROMPT, THEME, AVAIL_THEMES, ADD_WAIFU, help_menu_description, js_code_for_toggle_darkmode)
   # motified
  checkboxes, checkboxes_2, max_length_sl, theme_dropdown, system_prompt, file_upload_2, md_dropdown, top_p, temperature,custom_api_key = \
              define_gui_toolbar(AVAIL_LLM_MODELS, LLM_MODEL, INIT_SYS_PROMPT, THEME, AVAIL_THEMES, ADD_WAIFU, help_menu_description)
  ```

- `main.py`：約第229行，發生修改，接入自定義API-KEY功能，將一些JavaScript代碼從.py文件中移除，並合併到相應的.js文件中。
  
  ```python
   # original
   input_combo = [cookies, max_length_sl, md_dropdown, txt, txt2, top_p, temperature, chatbot, history, system_prompt, plugin_advanced_arg]
          input_combo_order = ["cookies", "max_length_sl", "md_dropdown", "txt", "txt2", "top_p", "temperature", "chatbot", "history", "system_prompt", "plugin_advanced_arg"]
    # motified
   input_combo = [cookies, max_length_sl, md_dropdown, txt, txt2, top_p, temperature, chatbot, history, system_prompt, plugin_advanced_arg,custom_api_key]
          input_combo_order = ["cookies", "max_length_sl", "md_dropdown", "txt", "txt2", "top_p", "temperature", "chatbot", "history", "system_prompt", "plugin_advanced_arg",'custom_api_key']
  ```

- `main.py`：第362行，已將自動更新程序註解掉。 
  
  ```python
  def auto_updates(): time.sleep(0); # auto_update() scholar naivs由于修改了代码，所以需要禁用自动更新
  ```

- `config.py`：第65行添加新內容： 
  
  ```python
  # 允许用户自行设定API和URL重定向（储存在localstorage中）
  ALLOW_CUSTOM_API_KEY = True
  ```

- `config.py`：預設模型（LLM_MODEL）更改为「glm-4-flash」；為AVAIL_LLM_MODELS添加了GLM系列、Qwen系列、Moonshot系列和Deepseek系列模型，並補充了一些GPT模型（均為原gpt_academic已經支持的模型）；多個模型（MULTI_QUERY_LLM_MODELS）更改为更廉價的模型「gpt-3.5-turbo&glm-4-flash」。
  
  `crazy_functional.py`：約 400 行處添加了下面的內容。`setup.py` 亦可以產生下述修改。這樣修改是為了 gpt_academic 能夠使用 Scholar Navis
  
  ```python
  ###### SCHOLAR NAVIS START ########
  from shared_utils.scholar_navis.gpt_academic_handler import registrator
  function_plugins = registrator(function_plugins)
  ##### SCHOLAR NAVIS END - UNINSTALL: DELETE THESE ######
  ```

- `config_private.py`：約 118 行處產生了以下修改內容。`setup.py` 亦可以產生下述修改，或產生一個含有下述修改內容的 config_private.py。這樣修改是為了用戶能通過 gpt_academic 的網絡服務使用 Scholar Navis。
  
  ```python
  # 原始内容：
  DEFAULT_FN_GROUPS = ['对话', '编程', '学术', '智能体']
  
  # 修改後的內容：
  DEFAULT_FN_GROUPS = ['Scholar Navis']
  
  # 有時候修改後的內容可能會包含原始的內容，例如：
  DEFAULT_FN_GROUPS = ['Scholar Navis','对话', '编程', '学术', '智能体']
  ```

- `toolbox.py`：添加了 import 
  
  ```python
  from shared_utils.scholar_navis.user_custom_manager import get_api_key,get_url_redirect
  from shared_utils.scholar_navis.statistics import user_useage_log
  ```

- `toolbox.py`：裝飾器方法（decorated method）添加了參數 user_custom_data: dict

- `toolbox.py` ：第 40 行，加入 `from shared_utils.statistics import user_usage_log` 

- `toolbox.py`：第98行添加如下內容： 
  
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

- `toolbox.py` ：第 147 行，添加以下內容：    
  
  ```python
   # 记录日志
  user_useage_log(request,user_name,llm_model,f.__name__,system_prompt,txt_passon)
  ```

- `toolbox.py`：對 cookies 和 llm_kwargs 的鍵值進行了修改，並為 llm_kwargs 添加了新的鍵值對。 

- `toolbox.py`：在第517行左右添加了修正文字編碼的內容，用以修復解壓後產生的亂碼。  
  
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

- `toolbox.py`：約564行程，修改如下：   
  
  ```python
      # 整理文件集合 输出消息
      files = glob.glob(f"{target_path_base}/**/*", recursive=True)
      moved_files = []
      for fp in files: # 修复不受cp437支持而产生的乱码
          if os.path.isfile(fp):
              basename = correct_code_error(os.path.basename(fp))
              correct_fp = os.path.join(os.path.dirname(fp),basename)
              os.rename(fp,correct_fp)
              moved_files.append(correct_fp)
          else:moved_files.append(fp)
  ```

- `multi_language.py`：具體修改如下。這裡添加這些內容是為了在翻譯 gpt_academic 之後，Scholar Navis 可以正常運行。
  
  ```python
  # 43行
  # 原始
  blacklist = ['multi-language', CACHE_FOLDER, '.git', 'private_upload', 'multi_language.py', 'build', '.github', '.vscode', '__pycache__', 'venv']
  # 修改後
  blacklist = ['multi-language', CACHE_FOLDER, '.git', 'private_upload', 'multi_language.py', 'build', '.github', '.vscode', '__pycache__', 'venv','scholar_navis']
  
  # 約526行，新增了如下內容
  def  step_ex_scholar_navis():
      ```加入的代碼```
  
  # 588行，添加了如下内容
  step_ex_scholar_navis()
  ```

- `themes/init.js`：大約在第九行處，註釋掉了關於 welcomeMessage 的內容（因為這些內容可能會引發錯誤）。
  
  ```js
  // 以下被註釋掉的部分則為修改的部分
  
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

- `themes/common.css`：在文件末尾添加了用於 HTML 的 summary 的樣式內容，已在源碼中注明

- `themes/common.js`：約第758行，發生修改：
  
  ```js
  // 原始
  const always_preserve = 2;
  // 修改後
  const always_preserve = btn_list.length;
  ```

- `themes/common.js`：約第1340行，將原來在 `theme.py` 中的黑暗模式代碼（function js_code_for_toggle_darkmode）移動至此

- `themes/common.py`：約第3行，添加用於獲取用戶啟用自定義功能的獲取方法 
  
  ```python
  # original
  CODE_HIGHLIGHT, ADD_WAIFU, LAYOUT = get_conf("CODE_HIGHLIGHT", "ADD_WAIFU", "LAYOUT")
  # motified
  CODE_HIGHLIGHT, ADD_WAIFU, LAYOUT,ALLOW_CUSTOM_API_KEY = get_conf("CODE_HIGHLIGHT", "ADD_WAIFU", "LAYOUT",'ALLOW_CUSTOM_API_KEY')
  ```

- `themes/common.py`：約第35行，註釋掉 "themes/welcome.js"，取消迎賓界面（有bug） 

- `themes/common.py`：約第35和38行，添加載入 scholar_navis 初始化 js 和自定義 API-KEY 功能的 js
  
  ```python
  "themes/scholar_navis/scholar_navis_init.js"
  if ALLOW_CUSTOM_API_KEY:common_js_path_list.append("themes/scholar_navis/custom_api_key.js")
  ```

- `themes/gui_advanced_plugin_class.py`：約第3、45行，添加了高级插件熱加載功能支持（熱加載為 gpt_acadmic 自有功能）
  
  ```python
  # line 3: HotReload added
  from toolbox import format_io, find_free_port, on_file_uploaded, on_report_generated, get_conf, ArgsGeneralWrapper, DummyWith,HotReload
  # line 45 original:
  plugin_exe = plugin_obj.execute
  # line 45 motified:
  if plugins[which_plugin].get('ClassHotReload',False):
  ```

- `themes/gui_toolbar.py`：添加了 import；第9行定義的 `define_gui_toolbar` 去除了 `js_code_for_toggle_darkmode` 参数；第7行，添加了 `ALLOW_CUSTOM_API_KEY = get_conf('ALLOW_CUSTOM_API_KEY')`；`define_gui_toolbar` 的返回值添加了 `user_custom_data` 参数

- `themes/gui_toolbar.py`：第17行添加了 `as model_switch_tab`，用於顯示添加的自定義模型：
  
  ```python
  with gr.Tab("更换模型", elem_id="interact-panel") as model_switch_tab:
  ```

- `themes/gui_toolbar.py`：第30行添加了新的 `gradio.tab`：API-KEY；文件末尾定義了新的方法 `_add_custom_model` 用於添加自定義模型

- `themes/theme.py`：移除了原有的黑暗模式代碼（`js_code_for_toggle_darkmode`），並合並到 `common.js` 中

- `request_llms/bridge_all.py`：引入了 `model_info_class` 取代了以往的 `model_info`，並提供了自定義的功能（兼容原有功能）；引入了 `extend_llm_support` 函數，取代了舊有的 api2d、llama、vllm 對齊，並為自定義模型提供了支持。

- `request_llms/bridge_ChatGPT.py`：約第31行，添加了 `_get_url_redirect_and_check`，用於決定是否可以使用 API 自定義重定向功能，並且該功能取代了原有的 `verify_endpoint`

- `request_llms/bridge_ChatGPT.py`：約第218行，發生了修改，給用戶提示添加自定義模型/api的提醒
  
  ```python
  # original
  chatbot.append((inputs, "缺少api_key。\n\n1. 临时解决方案：直接在输入区键入api_key，然后回车提交。\n\n2. 长效解决方案：在config.py中配置。"))
  # motified
  chatbot.append((inputs, "缺少api_key。\n\n1. 临时解决方案：直接在输入区键入api_key，然后回车提交。\n\n2. 长效解决方案：在上方的`API_KEY`中输入您的api-key。"))
  ```

- `request_llms/bridge_ChatGPT.py`：約第478行，添加了自定義模型便簽裁剪功能。
  
  ```python
  if llm_kwargs['llm_model'].startswith('custom-'):
          model = llm_kwargs['llm_model'][len('custom-'):]
  ```

- `request_llms/bridge_moonshot.py`：約第18-21行、158行、175行，添加了api_key參數，用於使用自定義api-key。

- `request_llms/bridge_moonshot.py`：約第153行、174行，修復了原有的空輸入報錯問題。
  
  ```python
  if not inputs:inputs = ' ' # 空白输入报错
  ```

- `request_llms/bridge_qwen.py`：約第18行、35行、46行、56行，添加了api_key參數，用於使用自定義api-key。

- `request_llms/com_qwenapi.py`：約第9行、16行、20行，添加了api_key參數，用於使用自定義api-key。

- `request_llms/bridge_zhipu.py`：約第10行、31行、37行、65行、97行，添加了api_key參數，用於使用自定義api-key。

- `request_llms/com_zhipuglm.py`：約第24行，添加了api_key參數，用於使用自定義api-key。

- `request_llms/oai_std_model_template.py`：約第132行，刪除了原有的API-KEY獲取方法。

- `request_llms/model_info.py`：為上文提到的model.info的取代組件，除了支持原list的功能外，還支持自定義模型的調用。

- `shared_utils/fastapi_server.py`：約216行，為網頁添加在線服務功能（目前只是pdf.js的在線瀏覽功能） 
  
  ```python
      # web api和服务
      from .scholar_navis_web_services import enable_api,enable_services
      enable_api(gradio_app);enable_services(gradio_app)
  ```

- `shared_utils/key_pattern_manager.py`：約第70行，添加了自定義模型支持；約第73行，添加內容，讓自定義模型也能支持非標準的api2d的api。    
  
  ```python
  # line 70
  if llm_model.startswith('gpt-') or llm_model.startswith('one-api-') or llm_model.startswith('custom-'):
  # line 73
  if is_api2d_key(k): avail_key_list.append(k)
  ```

**gpt_academic 的使用策略**：

- 存取 AI：多線程和單線程對多個 AI 的存取，以及其中發生的網絡處理、token 限制、和存取 AI 所需的 API 及其所需文本內容的整合。

- 網絡服務（基於 gradio）。包含但不限於登錄、多用戶管理、用戶界面、cookie 管理、插件選擇和參數修改、markdown 解析、捕捉錯誤後網頁呈現、前后端通訊、文件上傳和下載以及 Scholar Navis 用到的 HTML 的鏈接和跳轉。

- Markdown轉HTML

- 文件管理：gpt_academic 所屬文件/資料夾的處理和使用、PDF 全文獲取。

- 調試：控制台輸出彩色內容。

- 繪製思維導圖 @Menghuan1918

- 為了確保兼容性，參考了對於多線程中止的處理邏輯。

- 模組熱替換 

- 保留了gpt_academic幾乎全部的功能和插件。 

**Scholar Navis 獨立於 gpt_academic 的功能**：

- 文件管理：插件資料夾（scholar_navis）內部的文件管理、總結庫自身的管理。

- 配置文件和版本管理。

- Sqlite3 數據庫的通訊和管理。

- 使用與 gpt_academic 独立的 markdown 轉 pdf 功能。

- csv、yaml 文件解析。

- 适用于 gpt_academic 的 Scholar Navis 安裝器（含有安裝依賴庫的功能）。

- Scholar Navis 插件的多元語言（國際化）顯示與多元語言翻譯工具（支援 po 和 mo 格式） 

- 為了那些需要訪問LLM（大型語言模型）或需要文獻信息、進行網絡請求的部分，我們設計了緩存機制，以減少因為請求而產生的額外耗時。  

- 獲取論文的元數據、第一頁內容、摘要、DOI 號和標題（其中通過 LLM 獲取的部分是通過 gpt_academic 結行的）。

- 文章修飾處理邏輯、LLM 請求邏輯，markdown 轉 word（仍在測試）。

- 將上傳的 pdf 作為總結庫進行管理和關鍵詞設定。

- 基於關鍵詞的批量文章總結分析和 LLM 請求邏輯。

- 与 AI 交流的邏輯，包含擬定課題、尋找文章來源、直接交流的處理邏輯和 LLM 請求邏輯。

- 精細分析文章的處理邏輯和 LLM 請求邏輯、以及總結庫文章包含列表（HTML）設計。 

- PubMed OA 文章的多執行緒下載（在線服務關閉，僅限本地部署）

- 面向用戶的 API 自定義與模型自定義功能添加

- 上傳文件及生成文件的定期清理

- 網絡服務：在線PDF瀏覽

- API服務：簡易維護提醒
