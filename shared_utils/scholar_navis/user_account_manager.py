'''
Author: scholar_navis@PureAmaya
'''

import re
import os
import gradio as gr
import string
from .sqlite import SQLiteDatabase
from .const_and_singleton import ph
from .other_tools import generate_random_string
from shared_utils.scholar_navis.multi_lang import _


def generate_user_token(username):
    return generate_random_string(length=64,chars=string.ascii_letters+string.digits,seed=username)

def check_username_valid(username_input):
    """检查用户名是否有效"""
    return bool(re.match(r'^[a-zA-Z0-9_]+$', username_input))


def check_password_strong(password_input:str):
    """简单的检查密码强度。

    Args:
        password_input (str): 用户输入的密码

    Returns:
        符合要求返回true; 反之为false
    """
    password_input = password_input.strip()
    if len(password_input) < 8:
        return False
    has_lowercase = re.search(r'[a-z]', password_input) is not None    # 检查小写字母
    has_uppercase = re.search(r'[A-Z]', password_input) is not None    # 检查大写字母
    has_digit = re.search(r'\d', password_input) is not None            # 检查数字

    return has_lowercase and has_uppercase and has_digit    

def check_password_match(password_input,username):
    with SQLiteDatabase('user_account') as db:
        password_hash = db.easy_select(username,'password')
    try:
        result =  ph.verify(password_hash, password_input)
        return result
    except Exception as e:
        return False

def change_password(current_password_input,new_password_input,new_password_confirm_input,username):
    new_password_input = new_password_input.strip()
    current_password_input = current_password_input.strip()
    new_password_confirm_input = new_password_confirm_input.strip()
    username = username.strip()
    
    if not current_password_input:raise gr.Error(_('当前密码不能为空'),duration=5)
    if not new_password_input:raise gr.Error(_('密码不能为空'),duration=5)
    if not new_password_confirm_input:raise gr.Error(_('请重复输入密码'),duration=5)
    
    if not check_password_match(current_password_input,username): raise gr.Error(_('当前密码错误'),duration=5)
    if not check_password_strong(new_password_input): raise gr.Error(_('密码不符合要求。至少八位且有大小写字母和数字'),duration=5)
    if new_password_input != new_password_confirm_input:raise gr.Error(_('两次输入的密码不一致'),duration=5)
    
    try:
        password_hash = ph.hash(new_password_input)
        token_expiry = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        token = generate_user_token(username) # 使用新的token，并将其设定为立刻过期
        
        with SQLiteDatabase('user_account') as db:
            db.update(username,
                            ('password','token','token_expiry'),
                            (password_hash,token,token_expiry))
    except:
        raise gr.Error(_('密码修改失败，请稍后再试'),duration=5)

def check_user_token(token:str):
    """检查用户token是否有效。

    Returns:
        (True=能用; False=过期或者token不存在,   username: token存在的话就给，不管token是否过期)
    """
    if not token:return False,None
    
    with SQLiteDatabase('user_account') as db:
        result = db.select('token',token,("token_expiry",'username'))
        if not result:return False,None
        token_expiry,username = result
    if not token_expiry: return False,None
        
    current_time = datetime.now()
    token_expiry =  datetime.strptime(token_expiry, '%Y-%m-%d %H:%M:%S')
    
    # 比较时间
    if token_expiry < current_time:
        return False,username
    else:
        return True,username

def get_user_token(username:str):
    """获取用户token
    """
    with SQLiteDatabase('user_account') as db:
        return db.easy_select(username,'token')


def check_user_exist(username_input):
    """检查用户是否存在

    Returns:
        用户存在返回true; 反之为false
    """
    with SQLiteDatabase('user_account') as db:
        result = db.easy_select(username_input,'username')
        if result:
            return True
        else:    
            return False
