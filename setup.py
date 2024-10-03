import os
import sys
import shutil
import argparse
import subprocess
# 有的时候需要提前安装一个yaml
try:import yaml
except:subprocess.run(['pip', 'install', 'PyYAML'])
# 安装好之后再导入
from shared_utils.multi_lang import _,i18n
from shared_utils.const import GPT_ACADEMIC_ROOT_PATH, SCHOLAR_NAVIS_ROOT_PATH
from shared_utils.sn_config import VERSION,CONFIG,write_config, GPT_SUPPORT_LAMGUAGE

def _clear_console():
    if sys.platform == 'win32':os.system('cls')
    else:os.system('clear') 


def _check_input(txt:str,accept_char):
    while(True):
        print(txt)
        a = input().strip().lower()
        if a in accept_char:return a
        else:print('\n'); print(_('不合法输入，请重新输入'))

def _choose_language():
    
    
    # 选择 显示语言
    print('如果希望使用 简体中文 作为显示语言，请输入1')
    print('若希望使用 繁體中文 作為顯示語言，請輸入2.')
    print('If you wish to use English as the display language, please enter 3.')
    
    while(True): # 反正就仨）
        txt = input('\n').strip()
        if txt == '1':CONFIG['language_display'] = 'zh-Hans';break
        if txt == '2':CONFIG['language_display'] = 'zh-Hant';break
        elif txt == '3' :CONFIG['language_display'] = 'en-US';break
        else:print('不合法输入，请重新输入\n不合法輸入，請重新輸入\nInvalid input, please try again.')
    
    # 保存偏好
    write_config()
    # 更新语言
    i18n.update()
    
    _clear_console()
    
    # 选择 GPT偏好语言
    print('\n')
    for index,v in enumerate(GPT_SUPPORT_LAMGUAGE):
        print(_('如果希望 {lang} 为GPT的偏好语言，请输入 {k}').format(lang=v,k=index + 1))

    while(True):
        txt = input('\n').strip()
        try:
            txt_int = int(txt) - 1
            CONFIG['language_GPT_prefer'] = GPT_SUPPORT_LAMGUAGE[txt_int];break
        except:
            print(_('不合法输入，请重新输入'))
        
        
    # 保存偏好
    write_config()

def __check_path():
    
    install_vaild = True
    
    # 检查自己是不是在该有的目录下
    if not 'crazy_functions' in SCHOLAR_NAVIS_ROOT_PATH: # 安装的文件夹肯定有的
        print(_('没有安装在gpt_academic的crazy_functions文件夹下'))
        install_vaild = False
    
    
    if not install_vaild:
        input(_("按回车键退出..."))
        sys.exit(1)


def _configuration():
    
    _clear_console()
    
    def ync_parse(a,value):
        _clear_console()
        if a == 'y':return True
        elif a == 'n':return False
        else:return value
        
    bool_prompt = _('y(启用) / n(禁用) / 不输入(跳过修改)')
    bool_input = {'y','n',''}
    
    print(_('修改配置'))
    print('\n')
    
    print(_('启用临时文件自动删除: '))
    print(_('当前: ') + str(CONFIG['auto_clear_tmp']))
    a = _check_input(bool_prompt,bool_input)
    CONFIG['auto_clear_tmp'] = ync_parse(a,CONFIG['auto_clear_tmp'])
    
    print(_('启用总结库自动删除: '))
    print(_('当前: ') + str(CONFIG['auto_clear_summary_lib']))
    a = _check_input(bool_prompt,bool_input)
    CONFIG['auto_clear_summary_lib'] = ync_parse(a,CONFIG['auto_clear_summary_lib'])
    
    print(_('启用上传文件自动删除: '))
    print(_('当前: ') + str(CONFIG['auto_clear_private_upload']))
    a = _check_input(bool_prompt,bool_input)
    CONFIG['auto_clear_private_upload'] = ync_parse(a,CONFIG['auto_clear_private_upload'])
    
    print(_('启用简易翻译器（仅限于 Scholar Navis）: '))
    print(_('当前: ') + str(CONFIG['enable_simple_translator']))
    a = _check_input(bool_prompt,bool_input)
    CONFIG['enable_simple_translator'] = ync_parse(a,CONFIG['enable_simple_translator'])
    
    print(_('启用 PubMed OA 下载器: '))
    print(_('当前: ') + str(CONFIG['enable_pubmed_downloader']))
    a = _check_input(bool_prompt,bool_input)
    CONFIG['enable_pubmed_downloader'] = ync_parse(a,CONFIG['enable_pubmed_downloader'])
    
    print(_('启用 用户使用日志: '))
    print(_('当前: ') + str(CONFIG['enable_user_usage_log']))
    a = _check_input(bool_prompt,bool_input)
    CONFIG['enable_user_usage_log'] = ync_parse(a,CONFIG['enable_user_usage_log'])
    
    print(_('优先使用AI辅助功能获取文献doi和标题'))
    print(_('当前: ') + str(CONFIG['prioritize_use_AI_assistance']))
    a = _check_input(bool_prompt,bool_input)
    CONFIG['prioritize_use_AI_assistance'] = ync_parse(a,CONFIG['prioritize_use_AI_assistance'])
    
    write_config()

