'''
Author: scholar_navis@PureAmaya
'''

from themes.common import get_common_html_javascript_code
from pygments.formatters import HtmlFormatter

# 生成 Pygments CSS 样式
pygments_style = 'monokai'  # 可选风格：'default', 'monokai', 'friendly' 等
formatter = HtmlFormatter(style=pygments_style)
pygments_css = f"<style>{formatter.get_style_defs()}</style>"

local_js = get_common_html_javascript_code()

js = [
    '<script defer src="/file=themes/js/alertify.min.js"></script>',
    '<script async src="/file=themes/js/mermaid.min.js"></script>',
    '<script async src="/file=themes/js/tex-mml-chtml.min.js"></script>'
]
css = [
    '<link rel="stylesheet" href="/file=themes/css/alertify.min.css">',
    '<link rel="stylesheet" href="/file=themes/css/bootstrap.min.css">',
    '<link rel="stylesheet" href="/file=themes/css/style.css">',
    pygments_css,
]


def head():
    head_html = "\n".join(js) + "\n".join(css) + local_js
    return head_html
