'''
Author: scholar_navis@PureAmaya
'''

import os
import re
import yaml
import json
import pymupdf
from urllib.parse import quote
from request_llms.bridge_all import predict_no_ui_long_connection
from shared_utils.scholar_navis.sqlite import SQLiteDatabase
from crazy_functions.scholar_navis.scripts.tools.article_library_ctrl import pdf_yaml
from shared_utils.scholar_navis.other_tools import fix_problematic_text


def get_pdf_content(lang,pdf_path,page_range: tuple | int,allow_ai_assist,llmkwargs = None):
    if allow_ai_assist and llmkwargs is None:
        raise RuntimeError('AI-assisted features must provide LLM model parameters.')

    if isinstance(page_range,int):page_range = (page_range,page_range)
    
    # 确保页码范围合法
    if page_range[0] < 0 or page_range[1] < page_range[0]:
        raise ValueError("Invalid page range specified.")

    pdf_reader = pymupdf.open(pdf_path)
    
    if not _check_accessible(pdf_reader):raise RuntimeError("PDF is not accessible.")
    
    txt = ''
    doi,title = _get_pdf_doi_and_title(pdf_reader,default_doi='',
                                            default_title=os.path.basename(pdf_path)[:-4])
    
    # 宁可错杀，不可放过。反正都想要AI辅助获取信息了，尽可能把信息弄全了
    if len(doi) < 10 or len(title) <= 40 or '..' in title:     
        # 不需要辅助，放行
        if not allow_ai_assist:pass
        # 需要辅助
        else:
            # 用AI获取到信息后，顺便存到数据库里，减少后续的获取量
            dict = _get_inf_AI_assistant(pdf_reader.load_page(0).get_textpage().extractText(),llmkwargs)
            if dict:
                title = dict['title'];doi=dict['doi']
                with SQLiteDatabase('article_doi_title') as db:
                    db.insert_ingore(doi,('title','info'),(title,'attached by ai'))
    
    for i in range(page_range[0],page_range[1] + 1):
        txt += pdf_reader.load_page(i).get_textpage().extractText()
    return doi,title,txt
    
    
