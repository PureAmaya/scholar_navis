# 该插件的根目录
import os


SCHOLAR_NAVIS_ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
'''该插件的根目录'''
GPT_ACADEMIC_ROOT_PATH = os.path.dirname(os.path.dirname(SCHOLAR_NAVIS_ROOT_PATH))
'''gpt_academic根目录'''
SCHOLAR_NAVIS_DIR_NAME = os.path.basename(SCHOLAR_NAVIS_ROOT_PATH)
'''该插件所在的那个文件夹（仅一个文件夹）'''