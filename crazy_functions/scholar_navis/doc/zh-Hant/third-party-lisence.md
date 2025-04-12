Scholar Navis 使用 AGPL-3.0 許可證。

**此翻譯版本僅供參考，一切以簡體中文版為準。**

---

**第三方套件與專案：**

| 名稱                           | 許可證                   | 備註                                |
| ---------------------------- | --------------------- | --------------------------------- |
| gpt_academic                 | GPL-3.0               | 發生修改，修改請參見原gpt_academic檔案的头部區域    |
| aiohttp                      | Apache-2.0            |                                   |
| alertifyJS                   | GPL-3.0               |                                   |
| argon2-cffi                  | MIT License           |                                   |
| beautifulsoup4               | MIT License           |                                   |
| Bootstrap Icons              | MIT License           |                                   |
| colorama                     | BSD License           |                                   |
| cryptography                 | Apache-2.0            |                                   |
| fastapi                      | MIT License           |                                   |
| gradio                       | Apache-2.0            |                                   |
| gradio_modal                 | Apache-2.0            |                                   |
| latex2mathml                 | MIT License           |                                   |
| Markdown                     | BSD-3-Clause          |                                   |
| MathJax                      | Apache-2.0            |                                   |
| Mermaid                      | MIT License           |                                   |
| pandas                       | BSD-3-Clause          |                                   |
| PDF.js                       | Apache-2.0            |                                   |
| pydantic                     | MIT License           |                                   |
| pymdown-extensions           | MIT License           |                                   |
| PyMuPDF                      | GNU AFFERO GPL 3.0    |                                   |
| python_docx                  | MIT License           |                                   |
| PyYAML                       | MIT License           |                                   |
| rarfile                      | ISC License           |                                   |
| Requests                     | Apache-2.0            |                                   |
| rich                         | MIT License           |                                   |
| rjsmin                       | Apache-2.0            |                                   |
| tiktoken                     | MIT License           |                                   |
| uvicorn                      | BSD-3-Clause          |                                   |
| Vue.js                       | MIT license           |                                   |
| websockets                   | BSD-3-Clause          |                                   |
| zhipuai                      | unknown               | https://pypi.org/project/zhipuai/ |

**gpt_academic (3.83) 的使用策略：**

- 對 gpt_academic 原始碼的更改均位於每個檔案的開頭

- 訪問 AI：多執行緒和單執行緒對於多個 AI 的訪問，以及其中發生的網路處理、token 限制、和訪問 AI 所需的 API 及其所需文字內容的整合。

- 網頁服務（基於 gradio）。包含但不限於登入、多用戶管理、用戶界面、cookie 管理、插件選擇和參數修改、markdown 解析、捕捉錯誤後網頁呈現、前後端通訊、檔案上傳和下載以及 Scholar Navis 用到的 HTML 的連結和跳轉。

- 檔案管理：gpt_academic 所屬檔案/資料夾的處理和使用、PDF 全文獲取

- 除錯：控制台輸出彩色內容。

- 繪製思維導圖 @Menghuan1918

- 為了保證兼容性，參考了對於多執行緒中止的處理邏輯

- 模組熱加載

**Scholar Navis 獨立於 gpt_academic （3.83） 的功能：**

- 支援最新版的 gradio 和特性

- 檔案管理：插件資料夾（scholar_navis）內部的檔案管理、總結庫自身的管理

- 配置檔案和版本管理

- Sqlite3 資料庫的通信和管理

- 使用與 gpt_academic 獨立的 markdown 轉 pdf 功能

- csv、yaml 檔案解析

- 適用於 gpt_academic 的 Scholar Navis 安裝器（含有安裝依賴庫的功能）

- Scholar Navis 插件的多語言（國際化）顯示與多語言翻譯工具（支援 po 和 mo 格式）

- 為一些需要訪問 LLM 或者是需要文獻資訊、網路請求的部分，設計了快取機制，減少因為請求而產生的額外耗時

- 獲取論文的元數據、第一頁內容、摘要、doi 號和標題（其中通過 LLM 獲取的部分是通過 gpt_academic 進行的）

- 文章潤色處理邏輯及其 LLM 請求邏輯，markdown 轉 word（仍在測試）

- 將上傳的 pdf 作為總結庫進行管理和關鍵字設定

- 基於關鍵字的批次文章總結分析和 LLM 請求邏輯

- 與 AI 交流的邏輯，包含擬定課題、尋找文章來源、直接交流的處理邏輯和 LLM 請求邏輯

- 精細分析文章的處理邏輯和 LLM 請求邏輯、以及總結庫文章包含列表（HTML）設計

- PubMed OA 文章的多執行緒下載

- 用戶登入、註冊、資訊的保存與記錄（敏感盡可能進行了加密）。支援匿名使用（敏感資訊也在本地進行了加密）**（但是伺服器可以通過一些方法得到這些敏感內容）**

- 面向用戶的 API 自定義與模型自定義添加功能

- 上傳檔案和產生檔案的定時清理

- 網頁服務：在線 PDF 瀏覽（基於 pdf.js）

- API 服務：簡易通知

- 摘取有用的語句，並提供翻譯以便閱讀

- 行動端適配

- 支持推理模型，支持更新的模型

- 使用本地化JS技術提升執行效率

- 支援用戶自選顯示語言與大語言模型輸出語言

- 更完善的用戶登入註冊系統與優化界面
