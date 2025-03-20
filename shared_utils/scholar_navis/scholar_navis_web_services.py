'''
Author: scholar_navis@PureAmaya
'''

import os
import json
import traceback
import aiofiles
import hashlib
from functools import wraps
from fastapi import Depends, Form
from fastapi.responses import FileResponse,PlainTextResponse,JSONResponse,HTMLResponse
from .other_tools import base64_decode
from bs4 import BeautifulSoup

from .const_and_singleton import WEB_SERVICES_ROOT_PATH,NOTIFICATION_ROOT_PATH,GPT_ACADEMIC_ROOT_PATH

maintenance_json : dict = {
    'state' :  False,
    'title':'',
    'message':'',
}

def enable_services(app,get_user):
    @app.get("/services/pdf_viewer/{path:path}")
    @check_login(Depends(get_user))
    async def pdf_viewer(path:str,user = Depends(get_user)):

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
    </style>
            '''
            
            head = f'<head><meta charset="UTF-8"><title>Scholar Navis Easy HTML</title>{css}</head>'
            head_iframe = f'<head>{js}</head>'
            body_iframe = f'<body>{base64_decode(base64)}</body>'
            
            # 去除所有的所有不需要的script标签
            soup = BeautifulSoup(body_iframe, 'html.parser')
            for script in soup.find_all('script'):script.decompose()
            body_iframe = str(soup)
            
            iframe = f'<iframe sandbox="allow-popups allow-scripts" srcdoc=\'{head_iframe + body_iframe}\'></iframe>'
            body = f'<body>{iframe}</body>'
            
            #html = f'<!DOCTYPE html><html>{head}{body}</html>'
            html = f'<!DOCTYPE html><html>{head}{head_iframe}{body_iframe}</html>' # 暂时不用iframe了得了
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
            
    @app.get("/ico/{path:path}") # 现在还没ico
    async def image(path:str):
        if path.startswith('svg/'):
            realpath = os.path.join(GPT_ACADEMIC_ROOT_PATH,'themes','svg',path[4:])
        else: realpath = os.path.join(GPT_ACADEMIC_ROOT_PATH,path)
        if os.path.isfile(realpath):
            return FileResponse(realpath,media_type='image/svg+xml')
        else: return PlainTextResponse('bad request',status_code=400)


def check_login(user):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not user: return PlainTextResponse('bad request. Not login.',status_code=401)
            else: return await func(*args, **kwargs)
        return wrapper
    return decorator