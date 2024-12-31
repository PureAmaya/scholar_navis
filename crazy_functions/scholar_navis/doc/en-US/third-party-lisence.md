Scholar Navis is licensed under the AGPL-3.0 license.

**A translated version for reference only. In case of conflict, the Simplified Chinese version shall be considered as the authoritative one.**

----------------------------

**Third-party packages and projects:**

- gpt_academic: GPL-3.0（Contains revisions, see below.）

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

**The following files in `gpt_academic` were modified on December 28th:**

- `crazy_functions/pdf_fns/parse_pdf_grobid.py` (not internationalized)
- `crazy_functions/pdf_fns/parse_pdf.py` (not internationalized)
- `crazy_functions/pdf_fns/report_gen_html.py`
- `request_llms/生成多种Mermaid图表.py`
- `request_llms/crazy_utils.py`
- `request_llms/bridge_all.py`
- `request_llms/bridge_chatglm.py` (not internationalized)
- `request_llms/bridge_chatglm3.py` (not internationalized)
- `request_llms/bridge_chatglmft.py` (not internationalized)
- `request_llms/bridge_chatglmonnx.py` (not internationalized)
- `request_llms/bridge_chatgpt_vision.py` (not internationalized)
- `request_llms/bridge_chatgpt_website.py` (not internationalized)
- `request_llms/bridge_chatgpt.py`
- `request_llms/bridge_claude.py` (not internationalized)
- `request_llms/bridge_cohere.py` (not internationalized)
- `request_llms/bridge_deepseekcoder.py` (not internationalized)
- `request_llms/bridge_google_gemini.py` (not internationalized)
- `request_llms/bridge_jittorllms.py` (not internationalized)
- `request_llms/bridge_jittorllms_llama.py` (not internationalized)
- `request_llms/bridge_jittorllms_pangualpha.py` (not internationalized)
- `request_llms/bridge_jittorllms_rwkv.py` (not internationalized)
- `request_llms/bridge_llama2.py` (not internationalized)
- `request_llms/bridge_moonshot.py`
- `request_llms/bridge_qwen.py`
- `request_llms/bridge_zhipu.py`
- `request_llms/oai_std_model_template.py`
- `shared_utils/config_loader.py`
- `shared_utils/cookie_manager.py`
- `shared_utils/fastapi_server.py`
- `shared_utils/key_pattern_manager.py`
- `themes/svg`: Removed existing graphics and added images from [Bootstrap Icons](https://icons.getbootstrap.com/)
- `themes/common.js`
- `themes/gui_advanced_plugin_class.py`
- `themes/gui_toolbar.py`
- `themes/init.js`
- `themes/theme.py`
- `check_proxy.py` (only added localization support)
- `config.py`
- `core_functional.py` (only added localization support)
- `crazy_functional.py`
- `toolbox.py`

**scholar navis** also removed the following files and associated code, streamlining the program while maintaining compatibility and retaining features related to paper recognition, extraction, and translation:

- `crazy_functions/SourceCode_Comment.py`
- `crazy_functions/SourceCode_Analyse.py`
- `crazy_functions/Image_Generate.py`
- `crazy_functions/Image_Generate_Wrap.py`
- `crazy_functions/chatglm微调工具.py`
- `crazy_functions/总结音视频.py`
- `crazy_functions/知识库问答.py`
- `crazy_functions/语音助手.py`
- `crazy_functions/生成函数注释.py`
- `crazy_functions/命令行助手.py`
- `crazy_functions/解析JupyterNotebook.py`
- `crazy_functions/交互功能函数模板.py`
- `crazy_functions/互动小游戏.py`
- `crazy_functions/函数动态生成.py`
- `crazy_functions/高级功能函数模板.py`
- `crazy_functions/辅助功能.py`
- `crazy_functions/多智能体.py`
- `crazy_functions/数学动画生成manim.py`
- `crazy_functions/agent_fns`
- `crazy_functions/ast_fns`
- `crazy_functions/diagram_fns`
- `crazy_functions/game_fns`
- `crazy_functions/gen_fns`
- `crazy_functions/multi_stage`
- `crazy_functions/vector_fns`
- `tests` (directory)
- `themes/gradios.py`
- `themes/green.py`
- `themes/gui_floating_menu.py`

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

- Supports the Latest Version of Gradio and Its Features

- File Management: File management within the plugin folder (scholar_navis) and management of the summary library itself.

- Configuration file and version management

- Communication and Management of Sqlite3 Database

- Independent markdown to PDF conversion functionality from gpt_academic

- Parsing of csv, yaml files

- Installer for Scholar Navis compatible with gpt_academic (including functionality to install dependency libraries)

- Scholar Navis plugin's multilingual (internationalization) display and multilingual translation tool (supports po and mo formats) 

- A caching mechanism has been designed for parts that require access to LLMs or need literature information and network requests to reduce the additional time spent due to requests.  

- Retrieval of metadata, first page content, abstract, DOI number, and title of papers (where part obtained through LLM is done via gpt_academic)

- Article polishing processing logic, LLM request logic, markdown to word (still in testing)

- Management of uploaded PDFs as a summary library and setting of keywords

- Batch article summary analysis and LLM request logic based on keywords

- Logic for interacting with AI, including topic formulation, finding article sources, direct communication processing logic, and LLM request logic

- Logic for in-depth analysis of articles and LLM request logic, as well as design of the summary library article list (HTML)

- Multithreaded download of PubMed OA articles

- User Login, Registration, and Information Storage (Sensitive Data Encrypted Where Possible). Supports anonymous usage (Sensitive Information Also Encrypted Locally)

- Customization of user-facing APIs and model customization features added

- Scheduled cleanup of uploaded files and generated file 

- Web service: Online PDF viewing (Based on `pdf.js`)

- API Service: Simple Notification

- Extract useful sentences and provide translations for reading. 
