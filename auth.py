import os.path
from datetime import datetime, timedelta
from typing import Literal

from fastapi import Depends
from pydantic import BaseModel
from fastapi.responses import  HTMLResponse
import aiofiles
from shared_utils.scholar_navis.sqlite import SQLiteDatabase
from multi_language import init_language
from shared_utils.scholar_navis.const_and_singleton import ph,GPT_ACADEMIC_ROOT_DIR
from shared_utils.scholar_navis.user_account_manager import generate_user_token,get_user_token,check_password_match,check_password_strong,check_user_token,check_username_valid,check_user_exist

invalid_username = ('shared', 'default_user', 'data', 'dependencies', 'docs', 'gpt_log', 'gradio_temp', 'notification',
                    'private_upload','request_llms','shared_utils','themes','web_services'
                    'admin','root','administrator','sysadmin','system','superuser',
                    'super','user','test','guest','anonymous','anonymous_user','default','demo',
                    'sql','mysql','postgres','mongodb','redis','SELECT', 'FROM', 'WHERE', 'INSERT',
                    'UPDATE', 'DELETE', 'JOIN', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN',
                    'GROUP BY', 'ORDER BY', 'HAVING', 'DISTINCT', 'LIMIT', 'OFFSET', 'CREATE', 'DROP',
                    'ALTER', 'TABLE', 'INDEX', 'VIEW', 'TRUNCATE', 'UNION', 'CASE', 'WHEN', 'THEN', 'ELSE')

invalid_username_beginnings = ('_', '.')

class UserLogin(BaseModel):
    username: str
    password: str
    remember_me_days: int = 0

class UserRegister(BaseModel):
    username: str
    password: str


class Notify(BaseModel):
    notifier_type:Literal['success','warning','error','message','notify']
    msg: str
    delay:int = 5
    position:Literal['top-right','top-center','top-left','bottom-right','bottom-center','bottom-left'] = 'top-right'
    console_error:str = None


def _universal_check_username(username_input,translator):
    """
    通用化的用户名检查
    :param username_input: 用户输入的用户名
    :return: 错误提示信息，如果没有错误，返回None
    """
    _ = translator

    if not username_input:
        return Notify(notifier_type='error',msg=_('用户名不能为空'), delay=5)

    elif username_input in invalid_username:
        return Notify(notifier_type='error',msg=_('用户名无效'), delay=5)

    elif username_input.startswith(invalid_username_beginnings):
        return Notify(notifier_type='error',msg=_('用户名不能以特殊字符开头'), delay=5)

    elif not check_username_valid(username_input):
        return Notify(notifier_type='error',msg=_('用户名只能包含字母、数字和下划线'), delay=5)
    else:
        return None

def _universal_check_password(password_input,translator):
    """
    通用化的密码检查
    :param password_input: 用户输入的密码
    :return: 错误提示信息，如果没有错误，返回None
    """
    _ = translator

    if not password_input:
        return Notify(notifier_type='error',msg=_('密码不能为空'), delay=5)
    elif not check_password_strong(password_input):
        return Notify(notifier_type='error',msg=_('密码不符合要求。至少八位且有大小写字母和数字，且不能无效字符'), delay=5)
    else:
        return None


def enable_auth(app,auth_path:str,get_lang):

    @app.get(auth_path)
    async def _auth_page():
        """
        鉴权页面
        """
        async with aiofiles.open(os.path.join(GPT_ACADEMIC_ROOT_DIR,'themes','html','auth.html'),
                                 mode='r',encoding='utf-8') as f:
            a = await f.read()
            return HTMLResponse(a)

    @app.post(f"{auth_path}/login")
    async def _login(user: UserLogin,lang = Depends(get_lang)):

        _ = lambda txt:init_language(txt,lang)

        username_input = user.username.strip().lower() # 不区分大小写
        password_input = user.password # 去除strip()
        remember_me_input = user.remember_me_days

        a = _universal_check_username(username_input,_)
        if a:
            return a
        elif not check_user_exist(username_input):
            return Notify(notifier_type='error',msg=_('当前用户不存在'), delay=5)


        b = _universal_check_password(password_input,_)
        if b:
            return b
        elif not check_password_match(password_input, username_input):
            return Notify(notifier_type='error',msg=_('密码错误'), delay=5)

        try:
            old_token = get_user_token(username_input)

            # 获取旧的过期时间
            if check_user_token(old_token)[0]:
                token = old_token
                # 如果原用户token没过期，读取服务器里的过期时间
                with SQLiteDatabase('user_account') as db:
                    old_expiry_time = db.easy_select(username_input, "token_expiry")
                    old_expiry_time = datetime.strptime(old_expiry_time, '%Y-%m-%d %H:%M:%S')

            # 不匹配、过期都算不能用，这样的就好处理了
            else:
                token = generate_user_token(username_input)
                old_expiry_time = datetime.now()  # 设定一个最短时间，用于比较

            # 取最久时间作为过期时间
            if remember_me_input == 0:
                new_token_expiry_time = datetime.now() + timedelta(hours=3)  # 姑且记住3小时
            else:
                new_token_expiry_time = datetime.now() + timedelta(days=remember_me_input)

            if new_token_expiry_time > old_expiry_time:
                expiry_time = new_token_expiry_time
            else:
                expiry_time = old_expiry_time
            token_expiry_string = expiry_time.strftime('%Y-%m-%d %H:%M:%S')

            with SQLiteDatabase('user_account') as db:
                db.update(username_input, ('token', 'token_expiry'), (token, token_expiry_string))
        except:
            return Notify(notifier_type='error', msg=_('登陆失败，请稍后再试'), delay=5)

        msg_dict = Notify(notifier_type='success',msg=_('登陆成功'), delay=5).model_dump()
        msg_dict.update({'token': token,'remember_me_days': remember_me_input})
        return msg_dict

    @app.post(f"{auth_path}/register")
    async def _register(user: UserRegister,lang=Depends(get_lang)):

        _ = lambda txt: init_language(txt, lang)

        username_input = user.username.strip().lower() # 不区分大小写
        password_input = user.password # 去除strip()

        a = _universal_check_username(username_input,_)
        if a:
            return a
        elif check_user_exist(username_input):
            return Notify(notifier_type='error',msg=_('当前用户已存在，请使用其他用户名'), delay=5)

        b = _universal_check_password(password_input,_)
        if b:
            return b
        elif password_input == username_input:
            return Notify(notifier_type='error',msg=_('密码不能与用户名相同'), delay=5)

        try:
            password_hash = ph.hash(password_input)
            token_expiry = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            token = generate_user_token(username_input)

            with SQLiteDatabase('user_account') as db:
                db.insert_ingore(username_input,
                                 ('password', 'token', 'token_expiry'),
                                 (password_hash, token, token_expiry))
        except Exception as e:
            return Notify(notifier_type='error', msg=_('注册失败，请稍后再试'), delay=5, console_error=str(e))

        return Notify(notifier_type='success',msg=_('注册成功'), delay=5)



