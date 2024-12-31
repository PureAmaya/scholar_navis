from themes.common import get_common_html_javascript_code
from gradio_client import handle_file



local_js = get_common_html_javascript_code()

local_css = '''\
<style>


    /* 左上角的设置与文件上传 */
    
    #floating_panel_switch_btn {
        align-items: center; /* 垂直居中对齐 */
        width: 80%; /* 设置宽度为100% */
        max-width: 180px; /* 最大宽度，可根据需求调整 */
        margin-left: 0; /* 左对齐 */
        margin-right: auto; /* 处理右边距 */
        height: auto; /* 根据内容自动适配高度 */
        box-sizing: border-box; /* 包含padding和border在内 */
        font-size: 0.9em; /* 使用相对单位，字体大小可调整 */
        flex-grow: 1; /* 允许文本占据剩余空间 */
    }

    /* 禁止图像超出父元素边界 */
    #floating_panel_switch_btn img {
        max-width: 100%; /* 图像宽度不超过父元素宽度 */
        height: auto; /* 高度自动调整，保持比例 */
    }

    /* 暗黑模式切换 */
    #dark_mode_toggle {
        align-items: center;
        width: 80%; 
        max-width: 180px; 
        margin-right: 0;
        margin-left: auto; 
        height: auto; 
        box-sizing: border-box; 
        font-size: 0.9em; 
        flex-grow: 1; 

    }
    
    footer {
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .footer-content {
        text-align: center;
    }

    .footer-content p {
        margin: 0;
        display: flex;
        align-items: center; /* 确保段落内的元素垂直居中 */
        line-height: 1; /* 调整行高以适应SVG和文本的高度 */
    }

    .footer-content svg {
        vertical-align: middle; /* 使SVG图标和文本垂直居中对齐 */
        margin-right: 5px; /* 在SVG图标和文本之间添加一些间距 */
    }
</style>
'''

remote_js = ['<script src="https://fastly.jsdelivr.net/npm/alertifyjs@1.14.0/build/alertify.min.js"></script>',
            '<script src="https://fastly.jsdelivr.net/npm/mermaid@11.3.0/dist/mermaid.min.js"></script>']
remote_css = ['<link rel="stylesheet" href="https://fastly.jsdelivr.net/npm/alertifyjs@1.14.0/build/css/alertify.min.css">',
            '<link rel="stylesheet" href="https://fastly.jsdelivr.net/npm/alertifyjs@1.14.0/build/css/themes/bootstrap.min.css">']


def head():
    head_html =  '\n'.join(remote_js) + '\n'.join(remote_css) + local_css + local_js
    return head_html
    
