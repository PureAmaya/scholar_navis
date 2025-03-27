'''
Original Author: gpt_academic@binary-husky & Menghuan1918

Modified by PureAmaya on 2025-03-21
- When viewing the original GPT output in mermaid format, switch to using the markdown-to-html conversion method.

Modified by PureAmaya on 2025-03-19
- Change to using the POST method to display the drawing content.

Modified by PureAmaya on 2025-02-27
- Adjusted the chatbot's output. 
- It can now engage in conversations about drawing content.
- Adjusted the regular expression, and now the graphics are displaying correctly.

Modified by PureAmaya on 2024-12-28
- Add localization support.
- Added multilingual drawing support
- Due to the upgrade to Gradio 5, the functionality for small image previews and viewing larger images has also been modified.
'''

import os
import re
from toolbox import CatchException, update_ui, report_exception, update_ui_lastest_msg
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from crazy_functions.plugin_template.plugin_class_template import (
    GptAcademicPluginTemplate,
)
from crazy_functions.plugin_template.plugin_class_template import ArgProperty
from gradio import HTML
from shared_utils.scholar_navis.other_tools import base64_encode,generate_base64_html_webpage
from shared_utils.scholar_navis.multi_lang import _
from shared_utils.advanced_markdown_format import md2html

# 以下是每类图表的PROMPT
SELECT_PROMPT = """
“{subject}”
=============
The above is a summary extracted from the article, which will be used to create charts.
Please choose a suitable type of chart: 
1 Flowchart 
2 Sequence Diagram 
3 Class Diagram 
4 Pie Chart 
5 Gantt Chart 
6 State Diagram 
7 Entity Relationship Diagram 
8 Quadrant Prompt Chart 
No explanation is needed, just output a single number without any punctuation.
"""
# 没有思维导图!!!测试发现模型始终会优先选择思维导图
# 流程图
PROMPT_1 = """
Please provide a logical relationship diagram centered around '{subject}', using Mermaid syntax. 
Note that the content should be enclosed in double quotes. 
Example of Mermaid syntax:
```mermaid
graph TD
    P("编程") --> L1("Python")
    P("编程") --> L2("C")
    P("编程") --> L3("C++")
    P("编程") --> L4("Javascipt")
    P("编程") --> L5("PHP")
```
"""
# 序列图
PROMPT_2 = """
Please provide a sequence diagram centered around '{subject}', using Mermaid syntax. 
Example of Mermaid syntax:
```mermaid
sequenceDiagram
    participant A as 用户
    participant B as 系统
    A->>B: 登录请求
    B->>A: 登录成功
    A->>B: 获取数据
    B->>A: 返回数据
```
"""
# 类图
PROMPT_3 = """
Please provide a class diagram centered around '{subject}', using Mermaid syntax. 
Example of Mermaid syntax: 
```mermaid
classDiagram
    Class01 <|-- AveryLongClass : Cool
    Class03 *-- Class04
    Class05 o-- Class06
    Class07 .. Class08
    Class09 --> C2 : Where am i?
    Class09 --* C3
    Class09 --|> Class07
    Class07 : equals()
    Class07 : Object[] elementData
    Class01 : size()
    Class01 : int chimp
    Class01 : int gorilla
    Class08 <--> C2: Cool label
```
"""
# 饼图
PROMPT_4 = """
Please provide a pie chart centered around '{subject}', using Mermaid syntax. 
Note that the content should be enclosed in double quotes. 
Example of Mermaid syntax:
```mermaid
pie title Pets adopted by volunteers
    "狗" : 386
    "猫" : 85
    "兔子" : 15
```
"""
# 甘特图
PROMPT_5 = """
Please provide a Gantt chart centered around '{subject}', using Mermaid syntax. 
Note that the content should be enclosed in double quotes. 
Example of Mermaid syntax:
```mermaid
gantt
    title "项目开发流程"
    dateFormat  YYYY-MM-DD
    section "设计"
    "需求分析" :done, des1, 2024-01-06,2024-01-08
    "原型设计" :active, des2, 2024-01-09, 3d
    "UI设计" : des3, after des2, 5d
    section "开发"
    "前端开发" :2024-01-20, 10d
    "后端开发" :2024-01-20, 10d
```
"""
# 状态图
PROMPT_6 = """
Please provide a Gantt chart centered around '{subject}', using Mermaid syntax. 
Note that the content should be enclosed in double quotes. Example of Mermaid syntax:
```mermaid
stateDiagram-v2
   [*] --> "Still"
    "Still" --> [*]
    "Still" --> "Moving"
    "Moving" --> "Still"
    "Moving" --> "Crash"
    "Crash" --> [*]
```
"""
# 实体关系图
PROMPT_7 = """
Please provide an entity relationship diagram centered around '{subject}', using Mermaid syntax. 
Example of Mermaid syntax:
```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER {
        string name
        string id
    }
    ORDER {
        string orderNumber
        date orderDate
        string customerID
    }
    LINE-ITEM {
        number quantity
        string productID
    }
```
"""
# 象限提示图
PROMPT_8 = """
Please provide a quadrant diagram centered around '{subject}', using Mermaid syntax.
Note that the content should be enclosed in double quotes. 
Example of Mermaid syntax:
```mermaid
graph LR
    A["Hard skill"] --> B("Programming")
    A["Hard skill"] --> C("Design")
    D["Soft skill"] --> E("Coordination")
    D["Soft skill"] --> F("Communication")
```
"""
# 思维导图
PROMPT_9 = """
{subject}
==========
Please provide a mind map for the above content, 
taking into full consideration the logic between them, using Mermaid syntax.
Note that the content should be enclosed in double quotes. 
Example of Mermaid syntax:
```mermaid
mindmap
  root((mindmap))
    ("Origins")
      ("Long history")
      ::icon(fa fa-book)
      ("Popularisation")
        ("British popular psychology author Tony Buzan")
        ::icon(fa fa-user)
    ("Research")
      ("On effectiveness<br/>and features")
      ::icon(fa fa-search)
      ("On Automatic creation")
      ::icon(fa fa-robot)
        ("Uses")
            ("Creative techniques")
            ::icon(fa fa-lightbulb-o)
            ("Strategic planning")
            ::icon(fa fa-flag)
            ("Argument mapping")
            ::icon(fa fa-comments)
    ("Tools")
      ("Pen and paper")
      ::icon(fa fa-pencil)
      ("Mermaid")
      ::icon(fa fa-code)
```
"""


