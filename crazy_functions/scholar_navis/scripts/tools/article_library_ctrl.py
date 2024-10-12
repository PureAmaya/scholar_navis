import os
import csv
import yaml
import shutil
import codecs
import pymupdf
from enum import Enum
from shared_utils.scholar_navis.multi_lang import _
from functools import wraps
from datetime import datetime
from shared_utils.scholar_navis.sn_config import CONFIG,VERSION
from shared_utils.scholar_navis.const import SCHOLAR_NAVIS_ROOT_PATH,GPT_ACADEMIC_ROOT_PATH

class lib_manifest(Enum):# 单纯为了规范yaml的名称
    library_name = 'library_name'
    key_words = 'key_words'
    version = 'version'

class pdf_yaml(Enum):# 单纯为了规范yaml的名称
    abstract = 'abstract'
    filename = 'filename'
    title = 'title'
    doi = 'doi'
    analysis = 'analysis'
    full_txt = 'full_txt'
    
# 规范化总结库名称
_forbidden_contain = ( '\\', '/', ':', ';', '(', ')', '<', '>', '\"', '\'', '|', '@', '#', '$',  '?', '*')
_forbidden_startwith = ('.', '-', '+')


def check_library_exist_and_assistant(accept_nonexistent=False,accept_blank = False):
    """
        - 检测总结库是否存在，总结库名称输入检验合法性
        - 提供通用命令 help、info、about 的实现
        - 负责每个工具一开始的UI重置与历史记录的清除

    Args:
        accept_nonexistent (bool, optional): 允许总结库不存在吗。如果允许，则不会检查与处理总结库是否存在
        accept_blank (bool, optional): 允许总结库输入框为空吗。如果允许，则不会检查与处理总结库栏为空的情况
    """
    
    # 不适合放在外面的
    from toolbox import ChatBotWithCookies, update_ui, get_log_folder, get_user

    
    
    def decorate(f):
        @wraps(f)
        # 顺序 txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request
        def wrapper(*args):
            
            chatbot: ChatBotWithCookies = args[3]
            chatbot.clear()
            yield from update_ui(chatbot=chatbot, history=[])  # 这里是为了防止部分插件在按下终止按钮再次运行后，再次显示终止前的内容
            
            # < --------------------参数获取与检验，以及传递一些信息--------------- >
            
            plugin_kwargs = args[2]
            txt: str = args[0].strip() #去除无用空格等不可见字符 即所谓的 main_input

            # 命令（及其参数）修订
            if ':' in plugin_kwargs['command'] :#有一说一，只要是可用的命令，肯定会有英文冒号2333
                plugin_kwargs['command'] = plugin_kwargs['command'].split(':')[0]  #command是一定有的
            else:# 没有英文冒号的，就是没有选定任何命令
                plugin_kwargs['command'] =''
            command = plugin_kwargs['command'] # 方便起见，给个变量（）
            plugin_kwargs['command_para'] = plugin_kwargs.get('command_para','').strip()
            
            # 语言设定修订
            plugin_kwargs['gpt_prefer_lang'] = plugin_kwargs.get('gpt_prefer_lang',CONFIG['language_GPT_prefer'])

            # AI辅助修订
            ai_assist_text = plugin_kwargs.get('ai_assist',_('禁用'))
            plugin_kwargs['ai_assist'] = ai_assist_text == _('启用')

            # 获取选定的lib
            plugin_kwargs['lib'] = plugin_kwargs.get('lib','').strip()
            library_name :str = plugin_kwargs['lib']
            
            if any(library_name.startswith(char) for char in _forbidden_startwith) or any(
                char in library_name for char in _forbidden_contain):
                ban_inf = _('<ul><li>不能含有以下字符：{forbidden}</li><li>不能以{forbidden_start}开头</li></ul>').format(forbidden=" ".join(_forbidden_contain),forbidden_start = " ".join(_forbidden_startwith))
                chatbot.append([_("该名称`{}`无法使用，详细说明如下: ").format(library_name)
                                , ban_inf])
                yield from update_ui(chatbot=chatbot, history=[])  # 刷新界面
                return

            # 获取工具的根目录（即没有进入到某一个具体的总结库里面）
            tool_root = get_log_folder(user=get_user(
                chatbot), plugin_name='scholar_navis')
            this_library_fp = os.path.join(tool_root, library_name)
            
            # 插件的文档文件夹
            doc_dir = os.path.join(SCHOLAR_NAVIS_ROOT_PATH,'doc',CONFIG['language_display']) 
                
            # < --------------------通用型用户命令解析--------------------- >
            doc_fp = ''
            # 关于信息
            if command == 'about' or command == 'info':
                doc_fp = os.path.join(doc_dir,'about.md')
                with open(doc_fp,'r',encoding='utf-8') as about:
                    about_content = about.read()
                chatbot.append([_("Scholar Navis (ver.{}) \n关于文档如下。完整版可以参见github发布页").format(VERSION), about_content])
                yield from update_ui(chatbot=chatbot, history=[])  # 刷新界面
                return

            # 版权和许可证
            elif command == 'license' or command == 'licence':
                lisence_fp = os.path.join(doc_dir,'third-party-lisence.md')
                with open(lisence_fp,'r',encoding='utf-8') as lisence:
                    lisence_content = lisence.read()
                chatbot.append([_("Scholar Navis 使用到的第三方库: "), lisence_content])
                yield from update_ui(chatbot=chatbot, history=[])  # 刷新界面
                return

            # 各个插件的帮助文档
            elif command == 'help':
                help_fp = ''
                muilt_lang_name = ''
                if f.__name__ == '与AI交流研究进展':
                    help_fp = os.path.join(doc_dir,'Communicate-with-AI-about-Research-Progress.md')
                    muilt_lang_name = _('与AI交流研究进展')
                
                elif f.__name__ == '按关键词总结文献':
                    help_fp = os.path.join(doc_dir,'Summarize-Articles-by-Keywords.md')
                    muilt_lang_name = _('按关键词总结文献')
                
                elif f.__name__ == '缓存pdf文献':
                    help_fp = os.path.join(doc_dir,'Cache-PDF-Articles.md')
                    muilt_lang_name = _('缓存pdf文献')
                
                elif f.__name__ == '精细分析文献':
                    muilt_lang_name = _('精细分析文献')
                    help_fp = os.path.join(doc_dir,'Fine-grained-Analysis-of-Article.md')
                    
                elif f.__name__ == 'PubMed_OpenAccess文章获取':
                    pass
                    muilt_lang_name = _('PubMed_OpenAccess文章获取')
                    help_fp = os.path.join(doc_dir,'PubMed-Open-Access-Articles-Download.md')
                
                elif f.__name__ == '更好的文章润色':
                    pass
                    muilt_lang_name = _('更好的文章润色')

                # 读取对应的帮助文档
                with open (help_fp,'r',encoding='utf-8') as file:help_inf = file.read()
                
                # 下载这个，因为它有图片，单独处理一下，把图片的放到位于工作目录的用户缓存中
                if f.__name__ == 'PubMed_OpenAccess文章获取':
                    pb_png_tmp_fp = os.path.join(get_tmp_dir_of_this_user(chatbot,'res',[]),'pubmed.png') # 把图片放到缓存里，便于在web中显示
                    pb_png_raw_fp = os.path.join(doc_dir,'img','pubmed.png')
                    if os.path.exists(pb_png_raw_fp):
                        shutil.copy(pb_png_raw_fp,pb_png_tmp_fp)
                        help_inf= help_inf.replace('<img title="PUBMED-CSV" src="img/pubmed.png" alt="" style="zoom:50%;">',
                                                f'<img title="PUBMED-CSV" src="file={pb_png_tmp_fp}" alt="" style="zoom:150%;">')

                chatbot.append([_('<b>{}</b>的帮助文档如下: ').format(muilt_lang_name), help_inf])
                yield from update_ui(chatbot=chatbot, history=[])  # 刷新界面
                return

            # < --------------------高级参数筛查（现在由一个修饰器统一实现）------------------------ >
            # ! 乱（

            # 只有不接受accept_blank时，才检测是否为空白
            # 只有不接受“总结库不存在”的时候，才检测是否存在这个总结库
            if (not accept_blank and library_name == '') or ((not os.path.exists(this_library_fp)) and (not accept_nonexistent)):
                # 如果是单纯输入错误，没有找到这个总结库的话，就额外输出一段内容
                if not os.path.exists(this_library_fp) or  library_name == '':
                    show_to_user = _("总结库 <b>{}</b> 不存在，请检查输入是否准确").format(library_name) if library_name != '' else _('没有输入总结库名称')

                # 展示该用户名下所有的的总结库
                list = get_this_user_library_list(tool_root)
                if list == []:
                    show_to_user = show_to_user +'<br>'+ _("该用户没有任何总结库")
                else:
                    show_to_user = show_to_user +'<br>'+ _("下面是该用户拥有的总结库：\n\n")
                    for manifest_fp in list:
                        with open( manifest_fp,'r') as file:
                            name = yaml.safe_load(file)[lib_manifest.library_name.value]
                        if not name is None:
                            show_to_user = show_to_user + "- "+f"{name}\n"

                chatbot.append([_("不能进行正常操作。下面是有关信息: "), show_to_user])
                yield from update_ui(chatbot=chatbot, history=[])  # 刷新界面
                return
            
            # 正常情况下，就调用原函数
            yield from f(txt, args[1], plugin_kwargs, chatbot, [], args[5], args[6]) # 反正history已经是[]了
            
        return wrapper
    return decorate


