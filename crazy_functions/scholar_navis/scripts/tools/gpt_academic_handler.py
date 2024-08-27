from toolbox import HotReload
from .multi_lang import _
try:
    from shared_utils.colorful import print亮黄
except:
    from shared_utils.colorful import PrintBrightYellow as print亮黄


enable_translator = False # 翻译完之后，别忘了把这个给关了

def registrator(function_plugins:dict):
    
    #_check_pwd()
    
    try:
        from ..cache_pdf_articles import pdf_cacher
        function_plugins.update(
                {
                    'step 1. ' + _("缓存pdf文献"): {
                        "Group": "Scholar Navis",
                        "Color": "stop",
                        "AsButton": True, 
                        "Function": None,
                        "Class":pdf_cacher
                    }
                }
            )
        
        from ..summarize_articles_by_keywords import Summarize_Articles_Keywords
        function_plugins.update(
                {
                    'step 2. ' + _("按关键词总结文献"): {
                        "Group": "Scholar Navis",
                        "Color": "stop",
                        "AsButton": True, 
                        "Function": None,
                        "Class":Summarize_Articles_Keywords
                    }
                }
            )

        from ..communicate_with_ai_about_research_progress import Communicate_with_AI_about_research_progress
        function_plugins.update(
                {
                    'step 3. ' + _("与AI交流研究进展"): {
                        "Group": "Scholar Navis",
                        "Color": "stop",
                        "AsButton": True, 
                        "Function": None,
                        "Class":Communicate_with_AI_about_research_progress
                    }
                }
            )
        
        from ..fine_grained_analysis_of_article import Fine_Grained_Analysis_of_Article
        function_plugins.update(
                {
                    'step 4. ' + _("精细分析文献"): {
                        "Group": "Scholar Navis",
                        "Color": "stop",
                        "AsButton": True, 
                        "Function": None,
                        "Class":Fine_Grained_Analysis_of_Article
                    }
                }
            )
        
        from ..pubmed_openaccess_articles_download import PubMed_Open_Access_Articles_Download
        function_plugins.update(
            {
                _("PubMed_OpenAccess文章获取"): {
                    "Group": "Scholar Navis",
                    "Color": "stop",
                    "AsButton": True, 
                    "Function": None,
                    "Class":PubMed_Open_Access_Articles_Download
                }
            }
        )
        
        
        # 开发时多语言翻译用
        if enable_translator:
            from .multi_language_translator import 多语言翻译器
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
    

