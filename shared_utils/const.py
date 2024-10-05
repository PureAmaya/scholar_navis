# 该插件的根目录
import os

GPT_ACADEMIC_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
'''gpt_academic根目录'''
SCHOLAR_NAVIS_ROOT_PATH = os.path.join(GPT_ACADEMIC_ROOT_PATH,'crazy_functions','scholar_navis')
'''scholar navis 插件的根目录'''
WEB_SERVICES_ROOT_PATH = os.path.join(GPT_ACADEMIC_ROOT_PATH,'web_services')
'''一些WEB服务的根目录'''

if __name__ == "__main__":
    print('')
    print(GPT_ACADEMIC_ROOT_PATH)
    print(SCHOLAR_NAVIS_ROOT_PATH)