def get_def_user_library_list():
    """返回默认用户名下所有的总结库清单
    """
    default_user_dir =  os.path.join(GPT_ACADEMIC_ROOT_PATH,'gpt_log','default_user','scholar_navis')
    return get_this_user_library_list(default_user_dir)


def get_this_user_library_list(tool_root: str):
    """返回当前用户名下所有的总结库清单

    Args:
        tool_root (str):该用户此工具的根目录（不包含任何一个总结库）

    Returns:
        所有总结库的清单文件（manifest.yml）
    """

    list = []
    # 遍历目录
    # 分别是 遍历的目录，子目录文件夹列表，文件列表
    for root, dirs, files in os.walk(tool_root, False): 
        # 跳过非一级子目录，只在每一个总结库的根目录找manifest
        if root.endswith("cache") or root.endswith("repository"):
            continue
        # 遍历文件
        for file_fp in files:
            # 检查文件是否在目标列表中
            if file_fp.endswith('lib_manifest.yml'):
                list.append(os.path.join(root, file_fp))

    return list


def markdown_to_pdf(text:str,title:str,save_dir:str):
    from shared_utils.advanced_markdown_format import markdown_convertion
    
    filename = title
    if any(filename.startswith(char) for char in _forbidden_startwith):
        filename = filename[1:]
    
    for char in _forbidden_contain:
        if char in filename:filename = filename.replace(char,'_')
    
    fp = os.path.join(save_dir,f"{filename}.pdf")
    HTML =  markdown_convertion(text)
    A4 = pymupdf.paper_rect("A4")  # size of a page
    WHERE = A4 + (36, 36, -36, -36)  # leave borders of 0.5 inches
    story =  pymupdf.Story(html=HTML)  # make the story
    writer = pymupdf.DocumentWriter(fp)  # make the writer
    pno = 0 # current page number
    more = 1  # will be set to 0 when done
    while more:  # loop until all story content is processed
        dev = writer.begin_page(A4)  # make a device to write on the page
        more, filled = story.place(WHERE)  # compute content positions on page
        story.draw(dev)
        writer.end_page()
        pno += 1  # increase page number
    writer.close()  # close output file
    return fp


