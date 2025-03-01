'''
Author: scholar_navis@PureAmaya
'''

from datetime import datetime,timedelta
import gradio as gr
from shared_utils.scholar_navis.const_and_singleton import footer
from themes.common import theme
from shared_utils.scholar_navis.multi_lang import _
from themes.scholar_navis.html_head_manager import head
from shared_utils.scholar_navis.sqlite import SQLiteDatabase
from shared_utils.scholar_navis.const_and_singleton import ph
from shared_utils.scholar_navis.user_account_manager import generate_user_token,get_user_token,check_password_match,check_password_strong,check_user_token,check_username_valid,check_user_exist

css = \
'''
<style>
    body {
        color: #333;
        margin: 0;
    }

    h1 {
        text-align: center;
        color: #3b82f6;
    }

    p {
        text-align: center;
        font-size: 1.1em;
    }
    
    .auth_field {
    max-width: 500px; /* 最大宽度为 600px */
    width: 100%; /* 在小屏幕上宽度占满 */
    margin: 0 auto; /* 居中对齐 */
    box-sizing: border-box; /* 使 padding 包含在元素宽度内 */
    }
</style>
'''

register_login_switch_js =\
'''
function toggleVisibilityByClass() {
    // 获取所有具有指定类名的元素
    var elements = {
        register: document.querySelectorAll('.register'),
        login: document.querySelectorAll('.login')
    };

    // 修正display
    elements.login.forEach(function(element) { if (element.style.display === '') {element.style.display = 'block';}});
    elements.register.forEach(function(element) { if (element.style.display === '') {element.style.display = 'none';}});

    // 定义一个函数用于切换元素的可见性
    function toggleVisibility(elements) {
        elements.forEach(function(element) {
            if (element) {
                // 检查当前元素的 display 属性
                element.style.display = (element.style.display === 'none' || element.style.display === '') ? 'block' : 'none';
            } else {
                console.error('元素不存在或未定义');
            }
        });
    }

    // 切换注册和登录元素的可见性
    toggleVisibility(elements.register);
    toggleVisibility(elements.login);
    
    // 清除元素
    return ['','','']
}
'''

setCookie_js =\
'''
{
    list_ = user.split(",");
    console.log(list_);
    name = list_[0];
    value = list_[1];
    days = list_[2] === "0" ? null : list_[2];
    let expires = "";
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));  // 计算过期时间
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/";  // 设置 Cookie
    
    
    // 登陆好了，跳转
    window.location.href = "/";
}
'''

welcome_1 = _('欢迎使用 Scholar Navis')
welcome_2 = _('管理员启动了身份验证。请登录或注册以继续')
welcome_3 = _('API信息在服务端加密; 不登录的情况下API加密储存在localStorage中，请勿泄露')
welcome_4 = _('如果对安全性不放心，请不要使用常用用户名与密码')
welcome = f'''
        <h1>{welcome_1}</h1>
        <p>{welcome_2}</p>
        <p>{welcome_3}</p>
        <p><strong>{welcome_4}</strong></p>
        <br>
'''

invaild_username = ('shared','default_user','admin','root','administrator','sysadmin','system','superuser',
                    'super','user','test','guest','anonymous','anonymous_user','default','demo',
                    'sql','mysql','postgres','mongodb','redis','SELECT', 'FROM', 'WHERE', 'INSERT',
                    'UPDATE', 'DELETE', 'JOIN', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN', 
                    'GROUP BY', 'ORDER BY', 'HAVING', 'DISTINCT', 'LIMIT', 'OFFSET', 'CREATE', 'DROP', 
                    'ALTER', 'TABLE', 'INDEX', 'VIEW', 'TRUNCATE', 'UNION', 'CASE', 'WHEN', 'THEN', 'ELSE')


