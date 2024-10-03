import os
from toolbox import CatchException
from shared_utils.const import SCHOLAR_NAVIS_ROOT_PATH
from shared_utils.sn_config import SUPPORT_DISPLAY_LANGUAGE
from request_llms.bridge_all import predict_no_ui_long_connection # 问就是这个不能脱离gpt_academic独自运行，我也不想对gpt_acadmic产生过多修改

# ! 专供本软件的翻译，不能保证其他软件翻译可用
# 反正支持热重载，而且翻译完一般也就不用了，随便写写，能实现功能就行

lang_to_translate_natural = 'English'
lang_to_translate = 'en-US'
max = 10


public_prompt = '''
You are good at translation. When translating, please use the same expression for identical statements.
If there are any special symbols, please retain them unchanged.
You should translate follow these:
[文章] [Article]
[搜搜内容] [Query]
文献总结库   article summarization library
总结文件 summarization file
精细分析文献  Fine-grained Analysis of Article
访问文章发布页  Article Publisher Page
复制文章  Copy Article
下载文章 Download
缓存pdf文献   Cache PDF Articles
按关键词总结文献   Summarize Articles by Keywords
与AI交流研究进展    Communicate with AI about research progress
PubMed_OpenAccess文章获取   PubMed Open Access Articles Download
'''

class _po_formator:
    def __init__(self,po_block:str,llm_kwargs) -> None:
        self.block = po_block
        self.llm_kwargs = llm_kwargs
        self._get_code_location()
        self._get_msgid()
        self._get_msgstr()
            
    def _get_code_location(self):
        self._code_location = self.block.split('msgid')[0].strip()
    
    def _get_msgid(self):
        self._msgid = self.block.split('msgid')[1].split('msgstr')[0].replace('"','').replace('\n','').strip()
    
    def _get_msgstr(self):
        self._msgstr = self.block.split('msgstr')[1].replace('"','').replace('\n','').strip()
        
    def translate(self):
        
        if not self._msgstr:
            
            input = f'Please translate the following text into {lang_to_translate_natural}, and directly tell me the translation without any additional content.The text is below: {self._msgid}'
            try:
                a = predict_no_ui_long_connection(inputs=input,llm_kwargs=self.llm_kwargs,history=[],sys_prompt=public_prompt)
                self._msgstr = a.strip()
            except Exception as e:
                #raise RuntimeError(f'LLM access error. Error reason: {e}')
                pass
            
            # 发生了翻译，返回一个true
            return True
        else: return False
    
    def output(self):
        txt = f'\n{self._code_location}\nmsgid "{self._msgid}"\nmsgstr "{self._msgstr}"\n'
        return txt
    
def po_reader(po_fp,llm_kwargs):
    with open(po_fp,'r',encoding='utf-8') as f:
        all = f.read().split('\n\n')
        
    translated_po = all[0].strip()
    blocks : list[_po_formator]= []
    
    for block in all[1:]:
        blocks.append(_po_formator(block,llm_kwargs))
        
    count  = 0
    for block in blocks:
        if count <= max:
            if block.translate():count += 1
        translated_po = translated_po + block.output()
        

    # 有多少翻译完就写多少吧
    with open(po_fp,'w',encoding='utf-8') as f:
        f.write(translated_po)

    
@CatchException
def 多语言翻译器(txt: str, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):

    po_fp = os.path.join(SCHOLAR_NAVIS_ROOT_PATH,'i18n',lang_to_translate,'LC_MESSAGES','Scholar_Navis.po')
    if not os.path.exists(po_fp): os.makedirs(os.path.dirname(po_fp))
    
    print('translating...')
    print('')
    po_reader(po_fp,llm_kwargs)
    print('')
    print('end')

        
    