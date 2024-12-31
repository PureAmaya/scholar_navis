import os
from time import sleep
from shared_utils.scholar_navis.const_and_singleton import GPT_ACADEMIC_ROOT_PATH
from shared_utils.scholar_navis.user_custom_manager import DEFAULT_USER_CUSTOM,get_url_redirect,get_api_key
from request_llms.bridge_all import predict_no_ui_long_connection # 问就是这个不能脱离gpt_academic独自运行，我也不想对gpt_acadmic产生过多修改

# 使用poedit进行人工校验与格式修正，不保证其他的多语言编辑器可用
# 反正支持热重载，而且翻译完一般也就不用了，随便写写，能实现功能就行


# 这里是配置
lang_to_translate = '繁体中文'  # 需要翻译成的语言（告知LLM）
lang_to_translate_code = 'zh-Hant' # 目标语言代码 zh-Hant / zh-Hans / en-US
max = 10 # 每次翻译po的最大条数

model = 'custom-gpt-4o-mini' 
'''
所需模型
暂时只支持gpt_academic模型，后续会支持自定义模型
请在config_private.py中配置模型的api_key、url_redirect
'''


public_prompt = '''
You are good at translation. When translating, please use the same expression for identical statements, 
and directly tell me the translation without any additional content.
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
        self._get_msgstr()
        self._get_msgid()
            
    def _get_code_location(self):
        self._code_location = self.block.split('msgid')[0].strip()
    
    def _get_msgid(self):
        self._msgid = self.block.split('msgid')[1].split('msgstr')[0].strip()
        
    def _get_msgstr(self):
        self._msgstr = self.block.split('msgstr')[1].replace('"','').replace('\n','').strip()
        self._already_translated = bool(self._msgstr)
        if self._already_translated:self._msgstr = self.block.split('msgstr')[1].strip()  # 有翻译的话，就别动了，别再出问题了（带着开头结尾的引号）
        
    def translate(self):
        
        if not self._already_translated:
            
            _msgid = self._msgid.replace('"','').replace('\n','').strip()
            input = f'Please translate the following text into {lang_to_translate}. The text is below: {_msgid}'
            #try:
            a = predict_no_ui_long_connection(inputs=input,llm_kwargs=self.llm_kwargs,history=[],sys_prompt=public_prompt)
            self._msgstr = f'"{a.strip()}"'
            print(f'Translated: {_msgid} -> {self._msgstr}')
            #except Exception as e:
                #print(f'LLM access error, but it will try to continue. Error reason: {e}')
                #self._msgstr = '""'
            
            # 发生了翻译，返回一个true
            return  True
        else: return False
    
    def output(self):
        txt = f'\n{self._code_location}\nmsgid {self._msgid}\nmsgstr {self._msgstr}\n'
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
            sleep(0.02)
        translated_po = translated_po + block.output()
        

    # 有多少翻译完就写多少吧
    with open(po_fp,'w',encoding='utf-8') as f:
        f.write(translated_po)

    
def multi_language_translator():

    po_fp = os.path.join(GPT_ACADEMIC_ROOT_PATH,'i18n',lang_to_translate_code,'LC_MESSAGES','Scholar_Navis.po')
    if not os.path.exists(po_fp): os.makedirs(os.path.dirname(po_fp))

    
    def get_other_provider_api_key(provider_api_type:str):return get_api_key(DEFAULT_USER_CUSTOM,provider_api_type,True)
    
    llm_kwargs = {
            'api_key': get_api_key(DEFAULT_USER_CUSTOM,"API_KEY",True), 
            'llm_model': model,
            'top_p': 1,
            'max_length': 4096,
            'temperature':1,
            'client_ip': '',
            'most_recent_uploaded': '',
            'custom_api_key':get_other_provider_api_key, # 这里后面还需要用
            'custom_url_redirect':get_url_redirect('API_URL_REDIRECT',DEFAULT_USER_CUSTOM)
        }
    
    print('translating...')
    po_reader(po_fp,llm_kwargs)
    print(f'end. Please check the translated file. {po_fp}')
    
if __name__ == '__main__':
    multi_language_translator()

        
    