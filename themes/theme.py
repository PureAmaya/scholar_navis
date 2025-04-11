'''
Original Author: gpt_academic@binary-husky

Modified by PureAmaya on 2025-04-11
- The JS events for the reset and stop buttons have been removed from the py file.
- Remove useless js_code_for_persistent_cookie_init.

Modified by PureAmaya on 2024-12-28
- Add i18n support
- Due to the removal of certain features/replacement by gradio components, the corresponding code has been removed.
'''


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

