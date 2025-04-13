'''
Original Author: gpt_academic@binary-husky

Modified by PureAmaya on 2025-04-13
- Remove unused imports.
- Only resources and scripts from the same origin are allowed to load.
- Add user language acquisition feature.
- Adjust API and gradio routing.
- Compatible with the new version of multilingual function.
- Cancel specified font.
- Added redirects for multilingual/monolingual/authorization requirements.

Modified by PureAmaya on 2025-03-19
- Provide authentication for some APIs.

Modified by PureAmaya on 2025-02-28
- Add middleware for font acquisition.
- Close Login Interface Queue.
- Allow users to retrieve shared data via HTTP.
- To obtain font settings routing.

Modified by PureAmaya on 2024-12-28
- Add i18n support
- Add security policy
- Modify authentication
- Add login panel
'''
import os
import fastapi
from multi_language import init_language,LANGUAGE_DISPLAY,MULTILINGUAL
from dependencies.i18n import SUPPORT_DISPLAY_LANGUAGE
from fastapi import Depends, Request
from fastapi.responses import FileResponse, RedirectResponse,JSONResponse,PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
from urllib.parse import unquote
import gradio as gr
from toolbox import FriendlyException
from shared_utils.config_loader import get_conf
from shared_utils.scholar_navis.const_and_singleton import font_path

# Scholar Navis大幅度修改了这里

PATH_PRIVATE_UPLOAD, PATH_LOGGING = get_conf('PATH_PRIVATE_UPLOAD', 'PATH_LOGGING')


_ = lambda  text:init_language(text,LANGUAGE_DISPLAY)

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # 设置安全相关的HTTP响应头
        response.headers["X-Content-Type-Options"] = "nosniff"  # 防止MIME类型嗅探
        response.headers["X-XSS-Protection"] = "1; mode=block"  # 启用XSS保护
        response.headers["X-Frame-Options"] = "SAMEORIGIN"  # 防止Clickjacking攻击
        response.headers["Referrer-Policy"] = "no-referrer"  # 控制Referer信息
        #response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self';"

        return response

