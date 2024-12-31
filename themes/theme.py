import base64
import uuid
import json
import inspect
import json


"""
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
第 2 部分
cookie相关工具函数
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
"""
def assign_user_uuid(cookies):
    # 为每一位访问的用户赋予一个独一无二的uuid编码
    cookies.update({"uuid": uuid.uuid4()})
    return cookies


def to_cookie_str(d):
    # serialize the dictionary and encode it as a string
    serialized_dict = json.dumps(d)
    cookie_value = base64.b64encode(serialized_dict.encode('utf8')).decode("utf-8")
    return cookie_value


def from_cookie_str(c):
    # Decode the base64-encoded string and unserialize it into a dictionary
    serialized_dict = base64.b64decode(c.encode("utf-8"))
    serialized_dict.decode("utf-8")
    return json.loads(serialized_dict)


"""
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
第 3 部分
内嵌的javascript代码（这部分代码会逐渐移动到common.js中）
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
"""


js_code_for_persistent_cookie_init = """(web_cookie_cache, cookie) => {
    return [getCookie("web_cookie_cache"), cookie];
}
"""

# 详见 themes/common.js
js_code_reset = """
(a,b,c)=>{
    let stopButton = document.getElementById("elem_stop");
    stopButton.click();
    return reset_conversation(a,b);
}
"""


js_code_clear = """
(a,b)=>{
    return ["", ""];
}
"""


