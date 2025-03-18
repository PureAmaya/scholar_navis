'''
Author: scholar_navis@PureAmaya
'''

from themes.common import get_common_html_javascript_code

from pygments.formatters import HtmlFormatter
from shared_utils.config_loader import get_conf

LANGUAGE_DISPLAY = get_conf("LANGUAGE_DISPLAY")

# 生成 Pygments CSS 样式
pygments_style = 'monokai'  # 可选风格：'default', 'monokai', 'friendly' 等
formatter = HtmlFormatter(style=pygments_style)
pygments_css = f"<style>{formatter.get_style_defs()}</style>"


local_js = get_common_html_javascript_code()

if LANGUAGE_DISPLAY == "zh-Hans":
    js = [
        '<script defer src="https://lf26-cdn-tos.bytecdntp.com/cdn/expire-1-M/AlertifyJS/1.13.1/alertify.min.js"></script>',
        '<script async src="https://lf9-cdn-tos.bytecdntp.com/cdn/expire-1-M/mermaid/8.14.0/mermaid.min.js"></script>',
        '<script async src="https://lf6-cdn-tos.bytecdntp.com/cdn/expire-1-M/mathjax/3.2.0/es5/tex-mml-chtml.min.js"></script>'
    ]
    css = [
        '<link rel="stylesheet" href="https://lf3-cdn-tos.bytecdntp.com/cdn/expire-1-M/AlertifyJS/1.13.1/css/alertify.min.css">',
        '<link rel="stylesheet" href="https://lf26-cdn-tos.bytecdntp.com/cdn/expire-1-M/AlertifyJS/1.13.1/css/themes/bootstrap.min.css">',
        '<link rel="stylesheet" href="/file=themes/scholar_navis/style.css">',
        pygments_css,
    ]
else:
    js = [
        '<script defer src="https://fastly.jsdelivr.net/npm/alertifyjs@1.14.0/build/alertify.min.js"></script>',
        '<script async src="https://fastly.jsdelivr.net/npm/mermaid@11.3.0/dist/mermaid.min.js"></script>',
        '<script async src="https://fastly.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.min.js"></script>'
    ]
    css = [
        '<link rel="stylesheet" href="https://fastly.jsdelivr.net/npm/alertifyjs@1.14.0/build/css/alertify.min.css">',
        '<link rel="stylesheet" href="https://fastly.jsdelivr.net/npm/alertifyjs@1.14.0/build/css/themes/bootstrap.min.css">',
        '<link rel="stylesheet" href="/file=themes/scholar_navis/style.css">',
        pygments_css,
    ]


def head():
    head_html = "\n".join(js) + "\n".join(css) + local_js
    return head_html