def 解析历史输入(history, llm_kwargs, file_manifest, chatbot, plugin_kwargs):
    
    GPT_prefer_language = plugin_kwargs['gpt_prefer_lang']
    index = plugin_kwargs['index']
    
    ############################## <第 0 步，切割输入> ##################################
    # 借用PDF切割中的函数对文本进行切割
    TOKEN_LIMIT_PER_FRAGMENT = 2500
    txt = (
        str(history).encode("utf-8", "ignore").decode()
    )  # avoid reading non-utf8 chars
    from crazy_functions.pdf_fns.breakdown_txt import (
        breakdown_text_to_satisfy_token_limit,
    )

    txt = breakdown_text_to_satisfy_token_limit(
        txt=txt, limit=TOKEN_LIMIT_PER_FRAGMENT, llm_model=llm_kwargs["llm_model"]
    )
    ############################## <第 1 步，迭代地历遍整个文章，提取精炼信息> ##################################
    results = []
    MAX_WORD_TOTAL = 4096
    n_txt = len(txt)
    last_iteration_result = _("从以下文本中提取摘要")
    if n_txt >= 20:
        print(_("文章极长，不能达到预期效果"))
    for i in range(n_txt):
        NUM_OF_WORD = MAX_WORD_TOTAL // n_txt
        i_say = f"Read this section, recapitulate the content of this section with less than {NUM_OF_WORD} words in English: {txt[i]}"
        i_say_show_user = f"[{i+1}/{n_txt}] Read this section, recapitulate the content of this section with less than {NUM_OF_WORD} words: {txt[i][:200]} ...."
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
            i_say,
            i_say_show_user,  # i_say=真正给chatgpt的提问， i_say_show_user=给用户看的提问
            llm_kwargs,
            chatbot,
            history=[
                "The main content of the previous section is?",
                last_iteration_result,
            ],  # 迭代上一次的结果
            sys_prompt= f"Extracts the main content from the text section where it is located for graphing purposes, answer me with {GPT_prefer_language}.",  # 提示
        )
        results.append(gpt_say)
        last_iteration_result = gpt_say
    ############################## <第 2 步，根据整理的摘要选择图表类型> ##################################
    gpt_say = str(index)  # 将图表类型参数赋值为插件参数

    results_txt = "\n".join(results)  # 合并摘要
    if gpt_say not in [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
    ]:  # 如插件参数不正确则使用对话模型判断
        i_say_show_user = (
            _("接下来将判断适合的图表类型,如连续3次判断失败将会使用流程图进行绘制")
        )
        gpt_say = _("[Local Message] 收到。")  # 用户提示
        chatbot.append([i_say_show_user, gpt_say])
        yield from update_ui(chatbot=chatbot, history=[])  # 更新UI
        i_say = {SELECT_PROMPT.format(subject=results_txt)}
        i_say_show_user = _('请判断适合使用的流程图类型,其中数字对应关系为:1-流程图,2-序列图,3-类图,4-饼图,5-甘特图,6-状态图,7-实体关系图,8-象限提示图。由于不管提供文本是什么,模型大概率认为"思维导图"最合适,因此思维导图仅能通过参数调用.')
        for i in range(3):
            gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say,
                inputs_show_user=i_say_show_user,
                llm_kwargs=llm_kwargs,
                chatbot=chatbot,
                history=[],
                sys_prompt="",
            )
            if gpt_say in [
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
            ]:  # 判断返回是否正确
                break
        if gpt_say not in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            gpt_say = "1"
    ############################## <第 3 步，根据选择的图表类型绘制图表> ##################################
    if gpt_say == "1":
        i_say = PROMPT_1.format(subject=results_txt)
    elif gpt_say == "2":
        i_say = PROMPT_2.format(subject=results_txt)
    elif gpt_say == "3":
        i_say = PROMPT_3.format(subject=results_txt)
    elif gpt_say == "4":
        i_say = PROMPT_4.format(subject=results_txt)
    elif gpt_say == "5":
        i_say = PROMPT_5.format(subject=results_txt)
    elif gpt_say == "6":
        i_say = PROMPT_6.format(subject=results_txt)
    elif gpt_say == "7":
        i_say = PROMPT_7.replace("{subject}", results_txt)  # 由于实体关系图用到了{}符号
    elif gpt_say == "8":
        i_say = PROMPT_8.format(subject=results_txt)
    elif gpt_say == "9":
        i_say = PROMPT_9.format(subject=results_txt)
    i_say_show_user = _("请根据判断结果绘制相应的图表。如需绘制思维导图请使用参数调用,同时过大的图表可能需要复制到在线编辑器中进行渲染.")
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs= f'{i_say}\n And answer me with Markdown and {GPT_prefer_language}.',
        inputs_show_user=i_say_show_user,
        llm_kwargs=llm_kwargs,
        chatbot=chatbot,
        history=[],
        sys_prompt="",
    )

    # 在chatbot中添加预览图表，并支持跳转到大窗口查看
    # 这里有点乱，先这样吧
    pattern = r'mermaid(.*?)```'
    match = re.findall(pattern, gpt_say, re.DOTALL)[0]

    # 小图与大图跳转
    mermaid = '<pre class="mermaid">{}</pre>'.format(match)
    html_b64 =base64_encode(mermaid)
    chatbot.append([{'role':'user','content':_('请点击查看绘制结果')},
                    {'role':'assistant','content':generate_base64_html_webpage(html_b64,_("点击查看大图"))}])
    
    # 提示
    substitute_html = HTML(
        '''
        <p>{}</p>
        <details>
        <summary>{}</summary>
        {}
        </details>
            '''.format(_("上方为生成的图形"),_("如果生成失败，可以点击这里查看AI返回的内容并自行修复"),md2html(gpt_say))
        )
    chatbot.append([{'role':'user','content':substitute_html},
                    {'role':'assistant','content':_("此外，您还可以对于绘制的图形进行问答。")}])
    history.append(gpt_say)
    history.extend(results)
    yield from update_ui(chatbot=chatbot, history=history)


