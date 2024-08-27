Scholar Navis is licensed under the GPL-3.0 license.

**The copyright of gpt_academic, all plugins and parts thereof except for Scholar Navis, remains with the original authors and contributors. This means that Scholar Navis only claims copyright over the source code in the `crazy_functions\scholar_navis` directory, while the copyright of the source code in other directories belongs to the original authors**.

----------------------------

Below is a list of projects used or relied upon:

| Third-party Library or Tool                                                             | License                              | Usage Strategy                                                                                                                              |
| --------------------------------------------------------------------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| <a href="https://github.com/binary-husky/gpt_academic" target="_blank">GPT Academic</a> | GPL-3.0 license                      | Used as a plugin for this tool; cannot run independently. Detailed modifications and usage strategies for gpt_academic are described below. |
| <a href="https://pypi.org/project/PyPDF2/" target="_blank">PyPDF2</a>                   | BSD License                          | Library used for PDF processing                                                                                                             |
| <a href="https://pypi.org/project/PyYAML" target="_blank">PyYAML</a>                    | MIT License                          | Library used for parsing YAML files                                                                                                         |
| <a href="https://pypi.org/project/beautifulsoup4" target="_blank">beautifulsoup4</a>    | MIT License                          | Library used for web request processing                                                                                                     |
| <a href="https://pypi.org/project/requests/" target="_blank">requests</a>               | Apache Software License (Apache-2.0) | Library used for web requests                                                                                                               |
| <a href="https://pypi.org/project/python-docx" target="_blank">python-docx</a>          | MIT License                          | Library used to parse docx files and extract text content, and to convert markdown to word (these features are still in testing)            |
| <a href="https://pypi.org/project/markdown-pdf/" target="_blank">markdown-pdf</a>       | MIT License                          | Library used to convert markdown to PDF                                                                                                     |
| <a href="https://github.com/marktext/marktext" target="_blank">MarkText</a>             | MIT License                          | Used the software to convert markdown to HTML, and modifications were made to the HTML                                                      |

**The modified parts in gpt_academic are as follows:**

- The principle is to make as few modifications to gpt_academic as possible to facilitate portability or the use of other versions.

- Since modifications have been made to the source code of gpt_academic (mainly to enable it to call Scholar Navis), due to the constraints of the GPL-3.0 license, the source code of gpt_academic must also be distributed, and the modifications must be noted as well.

- In `crazy_functional.py`, the following content was added around line 400. The `setup.py` can also cause the following modifications.
  
  ```python
  ###### SCHOLAR NAVIS START ########
  from crazy_functions.scholar_navis.scripts.tools.gpt_academic_handler import registrator
  function_plugins = registrator(function_plugins)
  ##### SCHOLAR NAVIS END - UNINSTALL: DELETE THESE ######
  ```

> These modifications are made to enable gpt_academic to utilize Scholar Navis.

- In `config_private.py`, the following modifications were made around line 118. The `setup.py` can also make the following changes, or it can generate a `config_private.py` containing the following modifications.
  
  ```python
  # original：
  DEFAULT_FN_GROUPS = ['对话', '编程', '学术', '智能体']
  
  # modified：
  DEFAULT_FN_GROUPS = ['Scholar Navis']
  
  # Sometimes the modified content may include the original content
  # for example:
  DEFAULT_FN_GROUPS = ['Scholar Navis','对话', '编程', '学术', '智能体']
  ```

> This modification is made so that users can access Scholar Navis through the gpt_academic web service.

- `multi_language.py`: The specific modifications are as follow:
  
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
  
  > These contents are added here to ensure that Scholar Navis can operate normally after the translation of gpt_academic.

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

**gpt_academic Usage Strategies**:

- Accessing AI: Multithreading and single-threading for accessing multiple AIs, including network processing, token limitations, and the integration of API required for accessing AI and the necessary text content.

- Web Service (based on gradio): This includes but is not limited to login, multi-user management, user interface, cookie management, plugin selection and parameter modification, markdown parsing, error capture with web page presentation, frontend and backend communication, file upload and download, and HTML links and redirections used by Scholar Navis.

- File Management: Handling and usage of files/folders belonging to gpt_academic, as well as PDF full-text retrieval.

- Debugging: Console output with colored content.

- Drawing Mind Maps @Menghuan1918

- To ensure compatibility, the logic for handling thread interruption was referenced.

**Scholar Navis Functions Independent of gpt_academic**:

- File Management: File management within the plugin folder (scholar_navis) and management of the summary library itself.

- Configuration file and version management

- Communication and Management of Sqlite3 Database

- Independent markdown to PDF conversion functionality from gpt_academic

- Parsing of csv, yaml files

- Installer for Scholar Navis compatible with gpt_academic (including functionality to install dependency libraries)

- Multilingual (internationalization) display and multilingual translation tools (supporting po and mo formats)

- Retrieval of metadata, first page content, abstract, DOI number, and title of papers (where part obtained through LLM is done via gpt_academic)

- Article polishing processing logic, LLM request logic, markdown to word (still in testing)

- Management of uploaded PDFs as a summary library and setting of keywords

- Batch article summary analysis and LLM request logic based on keywords

- Logic for interacting with AI, including topic formulation, finding article sources, direct communication processing logic, and LLM request logic

- Logic for in-depth analysis of articles and LLM request logic, as well as design of the summary library article list (HTML)

- Multithreaded download of PubMed OA article
