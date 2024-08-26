Scholar Navis 使用 GPL-3.0 license 许可证

**gpt_academic的版权、其所有的除Scholar Navis之外的插件、部分等仍然为原作者、原贡献者所有，即 Scholar Navis 仅对`crazy_functions\scholar_navis`中的源码声明版权，其他目录中源码的版权均归原作者所有**。

----------------------------

下面是使用或依赖的项目：

| 第三方库或工具                                                                                 | 许可证                                  | 使用策略                                            |
| --------------------------------------------------------------------------------------- | ------------------------------------ | ----------------------------------------------- |
| <a href="https://github.com/binary-husky/gpt_academic" target="_blank">GPT Academic</a> | GPL-3.0 license                      | 作为该工具的插件，无法独立运行。针对gpt_academic详细的修改内容和使用策略请见下文。 |
| <a href="https://pypi.org/project/PyPDF2/" target="_blank">PyPDF2</a>                   | BSD License                          | 使用库，pdf处理                                       |
| <a href="https://pypi.org/project/PyYAML" target="_blank">PyYAML</a>                    | MIT License                          | 使用库，yaml文件解析                                    |
| <a href="https://pypi.org/project/beautifulsoup4" target="_blank">beautifulsoup4</a>    | MIT License                          | 使用库，网络请求处理                                      |
| <a href="https://pypi.org/project/requests/" target="_blank">requests</a>               | Apache Software License (Apache-2.0) | 使用库，网络请求                                        |
| <a href="https://pypi.org/project/python-docx" target="_blank">python-docx</a>          | MIT License                          | 使用库，解析docx并获取文本内容，将makrdown转换为word（所所属功能仍在测试）   |
| <a href="https://pypi.org/project/markdown-pdf/" target="_blank">markdown-pdf</a>       | MIT License                          | 使用库，将markdown转换为pdf                             |
| <a href="https://github.com/marktext/marktext" target="_blank">MarkText</a>             | MIT License                          | 使用该软件将markdown转换为HTML，并对HTML进行了修改               |

**gpt_academic中产生修改的部分如下：**

- 原则上是尽可能减少对于 gpt_academic 的修改，以方便移植或使用其他的版本。

- 因为对 gpt_academic 的源码产生了修改（主要是使其能够调用 Scholar Navis ），受限于GPL-3.0的约束，需要将 gpt_academic 的源码一并发布，并且亦需注明修改内容。

- `crazy_functional.py`：约400行处添加了下面的内容。`setup.py`亦可以产生下述修改
  
  ```python
  ###### SCHOLAR NAVIS START ########
  from crazy_functions.scholar_navis.scripts.tools.gpt_academic_handler import registrator
  function_plugins = registrator(function_plugins)
  ##### SCHOLAR NAVIS END - UNINSTALL: DELETE THESE ######
  ```

> 这样修改是为了gpt_academic能够使用 Scholar Navis

- `config_private.py`：约118行处产生了以下修改内容。`setup.py`亦可以产生下述修改，或产生一个含有下述修改内容的config_private.py
  
  ```python
  # 原始内容：
  DEFAULT_FN_GROUPS = ['对话', '编程', '学术', '智能体']
  
  # 修改后的内容：
  DEFAULT_FN_GROUPS = ['Scholar Navis']
  
  # 有的时候修改后的内容可能会包含原始的内容，例如：
  DEFAULT_FN_GROUPS = ['Scholar Navis','对话', '编程', '学术', '智能体']
  ```

> 这样子修改是为了用户可以通过gpt_academic的web服务使用 Scholar Navis

**gpt_academic的使用策略**：

- 访问AI：多线程和单线程对于多个AI的访问，以及其中发生的网络处理、token限制、和访问AI所需的API及其所需文本内容的整合。

- web服务（基于gradio）。包含但不限于登录、多用户管理、用户界面、cookie管理、插件选择和参数修改、markdown解析、捕捉错误后网页呈现、前后端通讯、文件上传和下载以及 Scholar Navis 用到的HTML的链接和跳转。

- 文件管理：gpt_academic所属文件/文件夹的处理和使用、PDF全文获取

- 调试：控制台输出彩色内容。

- 绘制思维导图 @Menghuan1918

- 为了保证兼容性，参考了对于多线程中止的处理逻辑

**Scholar Navis 独立于 gpt_academic 的功能**：

- 文件管理：插件文件夹（scholar_navis）内部的文件管理、总结库自身的管理

- 配置文件和版本管理

- Sqlite3数据库的通信和管理

- 使用与 gpt_academic 独立的 markdown 转 pdf 功能

- csv、yaml文件解析

- 适用于 gpt_academic 的 Scholar Navis 安装器（含有安装依赖库的功能）

- 多语言（国际化）显示与多语言翻译工具（支持po和mo格式）

- 获取论文的元数据、第一页内容、摘要、doi号和标题（其中通过LLM获取的部分是通过 gpt_academic 进行的）

- 文章润色处理逻辑、LLM请求逻辑，markdown转word（仍在测试）

- 将上传的pdf作为总结库进行管理和关键词设定

- 基于关键词的批量文章总结分析和LLM请求逻辑

- 与AI交流的逻辑，包含拟定课题、寻找文章来源、直接交流的处理逻辑和LLM请求逻辑

- 精细分析文章的处理逻辑和LLM请求逻辑、以及总结库文章包含列表（HTML）设计

- PubMed OA 文章的多线程下载
