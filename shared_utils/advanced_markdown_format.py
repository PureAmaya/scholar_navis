'''
Original Author: gpt_academic@binary-husky

Modified by PureAmaya on 2025-02-26
- Remove the existing code and use pymarkdown and its extensions to achieve better Markdown-to-HTML conversion. 
- Additionally, provide some assistance for PDF conversion (using xhtml2pdf).
- Add CSS and font support
'''

import os
import markdown
from pygments.formatters import HtmlFormatter
from crazy_functions.scholar_navis.scripts.tools.article_library_ctrl import _forbidden_contain, _forbidden_startwith
from shared_utils.scholar_navis.const_and_singleton import font_path
import pymupdf
from shared_utils.scholar_navis.other_tools import generate_random_string

# 配置扩展
extensions = [
    'markdown.extensions.tables',
    'pymdownx.arithmatex',       # 数学公式支持
    'pymdownx.superfences',      # 增强型代码块
    'markdown.extensions.attr_list',
    'markdown.extensions.admonition',
    'pymdownx.highlight',        # 代码高亮
    'markdown.extensions.md_in_html'  # 允许混合HTML
]

# 生成 Pygments CSS 样式
pygments_style = 'monokai'  # 可选风格：'default', 'monokai', 'friendly' 等
formatter = HtmlFormatter(style=pygments_style)
pygments_css = f"<style>{formatter.get_style_defs()}</style>"

temp_dir = os.path.join('tmp','md2html')

css = '''
 /* 基础样式 */
body {
    line-height: 1.6;
    color: #333;
    margin: 0;
}

.hlcode {
    background: #2d2d2d;
    padding: 1em;
    border-radius: 5px;
    overflow-x: auto;
    margin: 1em 0;
}
table {
    border-collapse: collapse;
    margin: 1em 0;
}
th, td {
    border: 1px solid #ddd;
    padding: 8px;
}
th {
    background-color: #f2f2f2;
}
img {
    max-width: 100%;
    height: auto;
}
blockquote {
    border-left: 4px solid #ddd;
    padding-left: 1em;
    color: #666;
    margin: 1em 0;
}



/* 代码块保持原有样式 */
pre code {
background: transparent !important;
border: none !important;
padding: 0 !important;
white-space: pre;
}

/* 分页控制 */
@media print {
    pre, table, img {
        page-break-inside: avoid;
    }
    h1, h2, h3 {
        page-break-after: avoid;
    }
    }
'''


def md2html(markdown_text:str)->str:
    """ markdown转换成html，但是不完全（仅有body部分）
    """

        # 转换为HTML
    html_content = markdown.markdown(
        markdown_text,
        extensions=extensions,
        extension_configs={
            'pymdownx.arithmatex': {
                'generic': True  # 启用通用数学公式支持
            },
            'pymdownx.highlight': {
                'use_pygments': True,
                'css_class': 'hlcode',
                'pygments_style': pygments_style
            }
        }
    )

    return html_content

def md2html_full(text:str,title:str):
    body = md2html(text)

    # 生成完整HTML（移除外部CSS引用）
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        {pygments_css}
        <!-- MathJax配置 -->
        <script id="MathJax-script" async src="https://fastly.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.min.js"></script>
        <style>
        {css}
        </style>
    </head>
    <body>
    {body}
    </body>
    </html>
    """

    return full_html


def html2pdf(html_content:str,title:str,save_dir:str):
    """ markdown转换成pdf
    """

    # 转换为PDF
    fp = os.path.join(save_dir,f"{title}.pdf") 

    A4 = pymupdf.paper_rect("A4")  # size of a page
    WHERE = A4 + (36, 36, -36, -36)  # leave borders of 0.5 inches
    story =  pymupdf.Story(html=html_content,user_css=css)  # make the story
    writer = pymupdf.DocumentWriter(fp)  # make the writer
    pno = 0 # current page number
    more = 1  # will be set to 0 when done
    while more:  # loop until all story content is processed
        dev = writer.begin_page(A4)  # make a device to write on the page
        more, filled = story.place(WHERE)  # compute content positions on page
        story.draw(dev)
        writer.end_page()
        pno += 1  # increase page number
    writer.close()  # close output file





def md2pdf(text:str,title:str,save_dir:str):

    filename = title
    if any(filename.startswith(char) for char in _forbidden_startwith):
        filename = filename[1:]

    for char in _forbidden_contain:
        if char in filename:filename = filename.replace(char,'_')
    fp = os.path.join(save_dir,f"{filename}.pdf")
    
    HTML =  md2html_full(text,title)
    html2pdf(HTML,title,save_dir)
    return fp