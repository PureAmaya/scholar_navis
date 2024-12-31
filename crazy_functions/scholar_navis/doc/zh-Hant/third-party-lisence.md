Scholar Navis 使用 AGPL-3.0 license 授權證

**此為翻譯版本，僅供參考。如有衝突，以簡體中文版為準。**

---

**第三方套件與專案：**

- gpt_academic: GPL-3.0（含有修改，見下文）

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

**在 `gpt_academic` 中，以下文件於12月28日進行了修改：**

- `crazy_functions/pdf_fns/parse_pdf_grobid.py` （未國際化）
- `crazy_functions/pdf_fns/parse_pdf.py` （未國際化）
- `crazy_functions/pdf_fns/report_gen_html.py`
- `request_llms/生成多种Mermaid图表.py`
- `request_llms/crazy_utils.py`
- `request_llms/bridge_all.py`
- `request_llms/bridge_chatglm.py` （未國際化）
- `request_llms/bridge_chatglm3.py` （未國際化）
- `request_llms/bridge_chatglmft.py` （未國際化）
- `request_llms/bridge_chatglmonnx.py` （未國際化）
- `request_llms/bridge_chatgpt_vision.py` （未國際化）
- `request_llms/bridge_chatgpt_website.py` （未國際化）
- `request_llms/bridge_chatgpt.py`
- `request_llms/bridge_claude.py` （未國際化）
- `request_llms/bridge_cohere.py` （未國際化）
- `request_llms/bridge_deepseekcoder.py` （未國際化）
- `request_llms/bridge_google_gemini.py` （未國際化）
- `request_llms/bridge_jittorllms.py` （未國際化）
- `request_llms/bridge_jittorllms_llama.py` （未國際化）
- `request_llms/bridge_jittorllms_pangualpha.py` （未國際化）
- `request_llms/bridge_jittorllms_rwkv.py` （未國際化）
- `request_llms/bridge_llama2.py` （未國際化）
- `request_llms/bridge_moonshot.py`
- `request_llms/bridge_qwen.py`
- `request_llms/bridge_zhipu.py`
- `request_llms/oai_std_model_template.py`
- `shared_utils/config_loader.py`
- `shared_utils/cookie_manager.py`
- `shared_utils/fastapi_server.py`
- `shared_utils/key_pattern_manager.py`
- `themes/svg`: 刪除原有圖形，新增來自 [Bootstrap Icons](https://icons.getbootstrap.com/) 的圖片
- `themes/common.js`
- `themes/gui_advanced_plugin_class.py`
- `themes/gui_toolbar.py`
- `themes/init.js`
- `themes/theme.py`
- `check_proxy.py` （僅添加本地化支持）
- `config.py`
- `core_functional.py` （僅添加本地化支持）
- `crazy_functional.py`
- `toolbox.py`

**scholar navis** 也刪除了以下文件及相關代碼，並在保證兼容性的前提下，精簡了程序，保留了與論文識別提取和翻譯相關的功能 （12月28日）：

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
- `tests` （目錄）
- `themes/gradios.py`
- `themes/green.py`
- `themes/gui_floating_menu.py`

**gpt_academic 的使用策略**：

- 存取 AI：多線程和單線程對多個 AI 的存取，以及其中發生的網絡處理、token 限制、和存取 AI 所需的 API 及其所需文本內容的整合。

- 網絡服務（基於 gradio）。包含但不限於登錄、多用戶管理、用戶界面、cookie 管理、插件選擇和參數修改、markdown 解析、捕捉錯誤後網頁呈現、前后端通訊、文件上傳和下載以及 Scholar Navis 用到的 HTML 的鏈接和跳轉。

- Markdown轉HTML

- 文件管理：gpt_academic 所屬文件/資料夾的處理和使用、PDF 全文獲取。

- 調試：控制台輸出彩色內容。

- 繪製思維導圖 @Menghuan1918

- 為了確保兼容性，參考了對於多線程中止的處理邏輯。

- 模組熱替換 

**Scholar Navis 獨立於 gpt_academic 的功能**：

- 支援最新版的 Gradio 及其特性

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

- 用戶登錄、註冊、信息的保存與記錄（敏感信息盡可能進行了加密）。支援匿名使用（敏感信息也在本地進行了加密）。

- PubMed OA 文章的多執行緒下載

- 面向用戶的 API 自定義與模型自定義功能添加

- 網絡服務：在線PDF瀏覽（基於 `pdf.js`）

- API 服務：簡易通知

- 摘取有用的语句，并提供翻译以便阅读 