def login(username_input,password_input,remember_me_input):
    username_input = username_input.strip().lower()
    password_input = password_input.strip()
    
    if username_input in invaild_username:raise gr.Error(_('用户名无效'),duration=5)
    
    if not username_input:raise gr.Error(_('用户名不能为空'),duration=5)
    if not password_input:raise gr.Error(_('密码不能为空'),duration=5)
    
    if not check_username_valid(username_input):raise gr.Error(_('用户名只能包含字母、数字和下划线'),duration=5)
    if not check_user_exist(username_input):raise gr.Error(_('当前用户不存在'),duration=5)
    if not check_password_strong(password_input):raise gr.Error(_('密码不符合要求。至少八位且有大小写字母和数字'),duration=5)
    if not check_password_match(password_input,username_input):raise gr.Error(_('密码错误'),duration=5)
    
    try:
        
        old_token = get_user_token(username_input)
        
        # 获取旧的过期时间
        if check_user_token(old_token)[0]: 
            token = old_token 
            # 如果原用户token没过期，读取服务器里的过期时间
            with SQLiteDatabase('user_account') as db:
                old_expiry_time  = db.easy_select(username_input,("token_expiry"))
                old_expiry_time =  datetime.strptime(old_expiry_time, '%Y-%m-%d %H:%M:%S')

        # 不匹配、过期都算不能用，这样的就好处理了
        else:
            token = generate_user_token(username_input) 
            old_expiry_time = datetime.now() # 设定一个最短时间，用于比较

        
        # 取最久时间作为过期时间
        if remember_me_input == 0:new_token_expiry_time = datetime.now() + timedelta(hours=3) #  姑且记住3小时
        else:new_token_expiry_time = datetime.now() + timedelta(days=remember_me_input)
        
        if new_token_expiry_time > old_expiry_time:expiry_time = new_token_expiry_time
        else:expiry_time = old_expiry_time
        token_expiry_string = expiry_time.strftime('%Y-%m-%d %H:%M:%S')

        with SQLiteDatabase('user_account') as db:
            db.update(username_input,('token','token_expiry'),(token,token_expiry_string))
    except:
        raise gr.Error(_('登录失败，请稍后再试'),duration=5)
        
    gr.Info(_('登陆成功'),duration=5)
    return f"user_token,{token},{remember_me_input}"

def register(username_input,password_input,password_confirm_input):
    username_input = username_input.strip().lower()
    password_input = password_input.strip()
    password_confirm_input = password_confirm_input.strip()
    
    if username_input in invaild_username:raise gr.Error(_('用户名无效'),duration=5)
    
    if not username_input:raise gr.Error(_('用户名不能为空'),duration=5)
    if not password_input:raise gr.Error(_('密码不能为空'),duration=5)
    if not password_confirm_input:raise gr.Error(_('请重复输入密码'),duration=5)
    
    if not check_username_valid(username_input):raise gr.Error(_('用户名只能包含字母、数字和下划线'),duration=5)
    if check_user_exist(username_input):raise gr.Error(_('当前用户已存在，请使用其他用户名'),duration=5)
    if not check_password_strong(password_input):raise gr.Error(_('密码不符合要求。至少八位且有大小写字母和数字'),duration=5)
    if password_input != password_confirm_input:raise gr.Error(_('两次输入的密码不一致'),duration=5)
    
    try:
        password_hash = ph.hash(password_input)
        token_expiry = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        token = generate_user_token(username_input)
        
        with SQLiteDatabase('user_account') as db:
            db.insert_ingore(username_input,
                            ('password','token','token_expiry'),
                            (password_hash,token,token_expiry))
    except:
        raise gr.Error(_('注册失败，请稍后再试'),duration=5)

    gr.Info(_('注册成功，请登录'),duration=5)


with gr.Blocks(title=_("Scholar Navis 登录授权页"),css=css,head=head(),theme=theme,analytics_enabled=False,delete_cache=(86400, 86400)) as authenticator:
    
    gr.HTML(welcome)
    
    with gr.Group(elem_classes='auth_field'):
        username = gr.Textbox(label=_("用户名"),placeholder=_("请输入用户名 (不区分大小写)"),max_lines=1)
        password = gr.Textbox(label=_("密码"),placeholder=_("至少八位，且有大小写字母与数字"),max_lines=1,type="password")
        remember_me = gr.Radio(choices=[(_('不自动登录'),0),(_('一周内自动登录'),7),(_('一个月内自动登录'),30),(_('总是自动登录'),365)],
                        value=7,label=_("自动登录"),elem_classes='login')
        confirm_password = gr.Textbox(label=_("确认密码"),placeholder=_("请再次输入密码"),max_lines=1,type="password",elem_classes='register',visible=False)
        login_btn = gr.Button(_('登录'),elem_classes='login',variant='primary')
        register_btn = gr.Button(_('注册'),elem_classes='register',visible=False,variant='primary')
        user = gr.Textbox(visible=False) # 给JS的 inputs 用不了 Browser，但是合理

    register_switch_btn = gr.Button(_('注册登录切换'),elem_classes='auth_field')
    gr.HTML(footer)

    register_switch_btn.click(None,None,outputs=[username,password,confirm_password],js=register_login_switch_js)

    login_btn.click(fn=login,inputs=[username,password,remember_me],outputs=[user]).success(None,inputs=[user],outputs=None,js=f'(user)=>{setCookie_js}')
    register_btn.click(fn=register,inputs=[username,password,confirm_password],outputs=None).success(None,None,outputs=[username,password,confirm_password],js=register_login_switch_js)

    #authenticator.load(None,None,None,js='()=>{ document.addEventListener("DOMContentLoaded", () => {dark_mode_init();});  }')
    authenticator.load(None,None,None,js='async function aaa() {dark_mode_init(); }')


demo = authenticator

if __name__ == "__main__":
    demo.launch()
