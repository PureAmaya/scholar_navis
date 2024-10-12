import os
import json
import aiofiles
import hashlib
from fastapi import FastAPI
from datetime import datetime
from fastapi.responses import FileResponse,PlainTextResponse,JSONResponse

from .const import WEB_SERVICES_ROOT_PATH,NOTIFICATION_ROOT_PATH

maintenance_json : dict = {
    'state' :  False,
    'start_time'  : '',
    'estimated_duration': '',
    'description': '',
    
}


def enable_services(app):
    
    
    @app.get("/services/pdf_viewer/{path:path}")
    async def pdf_viewer(path:str):
        
        if path.startswith('web/gpt_log'):realpath = path[4:]
        else:realpath = os.path.join(WEB_SERVICES_ROOT_PATH,'pdf.js',path)
        
        if os.path.exists(realpath):
            return FileResponse(realpath)
        else: return PlainTextResponse('bad request',status_code=400)
    
def enable_api(app):
    
    @app.get("/api/notification/maintenance")
    async def notification_maintenance():
        maintenance_json_fp = os.path.join(NOTIFICATION_ROOT_PATH ,'maintenance.json')
        try:
            async with aiofiles.open(maintenance_json_fp,'r',encoding='utf-8') as f:
                a = await f.read()
                json_ : dict= json.loads(a)
                json_.setdefault('hash',hashlib.md5(a.encode('utf-8')).hexdigest())
                return JSONResponse(json_)
        except:
            async with aiofiles.open(maintenance_json_fp,'w',encoding='utf-8') as f:
                await f.write(json.dumps(maintenance_json))
                return JSONResponse(maintenance_json)