def csv_load(file_fp:str):
    with codecs.open(filename=file_fp,encoding='utf-8-sig') as f:
        c = []
        for row in csv.DictReader(f, skipinitialspace=True):
            c.append(row)
    return c


def _get_dir(root_dir: str, sub_dir: list[str] , create_datetime_dir: bool):
    
    dir = root_dir
    
    if create_datetime_dir:
        dir = os.path.join(dir,datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))

    # 补充子目录
    if len(sub_dir) > 0:
        for sub in sub_dir:
            dir = os.path.join(dir, sub)

    # 自动创建文件夹（如果没有）
    os.makedirs(name=dir, exist_ok=True)

    return dir

def generate_download_file(file_path:str,txt:str = None):
    """生成下载链接（PDF则为跳转到在线服务）

    Args:
        file_path (str): 需要下载的文件路径
        txt (str, optional): 超链接显示的文本. 默认为下载文件的basename.

    Returns:
        str: html的href
    """
    # 为什么要把绝对路径转换为相对路径：下载连接更短，然后可以减少暴露，或许安全点？
    if os.path.isabs(file_path):
        file_path = os.path.relpath(file_path,os.getcwd())

        
    if not txt:txt = os.path.basename(file_path)
        
        
    if file_path.startswith('gpt_log') and file_path.lower().endswith('.pdf'):
        return f'<a href="services/pdf_viewer/web/viewer.html?file={file_path}" target="_blank">{txt}</a>'
    else:    
        return f'<a href="file={file_path}" target="_blank">{txt}</a>'

def get_data_dir(root_dir: str, sub_dir: list[str] = []):
    root_dir = os.path.join(SCHOLAR_NAVIS_ROOT_PATH,'data',root_dir)
    # SCHOLAR_NAVIS_ROOT_PATH/data/root_dir/sub_dir
    return _get_dir(create_datetime_dir=False,root_dir=root_dir,sub_dir=sub_dir)

def get_tmp_dir_of_this_user(chatbot,root_dir: str, sub_dir: list[str] = [],create_datetime_dir=True):
    from toolbox import get_user
    this_user_tmp_dir = os.path.join('tmp',get_user(chatbot))
    sub_dir.insert(0,root_dir)
    # tmp/user/2024-08-29 09-53-20/root_dir/sub_dir
    return _get_dir(root_dir=this_user_tmp_dir,sub_dir=sub_dir,create_datetime_dir=create_datetime_dir)