def get_pdf_inf(pdf_path: str,allow_ai_assist : bool,llmkwargs = None):
    """
    获取论文的摘要、元数据标题、doi等信息
        此外，将获取的这些信息，外加文件名、关键词写入到pdf清单中（与pdf相同文件名）

    Args:
        pdf_path (str): 待提取的pdf路径
        allow_ai_assist (bool): 允许AI辅助获取标题和doi吗
        llmkwargs (dict, optional): AI辅助时用到的模型参数. Defaults to None.

    Returns:
        accessible (bool): 能否使用（通常都可以，但是中文学位论文、加密文件、非PDF文件或损坏文件不行）
        abstract (str): 摘要.
        fp (str): pdf清单（md5.yml）的完整路径.

    """
    
    if allow_ai_assist and llmkwargs is None:
        raise RuntimeError('AI-assisted features must provide LLM model parameters.')
    
    # 摘取文件名和拓展名
    filename, extension = os.path.splitext(os.path.basename(pdf_path))

    # < ---------yaml信息-------------- >
    
    # 如果没有，则创建yaml的默认值（这是个字典），
    pdf_yaml_content = {
        pdf_yaml.filename.value: filename,
        pdf_yaml.title.value: None,# 可能为None
        pdf_yaml.abstract.value: None,# 可能为None
        pdf_yaml.doi.value:None
    }
    
    # pdf_yaml的完整路径
    pdf_manifest_path = os.path.join(os.path.dirname(pdf_path), filename + ".yml")
    
    # （如果有）读取此前有yaml，读一下
    if os.path.exists(pdf_manifest_path):
        with open(pdf_manifest_path,'r',encoding='utf-8') as f:
            pdf_manifest_content_file = yaml.safe_load(f)
            
            # 对上面的初始值更新
            if not pdf_manifest_content_file is None:
                pdf_yaml_content.update({k: v for k, v in pdf_yaml_content.items() if v is not None})
        
    # 反正先读取一下pdf
    if extension.lower() != '.pdf':
        return False, None, None  # 不是PDF，直接返回

    try:
        pdf_reader = pymupdf.open(pdf_path)
        first_page_text = pdf_reader.load_page(0).get_textpage().extractText()
    except Exception as e:
        # 处理打开失败的情况（如加密PDF等）
        print(f"读取PDF失败: {str(e)}")
        return False, None, None

    # 可用性检查
    if not _check_accessible(pdf_reader):
        return False, None, None  # 不能用，后面不管了

    # 获取doi和title
    doi ,title =_get_pdf_doi_and_title(pdf_reader,default_doi='', default_title=os.path.basename(pdf_manifest_path)[:-4])
                    
    # 宁可错杀，不可放过。反正都想要AI辅助获取信息了，尽可能把信息弄全了
    if len(doi) < 10 or len(title) <= 40 or '..' in title:     
        # 不需要辅助，放行
        if not allow_ai_assist:pass
        # 需要辅助
        else:
            # 用AI获取到信息后，顺便存到数据库里，减少后续的获取量
            dict = _get_inf_AI_assistant(first_page_text,llmkwargs)
            if dict:
                title = dict['title'];doi=dict['doi']
                with SQLiteDatabase('article_doi_title') as db:
                    db.insert_ingore(doi,('title','info'),(title,'attached by ai'))
        
    # 设定上doi和title
    pdf_yaml_content[pdf_yaml.doi.value] = doi
    pdf_yaml_content[pdf_yaml.title.value] = title

    # < ---------获取摘要-------------- >
    if pdf_yaml_content[pdf_yaml.abstract.value] is None or pdf_yaml_content[pdf_yaml.abstract.value] == 'None':
        
        # 去除多余换行符
        first_page_text = first_page_text.replace('\n','')
        
        # print(page_text)
        # 针对 PNAS 单独设计的代码（这东西就没有introduction和abstract）
        if re.search('www.pnas.org', first_page_text):
            # 摘要前
            pattern = r'.*(?:Contributed|Edited) by.*?\n'
            # print(re.findall(PNAS_front_pattern, page_text,re.DOTALL)[0])
            first_page_text = re.sub(pattern, '',
                            first_page_text, flags=re.DOTALL)
            # 摘要后
            pattern = r'\|.*?\|.*'
            # 如果后面那些文本真的删不了，那就尽可能地去除一些内容吧
            if re.findall(pattern, first_page_text, re.DOTALL) == []:
                pattern = r'\([0-9]\).*'
            # print(re.findall(PNAS_back_pattern, page_text,re.DOTALL)[0])
            first_page_text = re.sub(pattern, '',
                            first_page_text, flags=re.DOTALL)

            # 去掉最后一个句号（period）之后的内容
            last_period_index = first_page_text.rfind('.')
            if last_period_index > 0:
                first_page_text = first_page_text[:last_period_index + 1]  # +1；把句号留着

            # print(page_text)

        # 其他正常一点的文章，abstract/summary和introduction至少得有一个吧。通用的
        else:

            # 如果有abstract / summary，删除及其之前的内容  the plant journal用的是summary而不是abstract
            pattern = r'.*(?:[Ss]ummary|SUMMARY|ABSTRACT|[Aa]bstract)'
            # print(re.findall(summary_pattern, page_text,re.DOTALL)[0])
            first_page_text = re.sub(pattern, '', first_page_text, flags=re.DOTALL)

            # 删除introduction及其之后的内容
            # 不知道为什么加上大小写判定之后就炸了
            pattern = r'[Ii](?:ntroduction|NTRODUCTION).*'
            # print(re.findall(introduction_pattern,page_text,re.DOTALL)[0])
            first_page_text = re.sub(pattern, '',
                            first_page_text, flags=re.DOTALL)

            # 删除key words及其之后的内容
            pattern = r'\n[Kk](?:eywords|ey words|EYWORDS|EY WORDS).*'
            # print(re.findall(keywords_pattern,page_text,re.DOTALL)[0])
            first_page_text = re.sub(pattern, '',
                            first_page_text, flags=re.DOTALL)

            # 删除版权信息
            pattern = r'\.\n.*http://creativecommons.org/licenses/by-nc-nd/4.0/.*'
            # print(re.findall(copyright_pattern,page_text,re.DOTALL)[0])
            first_page_text = re.sub(pattern, '',
                            first_page_text, flags=re.DOTALL)

            # 删除DOI
            # doi_pattern = r'[Dd][Oo][Ii]:.*'
            # print(re.findall(doi_pattern,page_text,re.DOTALL)[0])
            # page_text = re.sub(doi_pattern,'',page_text,flags=re.DOTALL)

            # 删除Citation（PLOS那种东西，在摘要下面有很多怪的东西）
            # citation_pattern = r'[Cc]itation:.*'
            # print(re.findall(citation_pattern,page_text,re.DOTALL)[0])
            # page_text = re.sub(citation_pattern,'',page_text,flags=re.DOTALL)

            # 如果有参考文献的那个字样，删除及其之后的内容（顺便还可以删除参考文献所在的这一句）
            pattern = r'et al.*?\).*'
            # print(re.findall(reference_pattern,page_text,re.DOTALL)[0])
            first_page_text = re.sub(pattern, '',
                            first_page_text, flags=re.DOTALL)

        # 去除多余的换行符
        pdf_yaml_content[pdf_yaml.abstract.value] = first_page_text.replace('\n', '')
        # print(abstract)

    # 保存pdf的yaml
    with open(pdf_manifest_path,'w',encoding='utf-8') as f:
        f.write(yaml.safe_dump(pdf_yaml_content))

    # 返回摘要和创建的manifest路径
    return True,pdf_yaml_content[pdf_yaml.abstract.value], pdf_manifest_path


