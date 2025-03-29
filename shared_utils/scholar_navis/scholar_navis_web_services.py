'''
Author: scholar_navis@PureAmaya
'''

import os
import json
import traceback
from typing import Literal
import aiofiles
import hashlib
from functools import wraps
from fastapi import Depends, Form
from fastapi.responses import FileResponse,PlainTextResponse,JSONResponse,HTMLResponse
from .other_tools import base64_decode
from bs4 import BeautifulSoup
from shared_utils.scholar_navis.multi_lang import _

from .const_and_singleton import WEB_SERVICES_ROOT_PATH,NOTIFICATION_ROOT_PATH,GPT_ACADEMIC_ROOT_PATH,VERSION

maintenance_json : dict = {
    'state' :  False,
    'title':'',
    'message':'',
}

def enable_services(app,get_user):
    @app.get("/services/pdf_viewer/{path:path}")
    @check_login(Depends(get_user))
    async def pdf_viewer(path:str):

        if path.startswith('web/gpt_log'):realpath = path[4:]
        elif path.startswith('web/tmp'):realpath = path[4:]
        else:realpath = os.path.join(WEB_SERVICES_ROOT_PATH,'pdf.js',path)
        #else: return PlainTextResponse('bad request. Not support this path.',status_code=400)
    
        
        if os.path.isfile(realpath):
            return FileResponse(realpath)
        else: return PlainTextResponse('bad request. No file found.',status_code=400)
    
    @app.post("/services/easy_html")
    @check_login(Depends(get_user))
    async def easy_html(base64: str = Form()):
        try:
            js ='<script src="https://fastly.jsdelivr.net/npm/mermaid@11.3.0/dist/mermaid.min.js"></script>' 
            # 现在只有mermiad那边用到JS了，就单独给他加一个好了
            
            css = '''
            <style>
        html, body {
            margin: 0; /* 去掉外边距 */
            padding: 0; /* 去掉内边距 */
            height: 100%; /* 设置高度为100% */
        }
        iframe {
            width: 100%; /* 设置宽度为100% */
            height: 100%; /* 设置高度为100% */
            border: none; /* 移除边框 */
            display: block; /* 避免有底部间隙 */
        }

        /* 基础样式 */
        .container {
            max-width: 1200px;       /* 控制最大内容宽度 */
            width: 90%;              /* 默认占视口90%（留出左右边距） */
            margin: 0 auto;          /* 水平居中 */
            padding: 20px 40px;      /* 内边距保护内容 */
            box-sizing: border-box;  /* 防止 padding 影响总宽度 */

            /* 可选装饰样式 */
            background: #fff;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        /* 平板适配 */
        @media (max-width: 1024px) {
            .container {
            width: 94%;           /* 增大宽度缩小边距 */
            padding: 20px 30px;   /* 减少侧边内边距 */
            }
        }

        /* 手机端适配 */
        @media (max-width: 768px) {
            .container {
            width: 100%;          /* 占满屏幕宽度 */
            padding: 15px 20px;   /* 最小安全内边距 */
            margin: 0;            /* 移除自动边距 */
            border-radius: 0;     /* 移除圆角（如有） */
            }
        }
        </style>
        '''
            
            head = f'<head><meta charset="UTF-8"><title>Scholar Navis Easy HTML</title>{css}</head>'
            head_iframe = f'<head>{js}</head>'
            body = f'<body><main class="container">{base64_decode(base64)}</main></body>'
            
            # 去除所有的所有不需要的script标签
            soup = BeautifulSoup(body, 'html.parser')
            for script in soup.find_all('script'):script.decompose()
            body = str(soup)

            
            #html = f'<!DOCTYPE html><html>{head}{body}</html>'
            html = f'<!DOCTYPE html><html>{head}{head_iframe}{body}</html>' # 暂时不用iframe了得了
            return HTMLResponse(html)
        except Exception as e: 
            traceback.print_exc()
            return PlainTextResponse(f'invaild request parameter.\n\n{str(e)}',status_code=400)
    
    
def enable_api(app,get_user):
    
    @app.get("/api/notification/msg")
    @check_login(Depends(get_user))
    async def notification_maintenance():
        maintenance_json_fp = os.path.join(NOTIFICATION_ROOT_PATH ,'msg.json')
        try:
            async with aiofiles.open(maintenance_json_fp,'r',encoding='utf-8') as f:
                a = await f.read()
                json_ : dict= json.loads(a)
                # 检查是否有需要的键
                for key in maintenance_json.keys():
                    if not key in json_.keys():
                        raise Exception(f'invaild json format. No key {key} found.')
                json_.setdefault('hash',hashlib.md5(a.encode('utf-8')).hexdigest())
                return JSONResponse(json_)
        except:
            traceback.print_exc()
            os.makedirs(NOTIFICATION_ROOT_PATH,exist_ok=True)
            async with aiofiles.open(maintenance_json_fp,'w',encoding='utf-8') as f:
                await f.write(json.dumps(maintenance_json))
                return JSONResponse(maintenance_json)
            
    @app.get("/favicon.ico")
    async def ico(size:Literal['192','512'] = None):
        assert size in ['192','512'] or not size, 'invaild png_size'

        if not size:
            realpath = os.path.join(GPT_ACADEMIC_ROOT_PATH,'themes','svg','logo.svg')
            media_type='image/svg+xml'
        if size:
            realpath = os.path.join(GPT_ACADEMIC_ROOT_PATH,'themes','svg','logo_png',f'logo_{size}x{size}.png')
            media_type='image/png'

        try:
            return FileResponse(realpath,media_type=media_type)
        except: 
            return PlainTextResponse('bad request',status_code=404)

    @app.get("/manifest.json")
    async def manifest():
        _json = {
            "name": "Scholar Navis",               # 应用名称（必填）
            "short_name": "Scholar Navis",            # 短名称（主屏幕显示）
            "description": _("一款基于 gpt_academic 的流水线式领域进展分析工具。允许用户从大量文章中摘取有用的信息（例如研究进展，缺口，符合用户需求的句子，并且支持用母语显示"),  # 应用描述
            "version": VERSION,             # 版本号（自定义格式）
            "start_url": "/",               # 启动页面（必填）
            "display": "standalone",        # 独立窗口模式（必填）
            "icons": [
                {
                "src": "/favicon.ico?size=192",
                "sizes": "192x192",
                "type": "image/png"
                },
                {
                "src": "/favicon.ico?size=512",
                "sizes": "512x512",
                "type": "image/png"
                },
                {
                "src": "/favicon.ico",
                "sizes": "any",
                "type": "image/svg+xml"
                }
            ]
            }
        return JSONResponse(_json)



def check_login(user):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not user: return PlainTextResponse('bad request. Not login.',status_code=401)
            else: return await func(*args, **kwargs)
        return wrapper
    return decorator