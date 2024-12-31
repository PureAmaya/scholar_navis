Scholar Navis 使用 AGPL-3.0 license 许可证

----------------------------

**第三方包与项目：**

- gpt_academic: GPL-3.0（含有修改，见下文）

- aiofiles: Apache-2.0 license

- aiohttp: Apache-2.0 license

- alertifyJS:  GPL-3.0 license

- argon2-cffi: MIT License

- beautifulsoup4: MIT License

- Bootstrap: MIT License

- Bootstrap Icons: MIT License

- colorama: BSD License

- dashscope: Apache-2.0 license

- fastapi：MIT License

- fitz (pymupdf)：GNU AFFERO GPL 3.0

- gradio：Apache-2.0 license

- gradio_modal：Apache-2.0 license

- latex2mathml：MIT License (MIT)

- Markdown：BSD-3-Clause license

- Mermaid: MIT license

- numpy：BSD License

- pandas：BSD-3-Clause license

- pydantic：MIT License

- pymdown-extensions: MIT License

- PyPDF2：BSD License

- python_docx：MIT License

- PyYAML：MIT License

- rarfile：ISC License

- Requests：Apache-2.0 license

- rich：MIT License

- rjsmin: Apache-2.0 license

- starlette：BSD License

- tiktoken：MIT License

- uvicorn：BSD License (BSD-3-Clause)

- websockets：BSD License (BSD-3-Clause)

- zhipuai：unknown

**gpt_academic中产生修改的部分如下：**

- crazy_functions/pdf_fns/parse_pdf_grobid.py （未进行国际化，修改于12月28日）

- crazy_functions/pdf_fns/parse_pdf.py   （未进行国际化，修改于12月28日）

- crazy_functions/pdf_fns/report_gen_html.py  （修改于12月28日）

- request_llms/生成多种Mermaid图表.py  （修改于12月28日）

- request_llms/crazy_utils.py  （修改于12月28日）

- request_llms/bridge_all.py   （修改于12月28日）

- request_llms/bridge_chatglm.py  （未进行国际化，修改于12月28日）

- request_llms/bridge_chatglm3.py  （未进行国际化，修改于12月28日）

- request_llms/bridge_chatglmft.py  （未进行国际化，修改于12月28日）

- request_llms/bridge_chatglmonnx.py   （未进行国际化，修改于12月28日）

- request_llms/bridge_chatgpt_vision.py     （未进行国际化，修改于12月28日）

- request_llms/bridge_chatgpt_website.py   （未进行国际化，修改于12月28日）

- request_llms/bridge_chatgpt.py     （修改于12月28日）

- request_llms/bridge_claude.py（未进行国际化，修改于12月28日）

- request_llms/bridge_cohere.py   （未进行国际化，修改于12月28日）

- request_llms/bridge_deepseekcoder.py  （未进行国际化，修改于12月28日）

- request_llms/bridge_google_gemini.py   （未进行国际化，修改于12月28日）

- request_llms/bridge_jittorllms.py   （未进行国际化，修改于12月28日）

- request_llms/bridge_jittorllms_llama.py     （未进行国际化，修改于12月28日）

- request_llms/bridge_jittorllms_pangualpha.py   （未进行国际化，修改于12月28日）

- request_llms/bridge_jittorllms_rwkv.py    （未进行国际化，修改于12月28日）

- request_llms/bridge_llama2.py （未进行国际化，修改于12月28日）

- request_llms/bridge_moonshot.py  （修改于12月28日）

- request_llms/bridge_qwen.py  （修改于12月28日）

- request_llms/bridge_zhipu.py  （修改于12月28日）

- request_llms/oai_std_model_template.py  （修改于12月28日）

- shared_utils/config_loader.py  （修改于12月28日）

- shared_utils/cookie_manager.py  （修改于12月28日）

- shared_utils/fastapi_server.py  （修改于12月28日）

- shared_utils/key_pattern_manager.py  （修改于12月28日）

