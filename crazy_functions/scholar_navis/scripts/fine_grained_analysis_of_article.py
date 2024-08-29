import os
import yaml
import shutil
from .tools import pdf_reader
from .tools.multi_lang import _
from .tools.const import SCHOLAR_NAVIS_ROOT_PATH
from .tools.common_plugin_para import common_plugin_para
from crazy_functions.pdf_fns.breakdown_txt import breakdown_text_to_satisfy_token_limit
from toolbox import CatchException,get_user,get_log_folder,update_ui,update_ui_lastest_msg
from ...crazy_utils import get_files_from_everything,read_and_clean_pdf_text,request_gpt_model_in_new_thread_with_ui_alive
from .tools.article_library_ctrl import download_file, markdown_to_pdf, db_type,SQLiteDatabase,get_tmp_dir_of_this_user,check_library_exist_and_assistant,get_this_user_library_list,lib_manifest,pdf_yaml


@check_library_exist_and_assistant(accept_nonexistent=True,accept_blank=True)
@CatchException
def 精细分析文献(txt: str, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    # 非常精细的分析一篇文章，
    '''
    实现的过程：
    1. 对摘要、引言、实验方法、结论讨论分别总结
    2. 总结实验的创新性与开拓性
    3. 如果有，也总结一下实验的缺陷
    '''

    # < --------------------读取插件的参数与各种路径--------------- >

    library_name = plugin_kwargs['lib']
    GPT_prefer_language = plugin_kwargs['gpt_prefer_lang']

    # 工具的根目录与各种目录
    tool_root = get_log_folder(user=get_user(
        chatbot), plugin_name='scholar_navis')
    this_library_fp = os.path.join(tool_root, library_name)
    repo_dir = os.path.join(this_library_fp, 'repository')
    
    file_exist,pdfs_fp,_1 = get_files_from_everything(txt,'.pdf')

    chatbot.append([_('现在可以进行单篇文章的精细分析。支持总结库内置文章或上传的其他文章'), _('等待指令中...')])
    yield from update_ui(chatbot, history)

    # < --------------------将txt修正成可用路径------------------------- >

    # 如果是上传的文章（仅限pdf格式，不支持zip等），那就没问题了
    if file_exist:
        txt = pdfs_fp[0]
        if len(pdfs_fp) >= 2 : yield from update_ui_lastest_msg(_('[注意] 上传的文献多于1篇。<b>精细分析时仅使用第一篇文章</b>'), chatbot, history)

    # 如果上传的不是路径（路径不存在），直接跳转到展示的界面吧
    else:
        txt = ''
    
        # < --------------------没有输入任何可用的东西，提醒用户该怎么做------------------------- >

    # 如果啥都没输入，说一声，并且顺便展示一下已经加载了的文章
    if txt == '':

        # 总结库的名字也保持空，提醒以下
        if library_name == '':
            # 展示该用户名下所有的的总结库
            list = get_this_user_library_list(tool_root)
            if list == []:
                show_to_user = _("该用户没有任何总结库")
            else:
                show_to_user = _("下面是该用户拥有的总结库：\n\n")
                for manifest_fp in list:
                    with open(manifest_fp,'r') as yml:
                        name = yaml.safe_load(yml)[lib_manifest.library_name.value]
                    if not name is None:
                        show_to_user = show_to_user + "- "+f"{name}\n"
            yield from update_ui_lastest_msg(_('没有指定任何文章。可以选择上传文章或者从总结库中选择一篇文章进行分析</br></br>{}').format(show_to_user), 
                                            chatbot, history)
            return 
            
        # 甚至没有输入一个可以用的总结库（accept_nonexistent=True，修饰器不会检测是否）
        if not os.path.exists(this_library_fp):
            yield from update_ui_lastest_msg(_('没有上传可用的文章，<b>{}</b> 亦不是已有的总结库').format(library_name)
                                            , chatbot, history)
            return
        
        all_pdf_yml_fp = []
        for f in os.listdir(repo_dir):
            if f.endswith('.yml'):
                all_pdf_yml_fp.append(os.path.join(repo_dir,f))

        # 直接就没有没有加载完成的pdf，也提醒一下
        if len(all_pdf_yml_fp) == 0:
            yield from update_ui_lastest_msg(_('总结库 <b>{}</b> 中不存在任何已经加载完成的文章').format(library_name), chatbot, history)
            return

        # 把已经加载的文章给列举出来，并写入HTML中
        body_html = ''
        for pdf_fp in all_pdf_yml_fp:
            # 读取一下信息，方便用户确定要分析哪一篇文章，就是展示一下分析的结果，看看是这个吗
            # 为什么要用预分析的结果：语言是用户设定的，没有无用信息，排版一般而言也更好看一些
            with open( pdf_fp,'r') as f:
                yml = yaml.safe_load(f)
                filename,_1 = os.path.splitext(os.path.basename(pdf_fp))
                content =  yml[pdf_yaml.analysis.value]
                title = yml[pdf_yaml.title.value]
                # 如果title没有，就用文件名吧
                if title == 'None' or title is None: title = filename
                doi = yml[pdf_yaml.doi.value]
                '''  这个是旧版的，先留着
                doi_html = f'<a href="http://dx.doi.org/{doi}" target="_blank">[访问文章发布页...]</a>'          
            analyed_pdf_list_html = f'<details><summary>{title}  {doi_html} </summary>{content}</details></br>{analyed_pdf_list_html}'
        chatbot.append([f"尚未输入一个可用的文章。可以选择上传一篇文章，也可以从加载的文章中选择一篇使用。",
                        f'总结库 <b>{archive_name}</b> 包含下面的文章：</br>展开文字可以看到文章的预分析结果。\
                        使用时可以直接复制该文字</br></br><div style="height:500px;overflow-y:auto">{analyed_pdf_list_html}</div>'])
        '''     
                # 先把控件（其实是超链接）准备好
                # 就是显示的内容和辅助用的按钮
                path = os.path.relpath(pdf_fp)[:-3] +'pdf'#yaml替换成pdf
                path = path.replace('\\','/')
                press_hyperlink = _('访问文章发布页')
                copy_hyperlink = _('复制文章')
                download_hyperlink = _('下载文章')
                body_html = f'<details><p><summary><b>{title}</b></br>\
                            <a href="http://dx.doi.org/{doi}" target="_blank">[{press_hyperlink}]</a> \
                            <a href="javascript:void(0);" onclick="copyText(\'{path}\')">[{copy_hyperlink}]</a> \
                            <a href="javascript:void(0);" onclick="downloadLink(\'{path}\',\'{title}.pdf\')">[{download_hyperlink}]</a> \
                            [{doi}] [{filename}]\
                            </summary></p>\
                            <p>{content}</p></details><br>{body_html}'

        # 再获取一下关键词
        with open(os.path.join(this_library_fp,'lib_manifest.yml'),'r') as f:
            keywords = ', '.join(yaml.safe_load(f)[lib_manifest.key_words.value])
        
        # body上加上标题和尾巴
        library_indicator = _('总结库')
        title_text = _('包含下面的文章：')
        line_1 = _('展开文字可以看到文章的预分析结果。如果没有正常显示标题，说明文章标题获取失败，但不影响后续使用')
        line_2 = _('分析中使用的关键词：')
        line_3 = _('如果没有正常的显示文章标题，可能是该文章没有doi，或是没有在metadata中设定标题，此时显示的一般为文件名')
        line_4 = _('如果 [访问文章发布页] 不可用，可能是该文章没有doi，也可能是网络错误')

        body_html = f'</head><body><article class="markdown-body"><p>{library_indicator }&nbsp;<strong>{library_name}</strong>&nbsp;{title_text}</p>\
                    <ul><li>{line_1}</li>\
                    <li>{line_2} {keywords}</li>\
                    <li>{line_3}</li>\
                    <li>{line_4}</li>\
                    </ul><hr>{body_html}</article></body></html>'

        # 之后在缓存文件夹中，新建一个html，用于显示所有的文章信息
        html_tmp_fp = os.path.join(get_tmp_dir_of_this_user(chatbot,'html',[]),f'{library_name}_show_all_article.html')
        shutil.copy(os.path.join(SCHOLAR_NAVIS_ROOT_PATH,'scripts','res','all_articles.html'),html_tmp_fp)
        with open(html_tmp_fp,'a' ,encoding='utf-8') as f:
            f.write(body_html)
            
        chatbot.append([_("尚未输入一个可用的文章。可以选择上传一篇文章，也可以从加载的文章中选择一篇使用"),
                        '<ul><li><a href="/file={file_path}" target="_blank">{indicator} </a>{do_what}</li>'
                        .format(file_path = os.path.relpath(html_tmp_fp),indicator=_('您可以点击这里'),do_what=_('查阅该总结库包含的文章')),
                        ])
        
        yield from update_ui(chatbot, history)
        return


    # < --------------------提交给AI，进行后续的处理------------------------- >
    yield from update_ui_lastest_msg(_('精细分析中...'), chatbot, history)
    try:
        yield from __analyse_pdf(pdf_fp=txt, llm_kwargs=llm_kwargs, chatbot=chatbot, history=history, use_ai_assist = plugin_kwargs['ai_assist'], GPT_prefer_language = GPT_prefer_language)
    except Exception as e:
        yield from update_ui_lastest_msg(_('分析过程中出错！错误原因是：{}').format(str(e)), chatbot, history)


def __analyse_pdf(pdf_fp: str, llm_kwargs, chatbot, history, use_ai_assist, GPT_prefer_language):
    """精细分析文章

    Args:
        pdf_fp (str): _description_
        llm_kwargs (_type_): _description_
        chatbot (_type_): _description_
        history (_type_): _description_
        system_prompt (_type_): _description_
        user_request (_type_): _description_
    """
    history = []
    
    
    # 看看数据库里面有没有(因为是支持直接复制库内文章的)
    pdf_yml_fp = f'{pdf_fp[:-3]}yml'
    if not os.path.exists(f'{pdf_fp[:-3]}yml'):
        _1, pdf_yml_fp = pdf_reader.get_pdf_inf(pdf_fp,use_ai_assist,llm_kwargs) # 外部导入的文章（没有yml），临时生成一个
    with open(pdf_yml_fp , 'r') as yml:
        yaml_content = yaml.safe_load(yml)
        doi = yaml_content[pdf_yaml.doi.value]
        title = yaml_content[pdf_yaml.title.value]
        
    with SQLiteDatabase(type=db_type.doi_fulltext_ai_understand) as ft:
        fulltext = ft.select(doi,('fulltext',))
    # 没有的话，只能跑一边AI了
    if fulltext is None:
    
        yield from update_ui_lastest_msg(_('对pdf文件处理中...'), chatbot, history)
        # 获取pdf的内容（可能不含参考文献等内容，所有比正文字号小的都被删掉了）
        pdf_content, _1 = read_and_clean_pdf_text(pdf_fp)
        # 满足LLM的token要求进行切割
        pdf_content_token = breakdown_text_to_satisfy_token_limit(txt=pdf_content, limit=2048, llm_model=llm_kwargs['llm_model'])

        for index, content in enumerate(pdf_content_token):
            i_say = f"Please read the passage and retell it in English, emulating the author's writing style and narrative logic. Here's the excerpt: {content}"
            # 一般第一个就是标题啦
            if index == 0: i_say = i_say + f"If you encounter a title, please also repeat it in English."
            i_say_show = _("[{i}/{total}] AI阅读中...").format(i=index+1,total=len(pdf_content_token))
            
            #通常的，对分片进行总结
            gpt_say_for_fragment = yield from request_gpt_model_in_new_thread_with_ui_alive(i_say, i_say_show, llm_kwargs, chatbot,
                                                                            history=[], # 分段总结的时候，不需要历史记录
                                                                            sys_prompt='As a native speaker, grab the key points, please.')
            history.append(gpt_say_for_fragment)
            
        # 跑完AI，记录一下读到的全文
        with SQLiteDatabase(type=db_type.doi_fulltext_ai_understand) as ft:
            ft.insert_ingore(doi,('fulltext',),('\n\n\n'.join(history),))
    
    # 有的话，用它就行
    else:
        history = fulltext[0].split('\n\n\n')
    
    # 最后的总结    
    i_say = f'''Please read the above content and provide me with its title, 
        including both the original language and the {GPT_prefer_language}. 
        Also, please give me a detailed and accurate summary of the content in {GPT_prefer_language}, 
        along with the introduction or research background, the experimental methods, the conclusions, 
        the innovative aspects of the experiment, and its limitations and deficiencies. 
        Additionally, inform me about the author's writing style and narrative logic, 
        so I can get some advice for my own writing. '''
        
    i_say_show = _("总结中...")
    gpt_say_last = yield from request_gpt_model_in_new_thread_with_ui_alive(i_say, i_say_show, llm_kwargs, chatbot,
                                                                history=history,sys_prompt=f"Beautify the text with markdown formatting. Please be as detailed as possible.")

    
    #记录历史记录，便会交流
    chatbot.clear()
    chatbot.append([_('分析的文章如下：'),
                        f'<a href="https://dx.doi.org/{doi}" target="_blank">{title}</a></br>' +
                        _('标题可能不准确，跳转连接亦或许无法使用，仅供参考')])
    yield from update_ui(chatbot=chatbot,history=[])
    chatbot.append([_("精细分析完成，以下是分析的结果（现在亦可以与AI进行交流，也可以下载分析的结果）: "),gpt_say_last])
    history.append(f'Please reply to me using {GPT_prefer_language}') # 防止意外，再加一次
    
    # 提供一下下载
    pdf_path = os.path.join(get_tmp_dir_of_this_user(chatbot,'markdown2pdf',['Fine-grained Analysis of Article']),f'Analysis of {title}.pdf')
    pdf = markdown_to_pdf(gpt_say_last,f'Analysis of {title}')
    pdf.save(pdf_path)
    chatbot.append([_("下载分析结果："),download_file(pdf_path)])

    yield from update_ui(chatbot=chatbot,history=history) # 这里的history是分片总结得到的内容
    
class Fine_Grained_Analysis_of_Article(common_plugin_para):
    def define_arg_selection_menu(self):
        gui_definition = {}
        gui_definition.update(self.add_file_upload_field(title=_('选定的文章'),description=_('上传或使用总结库内的文章')))
        gui_definition.update(self.add_lib_field(True, _('选择总结库'), _('查看总结库内的文章')))
        gui_definition.update(self.add_command_selector([],[],[]))
        gui_definition.update(self.add_GPT_prefer_language_selector())
        gui_definition.update(self.add_use_AI_assistant_selector())
        return gui_definition

    def execute(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
        yield from 精细分析文献(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request)
