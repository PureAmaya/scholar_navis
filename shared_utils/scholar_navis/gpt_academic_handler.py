'''
Author: scholar_navis@PureAmaya
'''

import sys
import gradio as gr
from .multi_lang import _
from shared_utils.config_loader import get_conf
from .const_and_singleton import GPT_SUPPORT_LAMGUAGE
from old_file_clear import start_clear_old_files
from .other_tools import generate_text_file_download
from shared_utils.colorful import print亮黄

ENABLE_PUBMED_DOWNLOADER,EXTRACT_USEFUL_SENTENCES_THREADS_MAX_NUM=get_conf('ENABLE_PUBMED_DOWNLOADER','EXTRACT_USEFUL_SENTENCES_THREADS_MAX_NUM')

def registrator(function_plugins: dict):

    # 负责与 gpt_academic 交互，用它调用，合理（

    start_clear_old_files()

    #try:
    from crazy_functions.scholar_navis.scripts.cache_pdf_articles import pdf_cacher
    function_plugins.update(
        {
            'step 1. ' + _("缓存pdf文献"): {
                "Group": "Scholar Navis",
                "Color": "stop",
                "AsButton": True,
                "Function": None,
                "Class": pdf_cacher,
                "ClassHotReload": True  # 使这样子的面板也支持热更新
            }
        }
    )

    from crazy_functions.scholar_navis.scripts.summarize_articles_by_keywords import Summarize_Articles_Keywords
    function_plugins.update(
        {
            'step 2. ' + _("按关键词总结文献"): {
                "Group": "Scholar Navis",
                "Color": "stop",
                "AsButton": True,
                "Function": None,
                "Class": Summarize_Articles_Keywords,
                "ClassHotReload": True  # 使这样子的面板也支持热更新
            }
        }
    )

    from crazy_functions.scholar_navis.scripts.communicate_with_ai_about_research_progress import Communicate_with_AI_about_research_progress
    function_plugins.update(
        {
            'step 3. ' + _("与AI交流研究进展"): {
                "Group": "Scholar Navis",
                "Color": "stop",
                "AsButton": True,
                "Function": None,
                "Class": Communicate_with_AI_about_research_progress,
                "ClassHotReload": True  # 使这样子的面板也支持热更新
            }
        }
    )

    from crazy_functions.scholar_navis.scripts.fine_grained_analysis_of_article import Fine_Grained_Analysis_of_Article
    function_plugins.update(
        {
            'step 4. ' + _("精细分析文献"): {
                "Group": "Scholar Navis",
                "Color": "stop",
                "AsButton": True,
                "Function": None,
                "Class": Fine_Grained_Analysis_of_Article,
                "ClassHotReload": True  # 使这样子的面板也支持热更新
            }
        }
    )

    if ENABLE_PUBMED_DOWNLOADER:
        from crazy_functions.scholar_navis.scripts.pubmed_openaccess_articles_download import PubMed_Open_Access_Articles_Download
        function_plugins.update(
            {
                _("PubMed_OpenAccess文章获取"): {
                    "Group": "Scholar Navis",
                    "Color": "stop",
                    "AsButton": True,
                    "Function": None,
                    "Class": PubMed_Open_Access_Articles_Download,
                    "ClassHotReload": True  # 使这样子的面板也支持热更新
                }
            }
        )
    
        
    #except Exception as e:
        # 获取异常信息
        #exc_type, exc_value, exc_tb = sys.exc_info()
        # 获取出错的行号
        #line_number = exc_tb.tb_lineno
        #print亮黄(_("Scholar Navis 加载失败") + f"  line {line_number}: " + str(e))

    return function_plugins


def common_functions_panel_registrator(plugins: dict):
    gr.HTML('<h3 align="center">{}</h3>'.format(_("Scholar Navis 文章总结分析工具")))
    with gr.Row(equal_height=True):
        for index, (k, plugin) in enumerate(plugins.items()):
            if plugin.get("Group") != 'Scholar Navis':
                continue
            variant = plugins[k]["Color"] if "Color" in plugin else "primary"
            btn_elem_id = f"plugin_btn_{index}"
            plugin['Button'] = plugins[k]['Button'] = gr.Button(k, variant=variant,
                                                                visible=True, elem_id=btn_elem_id,size='sm')
            plugin['ButtonElemId'] = btn_elem_id

    #gr.Markdown('----------------')

    #clear_custom_btn = gr.Button(_("清除API-KEY"), variant="secondary", visible=True,size='sm')
    #clear_custom_btn.click(fn=None, js='delete_user_custom_data')
    return plugins


