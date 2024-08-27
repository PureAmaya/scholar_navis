import os
import sys
import shutil
import argparse
import subprocess
from scripts.tools.sn_config import GPT_SUPPORT_LAMGUAGE
from scripts.tools.multi_lang import _,i18n
from scripts.tools.sn_config import VERSION,CONFIG,write_config 
from scripts.tools.article_library_ctrl import GPT_ACADEMIC_ROOT_PATH,SCHOLAR_NAVIS_DIR_NAME,SCHOLAR_NAVIS_ROOT_PATH

def __choose_language():
    
    # 选择 显示语言
    print('如果希望使用 简体中文 作为显示语言，请输入1')
    print('若希望使用 繁體中文 作為顯示語言，請輸入2.')
    print('If you wish to use English as the display language, please enter 3.')
    
    while(True): # 反正就仨）
        txt = input('\n').strip()
        if txt == '1':CONFIG['display_language'] = 'zh-Hans';break
        if txt == '2':CONFIG['display_language'] = 'zh-Hant';break
        elif txt == '3' :CONFIG['display_language'] = 'en-US';break
        else:print('不合法输入，请重新输入\n不合法輸入，請重新輸入\nInvalid input, please try again.')
    
    # 保存偏好
    write_config()
    # 更新语言
    i18n.update()
    
    __clear_console()
    
    # 选择 GPT偏好语言
    print('\n')
    for index,v in enumerate(GPT_SUPPORT_LAMGUAGE):
        print(_('如果希望 {lang} 为GPT的偏好语言，请输入 {k}').format(lang=v,k=index + 1))

    while(True):
        txt = input('\n').strip()
        try:
            txt_int = int(txt) - 1
            CONFIG['GPT_prefer_language'] = GPT_SUPPORT_LAMGUAGE[txt_int];break
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
    
    # 检查安装目录是否可用（仅支持英文字母，数字，下划线，并且不能是纯数字，开头也不能是数字）
    all_is_letters_number_underscore = all(char.isalnum() or char == '_' for char in SCHOLAR_NAVIS_DIR_NAME)
    if  (not all_is_letters_number_underscore) or SCHOLAR_NAVIS_DIR_NAME.isdigit() or SCHOLAR_NAVIS_DIR_NAME[0].isdigit():
        print(_('安装的文件夹 "{}" 不合规。仅支持英文字母，数字，下划线，并且不能是纯数字，开头也不能是数字').format(SCHOLAR_NAVIS_DIR_NAME))
        install_vaild = False
    
    if not install_vaild:
        input(_("按回车键退出..."))
        sys.exit(1)

def __clear_console():
    if sys.platform == 'win32':os.system('cls')
    else:os.system('clear') 

def __install_def_data():
    
    def_database_fp = os.path.join(SCHOLAR_NAVIS_ROOT_PATH,'def_data')
    user_database_fp = os.path.join(SCHOLAR_NAVIS_ROOT_PATH,'data')
    
    if not os.path.exists(def_database_fp):
        print(_('找不到预先数据，该过程跳过'))
        return
    
    # 因为现在默认数据没多少，就先用想要预安装的数据库顶着吧
    if os.path.exists(user_database_fp):
        print(_('已安装预先数据，该过程跳过'))
    else:
        shutil.copytree(def_database_fp,user_database_fp)
        print(_('预先数据安装完成'))

def __crazy_function_modifier():
    
    txt = f'''
    ###### SCHOLAR NAVIS START ########
    from crazy_functions.{SCHOLAR_NAVIS_DIR_NAME}.scripts.tools.gpt_academic_handler import registrator
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
        
def __config_pri_modifier():
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
        
def __install_requirement():
        # 安装需要的包
    requirements_fp = os.path.join(SCHOLAR_NAVIS_ROOT_PATH,'requirements.txt')
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
                # gpt_Academic的依赖库
                subprocess.run(['pip', 'install', '-r',f'{os.path.join(GPT_ACADEMIC_ROOT_PATH,"requirements.txt")}','--upgrade'])
                # school navis的依赖库
                subprocess.run(['pip', 'install', '-r',f'{os.path.join(SCHOLAR_NAVIS_ROOT_PATH,"requirements.txt")}','--upgrade'])
                print(_('requirements.txt 安装成功'))
            elif country == 'y' or country == '':
                # gpt_Academic的依赖库
                subprocess.run(['pip', 'install', '-r',f'{os.path.join(GPT_ACADEMIC_ROOT_PATH,"requirements.txt")}','--upgrade','-i','https://pypi.mirrors.ustc.edu.cn/simple/'])
                # school navis的依赖库
                subprocess.run(['pip', 'install', '-r',f'{os.path.join(SCHOLAR_NAVIS_ROOT_PATH,"requirements.txt")}','--upgrade','-i','https://pypi.mirrors.ustc.edu.cn/simple/'])
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
    
    __clear_console()
    
    # 安装预先数据 现在暂时不需要了
    #__install_def_data()
    
    #  crazy中安装本工具 
    __crazy_function_modifier()
        
    # 配置中加上去
    __config_pri_modifier()
    
    # 安装需要的包
    __install_requirement()
    
    #提示一下应该调整的配置
    __config_prompt()


def main():
    
    __clear_console()
    
    print('\n')
    print(_('欢迎使用Scholar Navis'))
    print(f'ver. {VERSION}\n')
    
    # 选择语言
    __choose_language()
    
    # 路经检查
    __check_path()
    
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
    
    args = parser.parse_args()
    
    if not args.lang:
        main()
    else:
        __choose_language()