- themes/svg: 删除了原有的图形，添加了来自的<a href="https://icons.getbootstrap.com/" target="_blank">Bootstrap Icons</a>图片  （修改于12月28日）

- themes/common.js  （修改于12月28日）

- themes/gui_advanced_plugin_class.py  （修改于12月28日）

- themes/gui_toolbar.py  （修改于12月28日）

- themes/init.js  （修改于12月28日）

- themes/theme.py  （修改于12月28日）

- check_proxy.py (仅添加本地化支持，修改于12月28日)

- config.py  （修改于12月28日）

- core_functional.py (仅添加本地化支持，修改于12月28日)

- crazy_functional.py  （修改于12月28日）

- toolbox.py  （修改于12月28日）

**scholar navis也删除了这些文件和关联的代码：**

精简整个程序，在保证兼容性的前提下，保留与论文识别提取和翻译有关的功能。

- crazy_functions/SourceCode_Comment.py  （修改于12月28日）

- crazy_fcuntions/SourceCode_Analyse.py  （修改于12月28日）

- crazy_functions/Image_Generate.py  （修改于12月28日）

- crazy_functions/Image_Generate_Wrap.py  （修改于12月28日）

- crazy_functions/chatglm微调工具.py  （修改于12月28日）

- crazy_functions/总结音视频.py  （修改于12月28日）

- crazy_functions/知识库问答.py  （修改于12月28日）

- crazy_functions/语音助手.py  （修改于12月28日）

- crazy_functions/生成函数注释.py  （修改于12月28日）

- crazy_functions/命令行助手.py  （修改于12月28日）

- crazy_functions/解析JupyterNotebook.py  （修改于12月28日）

- crazy_functions/交互功能函数模板.py  （修改于12月28日）

- crazy_functions/互动小游戏.py  （修改于12月28日）

- crazy_functions/函数动态生成.py  （修改于12月28日）

- crazy_functions/高级功能函数模板.py  （修改于12月28日）

- crazy_functions/辅助功能.py  （修改于12月28日）

- crazy_functions/多智能体.py  （修改于12月28日）

- crazy_functions/数学动画生成manim.py  （修改于12月28日）

- crazy_functions/agent_fns  （修改于12月28日）

- crazy_functions/ast_fns  （修改于12月28日）

- crazy_functions/diagram_fns  （修改于12月28日）

- crazy_functions/game_fns  （修改于12月28日）

- crazy_functions/gen_fns  （修改于12月28日）

- crazy_functions/multi_stage  （修改于12月28日）

- crazy_functions/vector_fns  （修改于12月28日）

- tests (目录)  （修改于12月28日）

- themes/gradios.py  （修改于12月28日）

- themes/green.py  （修改于12月28日）

- themes/gui_floating_menu.py  （修改于12月28日）

**gpt_academic的使用策略**：

- 访问AI：多线程和单线程对于多个AI的访问，以及其中发生的网络处理、token限制、和访问AI所需的API及其所需文本内容的整合。

- web服务（基于gradio）。包含但不限于登录、多用户管理、用户界面、cookie管理、插件选择和参数修改、markdown解析、捕捉错误后网页呈现、前后端通讯、文件上传和下载以及 Scholar Navis 用到的HTML的链接和跳转。

- Markdown转HTML

- 文件管理：gpt_academic所属文件/文件夹的处理和使用、PDF全文获取

- 调试：控制台输出彩色内容。

- 绘制思维导图 @Menghuan1918

- 为了保证兼容性，参考了对于多线程中止的处理逻辑

- 模块热加载

**Scholar Navis 独立于 gpt_academic 的功能**：

- 支持最新版的gradio和特性

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

- PubMed OA 文章的多线程下载

- 用户登录、注册、信息的保存与记录（敏感尽可能进行了加密）。支持匿名使用（敏感信息也在本地进行了加密）

- 面向用户的API自定义与模型自定义添加功能

- 上传文件和产生文件的定时清理

- web服务：在线PDF浏览（基于pdf.js）

- API服务：简易通知

- 摘取有用的语句，并提供翻译以便阅读