def extract_useful_sentenses_panel(cookies,md_dropdown,temperature,top_p,user_custom_data):
    
    
    template_content ='''\
title,text
样例标题,此处用于输入该片文章所有待提取的文本。例如摘要 +前言 + 结论和讨论。一篇文章一行内容
樣本標題,此處用於輸入該篇文章所有待提取的文本。例如摘要、前言、結論和討論。一篇文章一行內容
Sample Title,"This cell is used to input all the text to be extracted from the article. For example, the abstract, introduction, conclusion, and discussion. Each article is on a single line."
        '''
    
    # 后方逻辑处理：summary_useful_sentences.py
    # 这里只负责UI更新和展示
    
    gr.HTML(
        '''<h3 align="center">{descr}</h3>
            <p align ="center">{fn_descr}<br>
            <font color ='red'>{warning}</font></p>
            <p align ="center"><strong>{large_files_warning}<br>{only_local_access}</strong></p>
'''.format(descr = _('使用此功能，批量从文章中获取有用的语句（保留原文便于快速查阅），并将其翻译成更熟悉的语言（便于阅读）'),
        fn_descr = _('适用于撰写文章摘要、前沿等内容。也可用于快速的文章学习'),
        warning = _('AI可能犯错或不完整，仍需要人工校对或人工检索原文章!'),
        large_files_warning = _('注意：文件过大时，可能会导致程序卡顿，并且处理速度会很慢。请耐心等待'),
        only_local_access = _('仅限本地使用。如果要中断任务，务必点击下方的“终止”按钮，否则任务无法结束'))
    )

    gr.Markdown('### 0. ' + _('新建摘要任务或导入已有任务'))
    gr.Markdown(_('- 新建任务时，推荐手动准备资源。第一列是文章标题，第二列是文章原文，需要有表头，以csv文件储存') +'\n' +
                    _('- 新建任务时，也可以直接上传PDF（支持压缩包），使用该自动工具获取文章资源（效果稍差）') + '\n' +
                    _('- 已经发生摘取行为后无法使用此功能'))
    task_name = gr.Textbox(value='',label=_('任务名称'),placeholder=_('输入任务名称，否则使用默认名称'))
    create_or_load_task = gr.File(label=_('请上传包含文章标题与内容的csv文件 or 以往下载的分析文件（.zip）or pdf or pdf的压缩包（.zip/.rar）'),file_types=['.zip','.rar','.csv','.pdf','.xls','.xlsx'])
    gr.HTML(value=_('点击这里下载样例csv文件: {}').format(generate_text_file_download(template_content,'extract_useful_sentences_template','.csv','utf-8-sig',True)))
    
    with gr.Accordion(visible=False) as below_accordion:
    
        gr.Markdown('### 1. ' + _('[可选] 增量添加PDF (zip / rar 格式)'))
        gr.Markdown(_('- 向摘要任务中添加额外的PDF文章'))
        add_pdf = gr.Files(label=_('请上传pdf或pdf的压缩包（.zip / .rar）'),file_types=['.zip','.rar','.pdf'])
        
        gr.Markdown('### 2. ' + _('设定分析参数'))
        gr.Markdown(_('关于AI的调整请使用页面顶部的设置'))
        with gr.Row(equal_height=True):
            content_requirements = gr.Textbox(value='',label=_('内容要求'),placeholder=_('输入对于内容的总体要求'),lines=3); 
            stru_requirements = gr.Textbox(value='',label=_('结构要求'),placeholder=_('输入对于行文结构的要求（一行一个）\n也可视为对内容的分类'),lines=3); 
        with gr.Row():
            support_language = list(GPT_SUPPORT_LAMGUAGE);support_language.insert(0,'')
            language = gr.Dropdown(value='简体中文',label=_('请选择翻译语言'), choices=support_language,allow_custom_value=False)
            max_workers = gr.Slider(minimum=1,maximum=EXTRACT_USEFUL_SENTENCES_THREADS_MAX_NUM,step=1,value=EXTRACT_USEFUL_SENTENCES_THREADS_MAX_NUM//2,label=_('最大并发数'),info=_('越大提取越快。过大可能会遇到问题'),interactive=True)
        
        gr.Markdown('### 3. '+_('选择操作步骤'))
        task_exec_btn = gr.Button(value=_('执行'))
        
        gr.Markdown('### 4. '+_('获取结果'))
        gr.Markdown(_('- 注意，当运行出错或超时（例如请求达到上限、网络问题），会自动结束任务，并输出结果')+ '\n' + 
                    _('- 可以选择“停止”，下载全部文件后，重新运行摘取功能。会继续之前的进度进行摘取')+ '\n' + 
                    _('- <b>在显示下载按钮之前，都是未完成的状态！</b>')+ '\n' + 
                    _('- 摘取完成后（无论成功与否），需要点击“重置”按钮以开启新一轮的摘取'))
        
        all_files_dl = gr.DownloadButton(label=_('全部下载(包含摘取结果，便于后续添加新文章)'),visible=False)
        result_file_dl = gr.DownloadButton(label=_('仅下载结果'),visible=False)
        
        gr.Markdown('--------------------')
        cancel_btn = gr.Button(value=_('终止'),visible=False)
        reset_btn = gr.Button(value=_('重置'))
        
    log = gr.Textbox(value='',label=_('日志'),interactive=False,lines=10,max_length=30,show_copy_button=True)
    
    # 将 gr_combo 列表转换为字典
    gr_combo = {
        'task_name':task_name,
        'create_or_load_task': create_or_load_task,
        'below_accordion':below_accordion,
        'add_pdf': add_pdf,
        'content_requirements': content_requirements,
        'stru_requirements': stru_requirements,
        'language': language,
        'max_workers': max_workers,
        'task_exec_btn':task_exec_btn,
        'all_files_dl': all_files_dl,
        'result_file_dl':result_file_dl,
        'cancel_btn':cancel_btn,
        'reset_btn':reset_btn,
        'log':log,
        'cookies':cookies,
        'temperature':temperature,
        'md_dropdown':md_dropdown,
        'top_p':top_p,
        'user_custom_data':user_custom_data,
    }
    
    try:
        from crazy_functions.scholar_navis.scripts.extract_useful_sentences import gradio_func
        return gradio_func(**gr_combo) # 返回停止句柄
    except Exception as e:
        # 获取异常信息
        exc_type, exc_value, exc_tb = sys.exc_info()
        # 获取出错的行号
        line_number = exc_tb.tb_lineno
        print亮黄(_("Scholar Navis 加载失败") + f"  line {line_number}: " + str(e))
        