# gr.Blocks
def start_app(apps:dict,CONCURRENT_COUNT, AUTHENTICATION, PORT, SSL_KEYFILE, SSL_CERTFILE):

    # --- --- configurate gradio app block --- ---

    for lang,app_block in apps.items():
        app_block.ssl_verify = False
        app_block.favicon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs/logo.png")
        app_block.blocked_paths = ['data',"config.py", "__pycache__", "config_private.py", "docker-compose.yml", "Dockerfile", f"{PATH_LOGGING}/admin"]
        app_block.dev_mode = False
        app_block.config = app_block.get_config_file()
        app_block.enable_queue = False
        app_block.queue(default_concurrency_limit=CONCURRENT_COUNT)
        app_block.validate_queue_settings()
        app_block.show_api = False
        app_block.config = app_block.get_config_file()
        max_threads = 40
        app_block.max_threads = max(
            app_block._queue.max_thread_count if app_block.enable_queue else 0, max_threads
        )
        app_block.is_colab = False
        app_block.is_kaggle = False
        app_block.is_sagemaker = False

    gradio_path = '/main'
    auth_path = '/auth'

    # --- --- configurate gradio app --- ---

    gradio_app = fastapi.FastAPI()
    gradio_app.add_middleware(SecurityMiddleware)

    # ##### 鉴权 #########
    from auth import check_user_token
    def get_user(request: Request):
        if AUTHENTICATION:
            token = request.cookies.get("user_token")
            if not token:return None
            token = unquote(token)
            accessible,user = check_user_token(token)
            if accessible: return user
            return None
        else:
            return 'default_user' # 啊好麻烦，直接匿名访问给个默认用户名得了

    # 读取语言设置
    def get_lang(request:Request) -> str:
        """
        获取用户语言。当启用多语言时可用。没启用的时候返回一个空值
        """
        if MULTILINGUAL:
            return request.cookies.get("lang",LANGUAGE_DISPLAY)
        else:return ''

    def validate_path_safety(path_or_url, user):
        sensitive_path = None
        path_or_url = os.path.relpath(path_or_url)
        allow = False

        if path_or_url.startswith(PATH_LOGGING):    # 日志文件（按用户划分）
            sensitive_path = PATH_LOGGING
        elif path_or_url.startswith(PATH_PRIVATE_UPLOAD):   # 用户的上传目录（按用户划分）
            sensitive_path = PATH_PRIVATE_UPLOAD
        elif path_or_url.startswith('tmp'):
            sensitive_path = 'tmp' # 用户自己产生的临时文件
        elif path_or_url.startswith('themes'):
            allow = True # 允许访问主题文件夹
        elif path_or_url.startswith('data'):
            sensitive_path = 'data' # 允许访问数据文件夹
        else:
            allow = False
        
        if sensitive_path:
            allowed_users = ['shared',user]  # 仅允许访问自身文件夹和共享文件夹
            for user_allowed in allowed_users:
                if f"{os.sep}".join(path_or_url.split(os.sep)[:2]) == os.path.join(sensitive_path, user_allowed):
                    allow = True
                    break
                else:
                    allow = False

        if allow and (not os.path.isfile(path_or_url)):
            raise FileNotFoundError(404)

        return allow

    @gradio_app.get("/")
    async def auth_redirect(user: dict = Depends(get_user),lang :str = Depends(get_lang)):
        if user:
            return RedirectResponse(url=f'{gradio_path}/{lang}')
        else: 
            return  RedirectResponse(url=auth_path)
    

    dependencies = []
    endpoint = None
    for route in list(gradio_app.router.routes):
        if route.path == "/file/{path:path}":
            gradio_app.router.routes.remove(route)
        if route.path == "/file={path_or_url:path}":
            dependencies = route.dependencies
            endpoint = route.endpoint
            gradio_app.router.routes.remove(route)
            
    #@gradio_app.get("/file/{path:path}", dependencies=dependencies)
    #@gradio_app.head("/file={path_or_url:path}", dependencies=dependencies)
    @gradio_app.get("/file={path_or_url:path}", dependencies=dependencies)
    async def file(path_or_url: str,user = Depends(get_user),lang = Depends(get_lang)):

        _ = lambda txt:init_language(txt,lang)

        try:
            if validate_path_safety(path_or_url, user):
                return FileResponse(path_or_url)
            else:
                raise FriendlyException(_("您没有访问该目录/文件的权限"))
        except FileNotFoundError:
            return PlainTextResponse(content='404 Not Found',status_code=404)
        except FriendlyException as e:
            return PlainTextResponse(content=str(e),status_code=403)
    
    
    # scholar navis的web api和服务
    from .scholar_navis.scholar_navis_web_services import enable_api,enable_services
    enable_api(gradio_app,get_user,get_lang);enable_services(gradio_app,get_user,get_lang)

    # --- --- favicon and block fastapi api reference routes --- ---

    @gradio_app.middleware("http")
    async def middleware(request: Request, call_next):
        if request.scope['path'] in ["/docs", "/redoc", "/openapi.json"]:
            return JSONResponse(status_code=404, content={"message": "Not Found"})
        response = await call_next(request)
        return response

    ssl_keyfile = None if SSL_KEYFILE == "" else SSL_KEYFILE
    ssl_certfile = None if SSL_CERTFILE == "" else SSL_CERTFILE
    server_name = "0.0.0.0"

    # 单语言版
    if len(apps) == 1:
        gr.mount_gradio_app(gradio_app, apps[LANGUAGE_DISPLAY], path=gradio_path, auth_dependency=get_user)

        # 误入多语言，直接重定向到默认语言
        @gradio_app.middleware("http")
        async def dispatch(request: Request, call_next):
            path = request.url.path

            # 检查是否是 /main/ 开头但不是 /main/{lang} 形式的路径
            if path.startswith(gradio_path) and path != gradio_path:
                lang = path.split("/")[2]
                if lang in SUPPORT_DISPLAY_LANGUAGE:  # 已配置的可用语言列表
                    return RedirectResponse(url=gradio_path)
            return await call_next(request)
    # 多语言版
    else:
        for lang,app in apps.items():
            gr.mount_gradio_app(gradio_app, app, path=f'{gradio_path}/{lang}', auth_dependency=get_user)
        # /main路由此时没啥用，重定向到指定语言界面
        @gradio_app.get(gradio_path)
        async def redirect_to_default_lang():
            return RedirectResponse(url="/")

    if AUTHENTICATION:
        from auth import enable_auth
        enable_auth(gradio_app,auth_path,get_lang)
    else:
        @gradio_app.get(auth_path)
        async def redirect_to_default_lang():
            return RedirectResponse(url="/")

    
    uvicorn.run(gradio_app, host=server_name, port=PORT,log_level="warning",ssl_keyfile=ssl_keyfile,ssl_certfile=ssl_certfile)