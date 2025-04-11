# add by scholar_navis(@PureAmaya)

# 添加一个简单的加密emm

from hashlib import sha256
from base64 import urlsafe_b64encode
from cryptography.fernet import Fernet
from shared_utils.config_loader import get_conf
from multi_language import init_language

_ = init_language

# 从配置获取原始字符串（如 "my_secret"）
secret_str = get_conf('SECRET').strip()

if not secret_str or secret_str == 'Please change it to your own strongest secret key':
    raise ValueError(_("请先在配置文件中设置SECRET_KEY！"))
if len(secret_str) < 16:
    raise ValueError(_("SECRET_KEY长度必须大于等于16！"))

# 步骤 1: 将字符串转换为 SHA-256 的 32 字节哈希
secret_bytes = secret_str.encode("utf-8")
hashed_secret = sha256(secret_bytes).digest()  # 32 字节
# 步骤 2: 将 32 字节转换为 URL-safe Base64 字符串（长度 44）
fernet_key = urlsafe_b64encode(hashed_secret).decode("utf-8")

# 步骤 3: 初始化 Fernet
cipher = Fernet(fernet_key)  # 正确！

def encrypt(text:str)->str:
    """
    加密函数
    """
    return cipher.encrypt(text.encode('utf-8')).decode('utf-8')

def decrypt(text:str)->str:
    """
    解密函数
    """
    return cipher.decrypt(text).decode('utf-8')

if __name__ == '__main__':
    print(secret_str)
    print(fernet_key)
    a = encrypt('hello')
    b=  decrypt(a)
    print(a)
    print(b)
    