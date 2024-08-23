Scholar Navis 使用 GPL-3.0 license 授權證

**gpt_academic 的版權、其所有的除 Scholar Navis 之外的插件、部分等仍然為原作者、原貢獻者所有，即 Scholar Navis 仅供 `crazy_functions\scholar_navis` 中的源碼聲明版權，其他目錄中源碼的版權均歸原作者所有**。

---

以下是使用或依賴的項目：

| 第三方庫或工具                                                                                 | 授權證                                  | 使用策略                                              |
| --------------------------------------------------------------------------------------- | ------------------------------------ | ------------------------------------------------- |
| <a href="https://github.com/binary-husky/gpt_academic" target="_blank">GPT Academic</a> | GPL-3.0 license                      | 作為該工具的插件，無法獨立運行。關於 gpt_academic 的詳細修改內容和使用策略請見下文。 |
| <a href="https://pypi.org/project/PyPDF2/" target="_blank">PyPDF2</a>                   | BSD License                          | 使用庫，pdf處理                                         |
| <a href="https://pypi.org/project/PyYAML" target="_blank">PyYAML</a>                    | MIT License                          | 使用庫，yaml文件解析                                      |
| <a href="https://pypi.org/project/beautifulsoup4" target="_blank">beautifulsoup4</a>    | MIT License                          | 使用庫，網絡請求處理                                        |
| <a href="https://pypi.org/project/requests/" target="_blank">requests</a>               | Apache Software License (Apache-2.0) | 使用庫，網絡請求                                          |
| <a href="https://pypi.org/project/python-docx" target="_blank">python-docx</a>          | MIT License                          | 使用庫，解析docx並獲取文本內容，將 Markdown 轉換為 Word（所屬功能仍在測試）   |
| <a href="https://pypi.org/project/markdown-pdf/" target="_blank">markdown-pdf</a>       | MIT License                          | 使用庫，將markdown轉換為pdf                               |
| <a href="https://github.com/marktext/marktext" target="_blank">MarkText</a>             | MIT License                          | 使用該軟件將markdown轉換為HTML，並對HTML進行了修改                 |

**gpt_academic 中產生修改的部分如下：**

1. 原則上是盡可能減少對 gpt_academic 的修改，以方便移植或使用其他的版本。

2. 因為對 gpt_academic 的源碼產生了修改（主要是使其能夠調用 Scholar Navis ），受限于 GPL-3.0 的約束，需要將 gpt_academic 的源碼一並發布，並且亦需注明修改內容。

3. crazy_functional.py：約 400 行處添加了下面的內容。`setup.py` 亦可以產生下述修改

4. ```python
   ###### SCHOLAR NAVIS START ########
   from crazy_functions.scholar_navis.scripts.tools.gpt_academic_handler import registrator
   function_plugins = registrator(function_plugins)
   ##### SCHOLAR NAVIS END - UNINSTALL: DELETE THESE ######
   ```

> 這樣修改是為了 gpt_academic 能夠使用 Scholar Navis

2. config_private.py：約 118 行處產生了以下修改內容。`setup.py` 亦可以產生下述修改，或產生一個含有下述修改內容的 config_private.py

3. ```python
   # 原始内容：
   DEFAULT_FN_GROUPS = ['对话', '编程', '学术', '智能体']
   
   # 修改後的內容：
   DEFAULT_FN_GROUPS = ['Scholar Navis']
   
   # 有時候修改後的內容可能會包含原始的內容，例如：
   DEFAULT_FN_GROUPS = ['Scholar Navis','对话', '编程', '学术', '智能体']
   ```

> 這樣修改是為了用戶能通過 gpt_academic 的網絡服務使用 Scholar Navis。

**gpt_academic 的使用策略**：

- 存取 AI：多線程和單線程對多個 AI 的存取，以及其中發生的網絡處理、token 限制、和存取 AI 所需的 API 及其所需文本內容的整合。

- 網絡服務（基於 gradio）。包含但不限於登錄、多用戶管理、用戶界面、cookie 管理、插件選擇和參數修改、markdown 解析、捕捉錯誤後網頁呈現、前后端通訊、文件上傳和下載以及 Scholar Navis 用到的 HTML 的鏈接和跳轉。

- 文件管理：gpt_academic 所屬文件/資料夾的處理和使用、PDF 全文獲取。

- 調試：控制台輸出彩色內容。

- 繪製思維導圖 @Menghuan1918

- 為了確保兼容性，參考了對於多線程中止的處理邏輯。

**Scholar Navis 獨立於 gpt_academic 的功能**：

- 文件管理：插件資料夾（scholar_navis）內部的文件管理、總結庫自身的管理。

- 配置文件和版本管理。

- Sqlite3 數據庫的通訊和管理。

- 使用與 gpt_academic 独立的 markdown 轉 pdf 功能。

- csv、yaml 文件解析。

- 适用于 gpt_academic 的 Scholar Navis 安裝器（含有安裝依賴庫的功能）。

- 多語言（國際化）顯示與多語言翻譯工具（支持 po 和 mo 格式）。

- 獲取論文的元數據、第一頁內容、摘要、DOI 號和標題（其中通過 LLM 獲取的部分是通過 gpt_academic 結行的）。

- 文章修飾處理邏輯、LLM 請求邏輯，markdown 轉 word（仍在測試）。

- 將上傳的 pdf 作為總結庫進行管理和關鍵詞設定。

- 基於關鍵詞的批量文章總結分析和 LLM 請求邏輯。

- 与 AI 交流的邏輯，包含擬定課題、尋找文章來源、直接交流的處理邏輯和 LLM 請求邏輯。

- 精細分析文章的處理邏輯和 LLM 請求邏輯、以及總結庫文章包含列表（HTML）設計。

- PubMed OA 文章的多線程下載。
