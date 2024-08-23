import os
import re
import yaml
import json
import PyPDF2
from request_llms.bridge_all import predict_no_ui_long_connection
from .article_library_ctrl  import pdf_yaml,SQLiteDatabase,db_type



def get_pdf_inf(pdf_path: str,allow_ai_assist : bool,llmkwargs = None):
    """获取论文的摘要、MD5、元数据标题、doi等信息
        此外，将获取的这些信息，外加文件名、关键词写入到pdf清单中（与pdf相同文件名）

    Args:
        pdf_path (str): 待提取的pdf路径
        allow_ai_assist (bool): 允许AI辅助获取标题和doi吗

    Returns:
        abstract: 摘要
        fp: pdf清单（md5.yml）的完整路径
    """
    # 摘取文件名
    filename, _1 = os.path.splitext(os.path.basename(pdf_path))

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
        with open(pdf_manifest_path,'r') as f:
            pdf_manifest_content_file = yaml.safe_load(f)
            
            # 对上面的初始值更新
            if not pdf_manifest_content_file is None:
                pdf_yaml_content.update({k: v for k, v in pdf_yaml_content.items() if v is not None})
        
    # 反正先读取一下pdf
    with open(pdf_path,'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        # 获取第一页
        first_page_text = pdf_reader.pages[0].extract_text()

        # 获取doi
        doi = ''
        if pdf_yaml_content[pdf_yaml.doi.value] is None  or pdf_yaml_content[pdf_yaml.doi.value] == 'None':
            doi :str = re.findall(r'10\.\d{4,}/.+', first_page_text)[0].strip()
            # 去除网址（e.g. nature的某些就有）
            doi = doi.split('www.')[0].strip()
            # 去除空格之后的多余信息（e.g.版权信息，网站信息等）
            doi = doi.split(' ',1)[0].strip()
            
        # 获取标题
        title = ''
        if pdf_yaml_content[pdf_yaml.title.value] is None or  pdf_yaml_content[pdf_yaml.title.value] == 'None':
            with SQLiteDatabase(db_type.article_doi_title) as db: 
                    title_tuple = db.select(doi,('title',))
                    if title_tuple is None: # 放心，如果数据库/数据不存在，返回的是None
                        # 数据库没有的话，就用元数据记录/文件名代替吧
                        meta_title = pdf_reader.metadata.title
                        title =  str(meta_title) if meta_title else os.path.basename(pdf_manifest_path)[:-4]
                        
                    else:# 数据库有记录
                        title = title_tuple[0]

        # 宁可错杀，不可放过。反正都想要AI辅助获取信息了，尽可能把信息弄全了
        if len(doi) < 10 or len(title) <= 20 or '..' in title:     
            # 不需要辅助，放行
            if not allow_ai_assist:pass
            # 需要辅助
            else:
                # 用AI获取到信息后，顺便存到数据库里，减少后续的获取量
                dict = ___get_inf_AI_assistant(first_page_text,llmkwargs)
                if dict:
                    title = dict['title'];doi=dict['doi']
                    with SQLiteDatabase(db_type.article_doi_title) as db:
                        db.insert_ingore(doi,('title','info'),(title,'attached by ai'))
            
        # 设定上doi和title
        pdf_yaml_content[pdf_yaml.doi.value] = doi
        pdf_yaml_content[pdf_yaml.title.value] = title

        # < ---------获取摘要-------------- >
        if pdf_yaml_content[pdf_yaml.abstract.value] is None or pdf_yaml_content[pdf_yaml.abstract.value] == 'None':
            
            # print(page_text)
            # 针对 PNAS 单独设计的代码（这东西就没有introduction和abstract）
            if re.search('www.pnas.org', first_page_text):
                # 摘要前
                PNAS_front_pattern = r'.*(?:Contributed|Edited) by.*?\n'
                # print(re.findall(PNAS_front_pattern, page_text,re.DOTALL)[0])
                first_page_text = re.sub(PNAS_front_pattern, '',
                                first_page_text, flags=re.DOTALL)
                # 摘要后
                PNAS_back_pattern = r'\|.*?\|.*'
                # 如果后面那些文本真的删不了，那就尽可能地去除一些内容吧
                if re.findall(PNAS_back_pattern, first_page_text, re.DOTALL) == []:
                    PNAS_back_pattern = r'\([0-9]\).*'
                # print(re.findall(PNAS_back_pattern, page_text,re.DOTALL)[0])
                first_page_text = re.sub(PNAS_back_pattern, '',
                                first_page_text, flags=re.DOTALL)

                # 去掉最后一个句号（period）之后的内容
                last_period_index = first_page_text.rfind('.')
                if last_period_index > 0:
                    first_page_text = first_page_text[:last_period_index + 1]  # +1；把句号留着

                # print(page_text)

            # 其他正常一点的文章，abstract/summary和introduction至少得有一个吧。通用的
            else:

                # 如果有abstract / summary，删除及其之前的内容  the plant journal用的是summary而不是abstract
                summary_pattern = r'.*(?:[Ss]ummary|SUMMARY|ABSTRACT|[Aa]bstract)'
                # print(re.findall(summary_pattern, page_text,re.DOTALL)[0])
                first_page_text = re.sub(summary_pattern, '', first_page_text, flags=re.DOTALL)

                # 删除introduction及其之后的内容
                # 不知道为什么加上大小写判定之后就炸了
                introduction_pattern = r'[Ii](?:ntroduction|NTRODUCTION).*'
                # print(re.findall(introduction_pattern,page_text,re.DOTALL)[0])
                first_page_text = re.sub(introduction_pattern, '',
                                first_page_text, flags=re.DOTALL)

                # 删除key words及其之后的内容
                keywords_pattern = r'\n[Kk](?:eywords|ey words|EYWORDS|EY WORDS).*'
                # print(re.findall(keywords_pattern,page_text,re.DOTALL)[0])
                first_page_text = re.sub(keywords_pattern, '',
                                first_page_text, flags=re.DOTALL)

                # 删除版权信息
                copyright_pattern = r'\.\n.*http://creativecommons.org/licenses/by-nc-nd/4.0/.*'
                # print(re.findall(copyright_pattern,page_text,re.DOTALL)[0])
                first_page_text = re.sub(copyright_pattern, '',
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
                reference_pattern = r'et al.*?\).*'
                # print(re.findall(reference_pattern,page_text,re.DOTALL)[0])
                first_page_text = re.sub(reference_pattern, '',
                                first_page_text, flags=re.DOTALL)

            # 去除多余的换行符
            pdf_yaml_content[pdf_yaml.abstract.value] = first_page_text.replace('\n', '')
            # print(abstract)


    # 保存pdf的yaml
    with open(pdf_manifest_path,'w') as f:
        f.write(yaml.safe_dump(pdf_yaml_content))

    # 返回摘要和创建的manifest路径
    return pdf_yaml_content[pdf_yaml.abstract.value], pdf_manifest_path

def ___get_inf_AI_assistant(pdf_first_page: str,llm_kwargs):
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
        match = '{' + a.split('{')[1].split('}')[0] + '}'
        dict = json.loads(match)
        dict['title'] = dict['title'].strip()
        doi:str = dict['doi'].strip() # 这两行是故意的，如果报错，就能排除一些其他不可见的问题
        
        if 'doi.org/' in doi: dict['doi'] = doi.split('doi.org/',1)[1]
        return dict
        
    except:
        return None
    