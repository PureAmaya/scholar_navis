'''
Author: scholar_navis@PureAmaya
'''

import os
import re
import base64
import urllib
import random
import string
from urllib.parse import quote

def generate_random_string(length=16,chars=string.ascii_lowercase + string.digits,seed=None):
    # 随机选择字符并生成字符串
    if not isinstance(seed,str):seed = str(seed)
    
    if not seed:
        random.seed(seed)
    
    random_string = ''.join(random.choice(chars) for _ in range(length))
    return random_string


def generate_text_file_download(content:str,file_name:str,file_type:str='.txt',encoding='utf-8',permanent=False):
    if not file_type.startswith('.'): file_type = '.' + file_type
    
    if permanent:dir = os.path.join('data','shared','files')
    else:dir = os.path.join('tmp','shared','files')
    
    os.makedirs(dir,exist_ok=True)
    with open(os.path.join(dir,file_name+file_type),'w',encoding=encoding) as f:
        f.write(content)
    
    return generate_download_file(os.path.join(dir,file_name+file_type))


def generate_download_file(file_path:str,txt:str = None):
    """生成下载链接

    Args:
        file_path (str): 需要下载的文件路径（原始路径 or tmp缓存路径均可）。
        txt (str, optional): 超链接显示的文本. 默认为下载文件的basename.

    Returns:
        str: html的href，有a标签，如果是PDF则导入到内置的在线服务
    """
    
    # 为什么要把绝对路径转换为相对路径：下载连接更短，然后可以减少暴露，或许安全点？
    if os.path.isabs(file_path):
        file_path = os.path.relpath(file_path,os.getcwd())

    if not txt:txt = os.path.basename(file_path)

    if file_path.lower().endswith('.pdf'):
        return f'<a href="/services/pdf_viewer/web/viewer.html?file={file_path}" target="_blank">{txt}</a>'
    else:
        return f'<a href="/file={file_path}" target="_blank">{txt}</a>'

def base64_encode(original_string:str):
    # 编码：将字符串转换为字节，再进行Base64编码
    # 使用UTF-8编码
    encoded_bytes = base64.b64encode(original_string.strip().encode('utf-8'))
    encoded_string = encoded_bytes.decode('utf-8')  # 将字节转换回字符串
    encoded_string = urllib.parse.quote(encoded_string)
    return encoded_string

def base64_decode(encoded_string:str):
    # 解码：将Base64字符串解码为字节，再转换为原字符串
    decoded_bytes = base64.b64decode(encoded_string)
    decoded_string = decoded_bytes.decode('utf-8')  # 将字节转换为字符串
    return decoded_string

def fix_problematic_text(text:str):
    # 修复错误的Unicode转义（如&_x02010_）
    text = re.sub(r'&_x0([0-9a-fA-F]{4})_', lambda m: chr(int(m.group(1), 16)), text)
    text = text.replace(" ", "_").replace("&", "and").replace('/','_').replace('/','_').replace('=','_')
    text = re.sub(r'[^\w\-_.]', '_', text)
    return text