def _crazy_function_modifier():
    
    _clear_console()
    
    txt = f'''
    ###### SCHOLAR NAVIS START ########
    from crazy_functions.scholar_navis.scripts.tools.gpt_academic_handler import registrator
    function_plugins = registrator(function_plugins)
    ##### SCHOLAR NAVIS END - UNINSTALL: DELETE THESE #########
    '''
    
    crazy_functional_bak_fp = os.path.join(GPT_ACADEMIC_ROOT_PATH,'crazy_functional.py.bak')
    crazy_functional_fp = os.path.join(GPT_ACADEMIC_ROOT_PATH,'crazy_functional.py')

    if not os.path.exists(crazy_functional_bak_fp):shutil.copy(crazy_functional_fp,crazy_functional_bak_fp)
    
    with open(crazy_functional_fp,'r',encoding='utf-8') as f:
        cr = f.read()
        
    # 检查是否安装
    if 'scripts.tools.gpt_academic_handler' in cr:
        print(_('已经在 crazy_functional 中注册过本工具，此过程跳过'))
        return 
        
    # 找到特定行的位置在哪，之后在这段文本的前后插入
    insert_position = cr.find('# -=--=-')   
    print(insert_position) 
    if insert_position == -1 :
        input(_('无法在 crazy_functional 中注册本工具（可以尝试手动安装）。安装程序已终止，按回车键退出...'))
        sys.exit(1)
    else:
        cr = f'{cr[:insert_position]}\n\n{txt}\n\n{cr[insert_position:]}'
        with open(crazy_functional_fp,'w',encoding='utf-8') as f:f.write(cr)
        print(_('crazy_functional 注册成功'))
        
def _config_pri_modifier():
    
    
    config_pri_bak_fp = os.path.join(GPT_ACADEMIC_ROOT_PATH,'config_private.py.bak')
    config_pri_fp = os.path.join(GPT_ACADEMIC_ROOT_PATH,'config_private.py')
    config_fp = os.path.join(GPT_ACADEMIC_ROOT_PATH,'config.py')

    # 如果没有私有的配置文件，弄一份
    if not os.path.exists(config_pri_fp):shutil.copy(config_fp, config_pri_fp)
    # 备份一次pri
    if not os.path.exists(config_pri_bak_fp):shutil.copy(config_pri_fp, config_pri_bak_fp)
    
    # 最终要写入的内容
    config_content = ''
    
    # 对该有的内容进行修改（不含网络代理，那里我没办法了）
    with open(config_pri_fp,'r',encoding='utf-8') as f:
        config_read = f.read()
        
    # 把这个参数之前的内容先记录一下（要改的参数不在这里）
    num = config_read.find('DEFAULT_FN_GROUPS')
    config_content =  config_read[:num]
    
    # 获取DEFAULT_FN_GROUPS这一行
    first_line = config_read[num:].find('\n') # 把第一行去掉
    DEFAULT_FN_GROUPS_line_str = config_read[num:][:first_line]
    #DEFAULT_FN_GROUP没有Scholar Navis的话，就给他加上
    if not 'Scholar Navis' in DEFAULT_FN_GROUPS_line_str:
        DEFAULT_FN_GROUPS_line_str = DEFAULT_FN_GROUPS_line_str.replace('[',"['Scholar Navis',",1)
        # 防止出现 , 后没有内容的情况
        print(_('config_private 注册工具组成功'))
    # 有了的话就保留现状
    else: print(_('config_private 中已注册工具组，此过程跳过'))
    
    # 把 DEFAULT_FN_GROUPS这一行 放进去
    config_content = f'{config_content}{DEFAULT_FN_GROUPS_line_str}'

    # 把后面的内容补上（后面这里就没有DEFAULT_FN_GROUPS这一行了）
    config_content = f'{config_content}{config_read[num:][first_line:]}'
    
    # 对修改进行保留
    with open(config_pri_fp,'w',encoding='utf-8') as f:
        config_read = f.write(config_content) 
        
