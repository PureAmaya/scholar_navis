Scholar Navis uses the AGPL-3.0 license.

**This translation is for reference only; the Simplified Chinese version shall prevail.**

---

**Third-party packages and projects:**

| Name                         | License               | Remarks                                                                                           |
| ---------------------------- | --------------------- | ------------------------------------------------------------------------------------------------- |
| gpt_academic                 | GPL-3.0               | Modifications occurred, please see the header area of the original gpt_academic file for details. |
| aiohttp                      | Apache-2.0            |                                                                                                   |
| alertifyJS                   | GPL-3.0               |                                                                                                   |
| argon2-cffi                  | MIT License           |                                                                                                   |
| beautifulsoup4               | MIT License           |                                                                                                   |
| Bootstrap Icons              | MIT License           |                                                                                                   |
| colorama                     | BSD License           |                                                                                                   |
| cryptography                 | Apache-2.0            |                                                                                                   |
| fastapi                      | MIT License           |                                                                                                   |
| gradio                       | Apache-2.0            |                                                                                                   |
| gradio_modal                 | Apache-2.0            |                                                                                                   |
| latex2mathml                 | MIT License           |                                                                                                   |
| Markdown                     | BSD-3-Clause          |                                                                                                   |
| MathJax                      | Apache-2.0            |                                                                                                   |
| Mermaid                      | MIT License           |                                                                                                   |
| pandas                       | BSD-3-Clause          |                                                                                                   |
| PDF.js                       | Apache-2.0            |                                                                                                   |
| pydantic                     | MIT License           |                                                                                                   |
| pymdown-extensions           | MIT License           |                                                                                                   |
| PyMuPDF                      | GNU AFFERO GPL 3.0    |                                                                                                   |
| python_docx                  | MIT License           |                                                                                                   |
| PyYAML                       | MIT License           |                                                                                                   |
| rarfile                      | ISC License           |                                                                                                   |
| Requests                     | Apache-2.0            |                                                                                                   |
| rich                         | MIT License           |                                                                                                   |
| rjsmin                       | Apache-2.0            |                                                                                                   |
| tiktoken                     | MIT License           |                                                                                                   |
| uvicorn                      | BSD-3-Clause          |                                                                                                   |
| Vue.js                       | MIT license           |                                   |
| websockets                   | BSD-3-Clause          |                                                                                                   |
| zhipuai                      | unknown               | https://pypi.org/project/zhipuai/                                                                 |

**Usage strategy for gpt_academic (3.83):**

- Changes to the gpt_academic source code are located at the beginning of each file.

- Access to AI: Multi-threading and single-threading for accessing multiple AIs, including network processing, token limits, and integration of APIs and required text content for accessing AIs.

- Web services (based on gradio). Includes but is not limited to login, multi-user management, user interface, cookie management, plugin selection and parameter modification, markdown parsing, error handling, front-end and back-end communication, file upload and download, and HTML links and jumps used by Scholar Navis.

- File management: Handling and usage of files/folders belonging to gpt_academic, full-text PDF retrieval.

- Debugging: Colored console output.

- Drawing mind maps @Menghuan1918

- To ensure compatibility, referenced the handling logic for multi-threading termination.

- Module hot reloading.

**Scholar Navis features independent of gpt_academic (3.83):**

- Supports the latest version of gradio and its features.

- File management: Internal file management of the plugin folder (scholar_navis), management of the summary library itself.

- Configuration file and version management.

- Sqlite3 database communication and management.

- Uses an independent markdown to PDF conversion function from gpt_academic.

- csv, yaml file parsing.

- Scholar Navis installer for gpt_academic (includes dependency library installation).

- Multi-language (internationalization) display for Scholar Navis plugins and multi-language translation tools (supports po and mo formats).

- Designed a caching mechanism for parts requiring access to LLM or literature information, network requests, to reduce additional time consumption caused by requests.

- Retrieval of paper metadata, first page content, abstract, doi, and title (the part obtained through LLM is done via gpt_academic).

- Article polishing logic and LLM request logic, markdown to word conversion (still in testing).

- Management of uploaded PDFs as a summary library and keyword setting.

- Batch article summary analysis based on keywords and LLM request logic.

- Logic for communicating with AI, including proposing topics, finding article sources, direct communication logic, and LLM request logic.

- Detailed article analysis logic and LLM request logic, and HTML design for summary library article lists.

- Multi-threaded download of PubMed OA articles.

- UserLogin login, registration, information saving and recording (sensitive information is encrypted as much as possible). Supports anonymous use (sensitive information is also encrypted locally) ** (however, the server can obtain this sensitive content through certain methods).**

- UserLogin-facing API customization and model customization features.

- Scheduled cleanup of uploaded and generated files.

- Web service: Online PDF viewing (based on pdf.js).

- API service: Simple notifications.

- Extraction of useful sentences and provision of translations for easy reading.

- Mobile device adaptation.

- Supports inference models, supports updated models.

- Accelerate performance with localized JS

- Support user-selected display languages and LLM output languages。

- Enhanced user login/registration system with improved UI.