def _check_accessible(document:pymupdf.Document):
    if not isinstance(document,pymupdf.Document):raise ValueError('document must be pymupdf.Document')
    
    accessible = True # 以后可能会添加更多的检查可用性逻辑，所以先单独拿出来吧
    
    # 不分析中文的学位论文（太长啦）
    pattern = r'学位论文|单位代码'
    first_page_text = document.load_page(0).get_textpage().extractText()
    if re.search(pattern, first_page_text):
        accessible = False
    
    return accessible

def _get_pdf_doi_and_title(document:pymupdf.Document,default_doi:str='',default_title:str=''):
    """获取pdf的标题和doi号，如果获取失败，则返回默认值

    Args:
        document (pymupdf.Document): 加载的PDF
        default_doi (str, optional): _description_. Defaults to ''.
        default_title (str, optional): _description_. Defaults to ''.

    Returns:
        tuple: doi,title
    """
    doi = '';title=''

    first_page_text = document.load_page(0).get_textpage().extractText()
    try:
        doi :str = re.findall(r'10\.\d{4,}/.+', first_page_text)[0].strip()
        # 去除网址（e.g. nature的某些就有）
        doi = doi.split('www.')[0].strip()
        # 去除空格之后的多余信息（e.g.版权信息，网站信息等）
        doi = doi.split(' ',1)[0].strip()
        # 去除可能有的空格
        doi = doi.replace(' ','').strip()
    except:doi=default_doi
    
    try:
        with SQLiteDatabase('article_doi_title') as db: 
            title_tuple = db.easy_select(doi,'title')
            if not title_tuple: # 放心，如果数据库/数据不存在，返回的是None
                # 数据库没有的话，就用元数据记录/文件名代替吧
                meta_title = document.metadata.get('title')
                title =  str(meta_title) if meta_title else default_title#  
            else:# 数据库有记录
                title = title_tuple[0]
    except:title = default_title

    return quote(doi,encoding="utf-8"),fix_problematic_text(title)

def _get_inf_AI_assistant(pdf_first_page: str,llm_kwargs):
    """使用AI辅助获取标题和doi号
        如果不是可用的json/dict，返回None
        如果获取失败，也返回None

    Args:
        pdf_first_page (str): 文章的第一页全文（通常来说第一页就有了）
        llm_kwargs (_type_): 传递大语言参数

    Returns:
        dict: title 与 doi
    """
    
    
    promot = '''
    I'm gonna give you a string of text, 
    and it's the first page of a scholarly article. 
    Please grab its title and DOI number, 
    and let me know in JSON format, like so: 
    {"title": the title you find, "doi": the DOI number you find}. 
    The DOI should start with "10.".
    And make sure to use the language that the article is written in.
    '''

    try:
        a = predict_no_ui_long_connection(inputs=pdf_first_page,llm_kwargs=llm_kwargs,history=[],sys_prompt=promot)
        # 获取json内容
        match_ = '{' + a.split('{')[1].split('}')[0] + '}'
        dict_ = json.loads(match_)
        dict_['title'] = dict_['title'].strip()
        doi:str = dict_['doi'].strip() # 这两行是故意的，如果报错，就能排除一些其他不可见的问题
        
        if 'doi.org/' in doi: dict_['doi'] = doi.split('doi.org/',1)[1]
        if not doi.strip().startswith('10.'): return None
        return dict_
        
    except:
        return None
    