def _install_requirement():
    
    _clear_console()
    
        # 安装需要的包
    requirements_fp = os.path.join(GPT_ACADEMIC_ROOT_PATH,'requirements.txt')
    if not os.path.exists(requirements_fp):
        input(_('不存在 requirements.txt 包安装终止。按回车键退出...'))
        sys.exit(1)
    else:
        print('')
        while(True):
            print(_('该工具所用的网络位于中国大陆吗？ y(默认)/n/c'))
            country = input(_('y=是 n=否 c=取消安装依赖（跳过）')).strip().lower()
            
            print('\n')
            if  country  == 'y' or country  =='n' or country == 'c' or country == '': break
            else:print('\n'); print(_('不合法输入，请重新输入'))
        
        print(_('开始安装依赖包...'))
        try:
            if country == 'n':
                subprocess.run(['pip', 'install', '-r',f'{os.path.join(GPT_ACADEMIC_ROOT_PATH,"requirements.txt")}','--upgrade'])
                print(_('requirements.txt 安装成功'))
            elif country == 'y' or country == '':
                subprocess.run(['pip', 'install', '-r',f'{os.path.join(GPT_ACADEMIC_ROOT_PATH,"requirements.txt")}','--upgrade','-i','https://pypi.mirrors.ustc.edu.cn/simple/'])
                print(_('requirements.txt 安装成功'))
            elif country == 'c':
                # 取消安装
                print(_('已经跳过依赖安装'))
            print('\n')
        except Exception as e:
            input(_('requirements.txt 安装失败（{}）。按回车键退出...').format(str(e)))
            sys.exit(1)
    

def __config_prompt():
    print(_('Scholar Navis 安装成功。'))
    print(_('进一步配置，请在 conig_private.py 中进行调整，内含各个参数的详细说明'))
    print(_('此外也请阅读 readme.md ，了解本程序、gpt_academic和其他事宜！'))
    
    print('\n')
    input(_('按回车键退出...'))
    sys.exit()

def install():
    
    
    _configuration()
    
    
    # 安装预先数据 现在暂时不需要了
    #__install_def_data()
    
    #  crazy中安装本工具 
    _crazy_function_modifier()
        
    # 配置中加上去
    _config_pri_modifier()
    
    input(_('按下回车键以继续...'))
    
    # 安装需要的包
    _install_requirement()
    
    #提示一下应该调整的配置
    __config_prompt()


def main():
    
    _clear_console()
    
    print('\n')
    print(_('欢迎使用Scholar Navis'))
    print(f'ver. {VERSION}\n')
    
    # 路经检查
    __check_path()
    
    # 选择语言
    _choose_language()
    
    while(True):
        print(_('要安装 Scholar Navis 吗？ y(默认)/n'))
        txt = input().strip().lower()
        
        if txt == 'y' or txt =='':install();break
        elif txt == 'n':input(_("按回车键退出..."));break
        else:print('\n'); print(_('不合法输入，请重新输入'))
        
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some parameters.')

    #parser.add_argument('-l', '--lang', type=str, default='en', help='Language code (default: en)')
    parser.add_argument('-l', '--lang', action='store_true', help='only choose language')
    parser.add_argument('-c', '--config', action='store_true', help='just configure')
    
    args = parser.parse_args()
    
    if args.config:
        _configuration()
    
    elif args.lang:
        _choose_language()
    
    elif not args.lang and not args.config:
        main()

