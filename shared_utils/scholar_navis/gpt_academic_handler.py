import gradio as gr
from toolbox import HotReload
from .multi_lang import _
from .sn_config import CONFIG
from .file_auto_deleter import start_clear_old_files
try:
    from shared_utils.colorful import print亮黄
except:
    from shared_utils.colorful import PrintBrightYellow as print亮黄


enable_translator = CONFIG['enable_simple_translator'] # 翻译完之后，别忘了把这个给关了
enable_pubmed_downloader = CONFIG['enable_pubmed_downloader']

def registrator(function_plugins:dict):
    
    # 负责与 gpt_academic 交互，用它调用，合理（
    
    
    start_clear_old_files()
    
    try:
        from crazy_functions.scholar_navis.scripts.cache_pdf_articles import pdf_cacher
        function_plugins.update(
                {
                    'step 1. ' + _("缓存pdf文献"): {
                        "Group": "Scholar Navis",
                        "Color": "stop",
                        "AsButton": True, 
                        "Function": None,
                        "Class":pdf_cacher,
                        "ClassHotReload":True # 使这样子的面板也支持热更新
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
                        "Class":Summarize_Articles_Keywords,
                        "ClassHotReload":True # 使这样子的面板也支持热更新
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
                        "Class":Communicate_with_AI_about_research_progress,
                        "ClassHotReload":True # 使这样子的面板也支持热更新
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
                        "Class":Fine_Grained_Analysis_of_Article,
                        "ClassHotReload":True # 使这样子的面板也支持热更新
                    }
                }
            )
        
        if enable_pubmed_downloader:
            from crazy_functions.scholar_navis.scripts.pubmed_openaccess_articles_download import PubMed_Open_Access_Articles_Download
            function_plugins.update(
                {
                    _("PubMed_OpenAccess文章获取"): {
                        "Group": "Scholar Navis",
                        "Color": "stop",
                        "AsButton": True, 
                        "Function": None,
                        "Class":PubMed_Open_Access_Articles_Download,
                        "ClassHotReload":True # 使这样子的面板也支持热更新
                    }
                }
            )
        
        # 开发时多语言翻译用
        if enable_translator:
            from crazy_functions.scholar_navis.scripts.tools.multi_language_translator import 多语言翻译器
            function_plugins.update(
            {
                '[Dev]'+ _("多语言翻译器"): {
                    "Group": "Scholar Navis",
                    "Color": "stop",
                    "AsButton": True, 
                    "Function": HotReload(多语言翻译器),
                }
            }
        )
    except Exception as e:
        print亮黄(_("Scholar Navis 加载失败") + "  " + str(e))
    
    return function_plugins
    
def panel_registrator(plugins: dict):
    # 负责注册面板，用它调用，合理（
    gr.HTML('<h3 align="center">{}</h3>'.format(_("Scholar Navis 文章总结分析工具")))
    with gr.Row():
        for index, (k, plugin) in enumerate(plugins.items()):
            if plugin.get("Group") != 'Scholar Navis': continue
            variant = plugins[k]["Color"] if "Color" in plugin else "primary"
            btn_elem_id = f"plugin_btn_{index}"
            plugin['Button'] = plugins[k]['Button'] = gr.Button(k, variant=variant,
                visible=True, elem_id=btn_elem_id).style(size="sm")
            plugin['ButtonElemId'] = btn_elem_id
    
    gr.Markdown('----------------')
    
    clear_custom_btn = gr.Button(_("清除API-KEY"), variant="secondary", visible=True).style(size="sm")
    clear_custom_btn.click(fn=None,_js='delete_user_custom_data')
    return plugins
    

    