@CatchException
def 生成多种Mermaid图表(
    txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port
):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，用于灵活调整复杂功能的各种参数
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """

    # 基本信息：功能、贡献者
    chatbot.append(
        [
            _("函数插件功能？"),
            _("根据当前聊天历史或指定的路径文件(文件内容优先)绘制多种mermaid图表，将会由对话模型首先判断适合的图表类型，随后绘制图表。\
        \n您也可以使用插件参数指定绘制的图表类型,函数插件贡献者: Menghuan1918"),
        ]
    )
    yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面

    if os.path.exists(txt):  # 如输入区无内容则直接解析历史记录
        from crazy_functions.pdf_fns.parse_word import extract_text_from_files

        file_exist, final_result, page_one, file_manifest, excption = (
            extract_text_from_files(txt, chatbot, history)
        )
    else:
        file_exist = False
        excption = ""
        file_manifest = []

    if excption != "":
        if excption == "word":
            report_exception(
                chatbot,
                history,
                a=_("解析项目: {}").format(txt),
                b=_("找到了.doc文件，但是该文件格式不被支持，请先转化为.docx格式。"),
            )

        elif excption == "pdf":
            report_exception(
                chatbot,
                history,
                a=_("解析项目: {}").format(txt),
                b=_("导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade pymupdf```。"),
            )

        elif excption == "word_pip":
            report_exception(
                chatbot,
                history,
                a=_("解析项目: {}").format(txt),
                b=_("导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade python-docx pywin32```。"),
            )

        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面

    else:
        if not file_exist:
            history.append(txt)  # 如输入区不是文件则将输入区内容加入历史记录
            i_say_show_user = _("首先你从历史记录中提取摘要")
            gpt_say = _("[Local Message] 收到。")  # 用户提示
            chatbot.append([i_say_show_user, gpt_say])
            yield from update_ui(chatbot=chatbot, history=history)  # 更新UI
            yield from 解析历史输入(
                history, llm_kwargs, file_manifest, chatbot, plugin_kwargs
            )
        else:
            file_num = len(file_manifest)
            for i in range(file_num):  # 依次处理文件
                i_say_show_user = f"[{i+1}/{file_num}] {_('处理文件: ')} {file_manifest[i]}"
                gpt_say = _("[Local Message] 收到。")  # 用户提示
                chatbot.append([i_say_show_user, gpt_say])
                yield from update_ui(chatbot=chatbot, history=history)  # 更新UI
                history = []  # 如输入区内容为文件则清空历史记录
                history.append(final_result[i])
                yield from 解析历史输入(
                    history, llm_kwargs, file_manifest, chatbot, plugin_kwargs
                )

# 暂时无用，无需国际化
#  Temporarily useless, no need for internationalization
class Mermaid_Gen(GptAcademicPluginTemplate):
    def __init__(self):
        pass

    def define_arg_selection_menu(self):
        gui_definition = {
            "Type_of_Mermaid": ArgProperty(
                title="绘制的Mermaid图表类型",
                options=[
                    "由LLM决定",
                    "流程图",
                    "序列图",
                    "类图",
                    "饼图",
                    "甘特图",
                    "状态图",
                    "实体关系图",
                    "象限提示图",
                    "思维导图",
                ],
                default_value="由LLM决定",
                description="选择'由LLM决定'时将由对话模型判断适合的图表类型(不包括思维导图)，选择其他类型时将直接绘制指定的图表类型。",
                type="dropdown",
            ).model_dump_json(),
        }
        return gui_definition

    def execute(
        txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request
    ):
        options = [
            "由LLM决定",
            "流程图",
            "序列图",
            "类图",
            "饼图",
            "甘特图",
            "状态图",
            "实体关系图",
            "象限提示图",
            "思维导图",
        ]
        plugin_kwargs = options.index(plugin_kwargs['Type_of_Mermaid'])
        yield from 生成多种Mermaid图表(
            txt,
            llm_kwargs,
            plugin_kwargs,
            chatbot,
            history,
            system_prompt,
            user_request,
        )
