'''
Author: scholar_navis@PureAmaya
'''

import os
import csv
import json
import shutil
import gradio as gr
from threading import Lock
from zipfile import ZipFile
from rarfile import RarFile
from time import time,sleep
from pandas import read_excel
from datetime import datetime
from typing import Literal
from ...crazy_utils import get_files_from_everything
from concurrent.futures import ThreadPoolExecutor
from shared_utils.scholar_navis.multi_lang import _
from shared_utils.scholar_navis.pdf_reader import get_pdf_content
from request_llms.bridge_all import predict_no_ui_long_connection 
from shared_utils.scholar_navis.other_tools import generate_random_string
from shared_utils.scholar_navis.user_custom_manager import get_url_redirect,get_api_key
from shared_utils.scholar_navis.const_and_singleton import VERSION


ARTICLE_CSV_FILENAME = 'articles_content.csv'
PARAMETER_JSON_FILENAME = 'parameter.json'
USEFUL_SENTENCES_JSON_FILENAME = 'useful_original_text.json'
ACCEPTABLE_SENTENCES_JSON_FILENAME = 'acceptable_original_text.json'
RESULT_JSON_FILENAME ='result.json'
RESULT_CSV_FILENAME ='result.csv'
LOG_FILENAME = 'task.log'
lock = Lock()

class for_gradio:
    
    @staticmethod
    def update_task_name(request: gr.Request,cookies,task_name:str):
        """ 更新任务名称

        Returns:
            cookies(记录在work_path中)
        """
        if not task_name.strip():
            task_name = 'default_extraction_task'
        task_name = task_name.strip() + '_' + generate_random_string(12)
        username =  request.username if request.username else 'default_user'
        target_work_dir = os.path.join('gpt_log',username,'scholar_navis_useful_sentences',task_name)
        # 记录任务参数
        if not cookies:cookies = {}
        cookies.update({'extract_sentences_work_path':target_work_dir})
        return cookies
    
    
    @staticmethod
    def create_or_load(request: gr.Request,cookies,create_or_load_task: str,task_name:str):
        """创建或上传新的项目时更新gr

        Returns:
            cookies,sturcture_requirements,content_requirements,target_language
        """
        # 更新一下任务名称
        cookies = for_gradio.update_task_name(request,cookies,task_name)
        
        # 根据参数配置文件更新参数（不含AI相关参数）
        parameter_dict:dict = {}
        if create_or_load_task and create_or_load_task.lower().endswith('.zip'):
            with ZipFile(create_or_load_task) as zf:
                file_list = zf.namelist()
                for file in file_list:
                    if file== PARAMETER_JSON_FILENAME:
                        with zf.open(file) as f:
                            parameter_dict:dict = json.loads(f.read().decode('utf-8'))
        elif create_or_load_task and create_or_load_task.lower().endswith('.rar'):
            with RarFile(create_or_load_task) as rf:
                file_list = rf.namelist()
                for file in file_list:
                    if file== PARAMETER_JSON_FILENAME:
                        with rf.open(file) as f:
                            parameter_dict:dict = json.loads(f.read().decode('utf-8'))
        
        sturcture_requirements = parameter_dict.get('sturcture_requirements','')
        content_requirements = parameter_dict.get('content_requirements','')
        target_language = parameter_dict.get('target_language','')
        
        return cookies,sturcture_requirements,content_requirements,target_language
        
    
    @staticmethod
    def para_disable_user_edition(sturcture_requirements,content_requirements,target_language):
            classification_updater = gr.update(value = sturcture_requirements, interactive= not bool(sturcture_requirements.strip()))
            con_updater = gr.update(value = content_requirements, interactive= not bool(content_requirements.strip()))
            lang_updater = gr.update(value = target_language, interactive= not bool(target_language.strip()))
            return classification_updater,con_updater,lang_updater

    @staticmethod
    def llm_kwargs_combiner(request: gr.Request, cookies,md_dropdown,top_p,temperature,user_custom_data):
            # 获取openai用的api
        api_key = get_api_key(user_custom_data,"API_KEY",True)
        url_redirect = get_url_redirect('API_URL_REDIRECT',user_custom_data)
        
        # 方便获取其他供应商的api_key
        def get_other_provider_api_key(provider_api_type:str):return get_api_key(user_custom_data,provider_api_type,True)
        
        if md_dropdown.startswith('custom-'):
            # 自定义模型使用openai兼容方案，覆盖一些openai的设定
            api_key = get_api_key(user_custom_data,"CUSTOM_API_KEY")
            url_redirect = get_url_redirect('CUSTOM_REDIRECT',user_custom_data)
        
        
        llm_kwargs = {
            'api_key': api_key if api_key else cookies['api_key'], 
            'llm_model': md_dropdown,
            'top_p': top_p,
            'max_length': 40960,
            'temperature': temperature,
            'client_ip': request.client.host,
            'most_recent_uploaded': '',
            'custom_api_key':get_other_provider_api_key, 
            'custom_url_redirect':url_redirect
        }
        
        return llm_kwargs

    @staticmethod
    def create_or_load_task(request: gr.Request,cookies,task_name,create_or_load_task_path):
        """ 当上传旧的任务或者创建新的任务时，使用它

        Returns:
            _cookies,sturcture_requirements,content_requirements,target_language,below_accordion_updater
        """
        if not cookies:cookies = {}
        
        # 加载上传的文件
        new_cookies,sturcture_requirements,content_requirements,target_language = for_gradio.create_or_load(request,cookies,create_or_load_task_path,task_name)
        # 调整参数可编辑性
        sturcture_requirements,content_requirements,target_language = for_gradio.para_disable_user_edition(sturcture_requirements,content_requirements,target_language)
        # 显示后续内容
        below_accordion_updater = gr.update(visible=True)
        # 更新cookies
        cookies.update(new_cookies)
        return  cookies,sturcture_requirements,content_requirements,target_language,below_accordion_updater
    
    @staticmethod
    def reset(cookie,md_dropdown,user_custom_data):
        if not cookie:
            cookie = {}
        cookie.pop('extract_sentences_already_run',None)
        cookie.pop('extract_sentences_work_path',None)
        cookie.update({'api_key':get_api_key(user_custom_data,"API_KEY",True)})
        cookie.update({'llm_model':md_dropdown}) # 防止不知道为什么以外的cookies重置
        
        exec_btn_updater = gr.update(visible=True)
        cancel_btn  = gr.update(visible=False)
        below_accordion = gr.update(visible=False)
        content_classification = gr.update(value='',interactive=True)
        content_requirements = gr.update(value='',interactive=True)
        language = gr.update(value='简体中文',interactive=True)
        task_name  = gr.update(value='',interactive=True)
        create_or_load_task = gr.update(value=None)
        upload_extra_pdf = gr.update(value=None)
        all_files_dl_updater = gr.update(value=None,visible=False)
        result_file_dl_updater = gr.update(value=None,visible=False)
        log = gr.update(value='')
        return cookie,exec_btn_updater,cancel_btn,below_accordion,content_classification,content_requirements,language,task_name,create_or_load_task,upload_extra_pdf,all_files_dl_updater,result_file_dl_updater,log

    @staticmethod
    def before_start_task(cookies,content_classification,content_requirements,lang):
        """运行前进行一些检查。成功了再运行

        Returns:
            成功的话会返回cookies，失败的话会抛出异常
        """
        if not cookies or cookies.get('extract_sentences_already_run',False):
            raise gr.Error(_('请重置后再执行'),duration=5)
        
        if not 'extract_sentences_work_path' in cookies:
            raise gr.Error(_('任务名称意外丢失，请重新设定'),duration=5)
        
        
        if not content_classification.strip() or not content_requirements.strip():
            raise gr.Error(_('结构和内容要求不能为空'),duration=5)
        
        if not lang.strip():
            raise gr.Error(_('目标语言不能为空。请选定目标语言'),duration=5)
        
        work_path = cookies['extract_sentences_work_path']
        try:
            os.makedirs(work_path)
        except Exception as e:
            raise gr.Error(_('工作目录处理失败，请重新设定{}').format(f'{e}'),duration=5)
        
        cookies.update({'extract_sentences_already_run':True})
        
        # 调整UI
        exec_btn_updater = gr.update(visible=False)
        cancel_btn_updater = gr.update(visible=True)
        
        return cookies,exec_btn_updater,cancel_btn_updater

    @staticmethod
    def execute_task(request: gr.Request,cookies:dict,md_dropdown,top_p,temperature,log,user_custom_data,create_or_load_task,upload_extra_pdf,target_language,content_classification,content_requirements,max_workers):
        """ 执行任务

        Yields:
            log日志
        """
        
        gr.Info(_('任务开始执行'),duration=5)

        llm_kwargs = for_gradio.llm_kwargs_combiner(request,cookies,md_dropdown,top_p,temperature,user_custom_data)
        
        task_worker = worker(cookies,log,llm_kwargs,create_or_load_task,upload_extra_pdf,content_requirements,content_classification,target_language,max_workers)
        
        # 开始执行与结果输出
        for log in task_worker.deploy():
            yield log,gr.update(),gr.update()

        # 运行完成，输出结果F
        for log in task_worker.output():
            yield log,gr.update(),gr.update()
            
        # 激活下载按钮
        msg = '''
            <strong>{}</strong>
            <p>{}</p>
        '''
        
        gr.Info(msg.format(_('任务执行完成'),_('如果要执行新的任务，请重置')),duration=10)
        
        result_fp = worker.generate_download_file(cookies,'only_result')
        all_fp = worker.generate_download_file(cookies,'all_files')
        
        all_files_dl_updater = gr.update(value=all_fp,visible=True)
        result_file_dl_updater = gr.update(value=result_fp,visible=True)

        yield  log,all_files_dl_updater,result_file_dl_updater
    
class worker:
    @staticmethod
    def _title_splice_in_log(title:str):
        return f'{title[:50]}...' if len(title) > 50 else title # 用于输出处理过程
    
    @staticmethod
    def get_all_essential_files(work_path):
        essential_files = []
        articles_csv_fp = os.path.join(work_path,ARTICLE_CSV_FILENAME);essential_files.append(articles_csv_fp)
        useful_sentences_json_fp = os.path.join(work_path,USEFUL_SENTENCES_JSON_FILENAME);essential_files.append(useful_sentences_json_fp)
        '''初步甄选出可用的原句，不发生修改（尽可能）'''
        extract_acceptable_sentences_json_fp = os.path.join(work_path,ACCEPTABLE_SENTENCES_JSON_FILENAME);essential_files.append(extract_acceptable_sentences_json_fp)
        '''进一步整理出每一篇文章的有用句子（原文，尽可能不修改）'''
        result_json_fp = os.path.join(work_path,RESULT_JSON_FILENAME);essential_files.append(result_json_fp)
        '''最终的成果(json格式，便于程序读写)'''
        result_csv_fp = os.path.join(work_path,RESULT_CSV_FILENAME);essential_files.append(result_csv_fp)
        '''最终的成果(csv格式，提供给用户)'''
        log_fp = os.path.join(work_path,LOG_FILENAME);essential_files.append(log_fp)
        parameter_json_fp = os.path.join(work_path,PARAMETER_JSON_FILENAME);essential_files.append(parameter_json_fp)
        return essential_files

    @staticmethod
    def generate_download_file(cookies,type:Literal['only_result','all_files']):
        """根据cookies生成需要下载的文件的路径

        Returns:
            str: 需要下载文件的路径
        """
        
        work_path = cookies.get('extract_sentences_work_path','')
        
        if not os.path.isdir(work_path) or not work_path:
            return ''
        
        if type=='only_result':
            file_path = os.path.join(work_path,RESULT_CSV_FILENAME)
        else:
            file_path = os.path.join(work_path,'extract_sentences.zip')
            if not os.path.exists(file_path):
                files_to_compress = worker.get_all_essential_files(work_path)
                
                with ZipFile(file_path,'w') as f:
                    for file in files_to_compress:
                        if os.path.exists(file):
                            f.write(file,os.path.basename(file))
        if not os.path.isfile(file_path):
            raise gr.Error(_('要下载的文件不存在。请尝试下载另一个文件或重新摘取'),duration=5)
        
        return file_path
    
    def __init__(self,cookies,logger,llm_kwargs,create_or_load_task,add_extra_pdf, content_requirements,content_classification:str,target_language,max_workers):
        self.work_path = cookies.get('extract_sentences_work_path') # 这样子的话，再修改任务名就没用了233
        tmp_dir = os.path.join(self.work_path,'tmp');os.makedirs(tmp_dir,exist_ok=True)
        self._logger = logger
        self.lifespan = 3
        
        #### 获取必要路径 ######
        
        essential_files = worker.get_all_essential_files(self.work_path)
        self._articles_csv_fp = essential_files[0]
        self._useful_sentences_json_fp = essential_files[1]
        self._extract_acceptable_sentences_json_fp = essential_files[2]
        self._result_json_fp = essential_files[3]
        self._result_csv_fp = essential_files[4]
        self._log_fp = essential_files[5]
        self._parameter_json_fp = essential_files[6]

        ###### 先把用户上传的文件存放在临时目录 #$###########
        if not create_or_load_task or not os.path.isfile(create_or_load_task):
            raise gr.Error(_('文件不存在。请上传文件或选择已有文件'))
        
        if create_or_load_task.lower().endswith('.zip'):
            with ZipFile(create_or_load_task) as zf:
                file_list = zf.namelist()
                missing_but_pdf_exist = False
                for essential_file in essential_files:
                    if not os.path.basename(essential_file) == LOG_FILENAME and os.path.basename(essential_file) not in file_list:
                        for file in file_list:
                            if file.lower().endswith('.pdf'):
                                missing_but_pdf_exist = True
                                gr.Warning(_('压缩包中缺少必要文件 {}，但是有pdf文件，将按照新任务执行。如果您的压缩包内只有pdf，请忽略该提醒').format(os.path.basename(essential_file)))
                                break
                        if missing_but_pdf_exist:break
                        raise gr.Error(_('压缩包中缺少必要文件 {}，请重新上传或选择已有文件').format(os.path.basename(essential_file)))
                zf.extractall(tmp_dir)
        
        elif create_or_load_task.lower().endswith('.rar'):
            with RarFile(create_or_load_task) as rf:
                file_list = rf.namelist()
                missing_but_pdf_exist = False
                for essential_file in essential_files:
                    if not os.path.basename(essential_file) == LOG_FILENAME and os.path.basename(essential_file) not in file_list:
                        for file in file_list:
                            if file.lower().endswith('.pdf'):
                                missing_but_pdf_exist = True
                                gr.Warning(_('压缩包中缺少必要文件 {}，但是有pdf文件，将按照新任务执行。如果您的压缩包内只有pdf，请忽略该提醒').format(os.path.basename(essential_file)))
                                break
                        if missing_but_pdf_exist:break
                        raise gr.Error(_('压缩包中缺少必要文件 {}，请重新上传或选择已有文件').format(os.path.basename(essential_file)))
                rf.extractall(tmp_dir)
        else:
            # 部分文件更改成统一的文件名
            if create_or_load_task.lower().endswith(('.csv','.xls','.xlsx')):
                filename = ARTICLE_CSV_FILENAME.split('.')[0]+os.path.splitext(create_or_load_task)[1]
            else:filename = os.path.basename(create_or_load_task) #pdf没有必要
            shutil.copy(create_or_load_task,os.path.join(tmp_dir,filename)) 
        
        ###### 把临时文件收拾一下，放到工作目录下 ############
        for file in essential_files:
            file_in_tmp = os.path.join(tmp_dir,os.path.basename(file))
            if os.path.exists(file_in_tmp):shutil.move(file_in_tmp,file)
        shutil.move(tmp_dir,os.path.join(self.work_path,'pdf')) # 省的移动了
        
        ###### 处理额外的pdf #######
        # 上传的格式：'.zip','.pdf'
        if add_extra_pdf:
            for file in add_extra_pdf:
                if file.endswith('.zip'):
                    with ZipFile(file) as zf:
                        zf.extractall(os.path.join(self.work_path,'pdf'))
                elif file.endswith('.rar'):
                    with RarFile(file) as rf:
                        rf.extractall(os.path.join(self.work_path,'pdf'))
                else:shutil.copy(file,os.path.join(self.work_path,'pdf',os.path.basename(file))) 
        
        ##### excel 转 csv  ######
        xls = os.path.join(self.work_path,ARTICLE_CSV_FILENAME.split('.')[0]+'.xls')
        xlsx = os.path.join(self.work_path,ARTICLE_CSV_FILENAME.split('.')[0]+'.xlsx')
        if os.path.exists(xls):excel_path = xls
        elif os.path.exists(xlsx):excel_path = xlsx
        else:excel_path = None
        
        if excel_path:
            try: # 如果是正经的excel文件，就转csv
                dfs = read_excel(excel_path,sheet_name=None)
                dfs[0].to_csv(self._articles_csv_fp,index=False,encoding='utf-8')
            except: # 如果是奇怪的excel文件，就直接读csv
                shutil.move(excel_path,self._articles_csv_fp)
        
        #### 读取已经有的文件 ####
        self._articles = {}
        if os.path.exists(self._articles_csv_fp):
            with open(self._articles_csv_fp,'r',encoding='utf-8') as f:
                reader = csv.reader(f)
                for line in reader:
                    self._articles.update({line[0]:line[1]})
        
        self._useful_sentences_json = {}
        if os.path.exists(self._useful_sentences_json_fp):
            with open(self._useful_sentences_json_fp,'r',encoding='utf-8') as f:
                self._useful_sentences_json = json.loads(f.read())
        
        self._extract_acceptable_sentences_json = {}
        if os.path.exists(self._extract_acceptable_sentences_json_fp):
            with open(self._extract_acceptable_sentences_json_fp,'r',encoding='utf-8') as f:            
                self._extract_acceptable_sentences_json = json.loads(f.read())
        
        self._result_json = {}
        if os.path.exists(self._result_json_fp):
            with open(self._result_json_fp,'r',encoding='utf-8') as f:
                self._result_json = json.loads(f.read())
        '''
        格式：{title: {requirement: [original_sentences_0,translated_sentences_0,.......],...},...}
        '''
        
        if os.path.exists(self._log_fp):
            os.remove(self._log_fp)
        self._log = []
        
        if os.path.exists(self._result_csv_fp):
            os.remove(self._result_csv_fp) 
            
        #######   读取参数   ##########    
        self._llm_kwargs = llm_kwargs
        self._content_requirements = content_requirements
        self._content_classification = []
        # 修正可能含有的空行
        for line in content_classification.split('\n'):
            if line.strip():self._content_classification.append(line.strip())
        self._max_workers = max_workers
        self._target_language = target_language
        
        #####  记录参数  ##########
        self._parameter_json = {'sturcture_requirements':'\n'.join(self._content_classification)}
        self._parameter_json.update({'content_requirements':self._content_requirements})
        self._parameter_json.update({'target_language':self._target_language})
        


    def _request_llm(self,prompt,txt):
        try:
            a = predict_no_ui_long_connection(inputs=txt,llm_kwargs=self._llm_kwargs,history=[],sys_prompt=prompt)
            return True,a
        except Exception as e:return False,e
    
    def _update_log(self,level:Literal['life_timer','info','warning','error'],msg:str):
        
        if level not in ['life_timer','info','warning','error']:
            raise ValueError('level参数错误')
        
        if level == 'life_timer':
            return
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_log = f"[{current_time}] [{level.upper()}] {msg}"
        '#de425b'
        with lock:
            self._log.append(formatted_log)
        
    def _check_already_exist_inf(self,type:Literal['articles','useful_sentences','acceptable_sentences','result'],key):
        """当key存在时，返回true，否则返回false"""
        with lock:
            if type == 'articles':
                return key in self._articles
            elif type == 'useful_sentences':
                return key in self._useful_sentences_json
            elif type == 'acceptable_sentences':
                return key in self._extract_acceptable_sentences_json
            elif type =='result':
                return key in self._result_json
            else:raise ValueError('type参数错误')
        
    def _exec_multithread(self,pdf_file_fp,title,content,index):
        if title: title_to_print = self._title_splice_in_log(title)
        else: title_to_print = ''

         # 每个任务之间差个1.1s，因为有的服务限制是每秒一次请求...，反正1秒也无所谓
        sleep_time = index
        while sleep_time >= 0:
            sleep_time -= self._max_workers
        sleep((sleep_time + self._max_workers) * 1.1)

        # 首先，把新加的pdf导入到最开始的csv中（如果有的话）
        if self._check_lifespan_termination('一开始的'):return
        if pdf_file_fp:
            success,title,result =self._convert_pdf_to_article_csv_line(pdf_file_fp)
            if success:
                title_to_print = self._title_splice_in_log(title)
                self._update_log('info',_('{} 加载pdf成功').format(title_to_print))
                content = result;title = title.strip()
                with lock:self._articles.update({title:content})
            else:
                self._update_log('error',_('{} 加载pdf: 失败，后续过程将跳过。原因：{}').format(title_to_print,result))
                return
            
        # 之后，根据title和content先获取有用的句子（根据内容要求摘取句子）
        if self._check_lifespan_termination('获取有用句子'):return
        success,title,result = self._extract_get_useful_sentences(title,content)
        if not success:
            self._update_log('error',_('{} 获取有用句子失败，后续过程将跳过。原因：{}').format(title_to_print,result))
            return
        else:
            self._update_log('info',_('{} 获取有用句子成功').format(title_to_print))
            with lock:self._useful_sentences_json.update({title:result})
            
        # 摘取可以接受的句子（根据结构要求摘取和整理句子）
        if self._check_lifespan_termination('摘取可接受句子'):return
        success,title,result = self._extract_acceptable_sentences(title,result)
        if not success:
            self._update_log('error',_('{} 摘取可接受句子失败，后续过程将跳过。原因：{}').format(title_to_print,result))
            return
        else:
            self._update_log('info',_('{} 摘取可接受句子成功').format(title_to_print))
            with lock:self._extract_acceptable_sentences_json.update({title:result})
            
        # 翻译可接受的句子、
        if self._check_lifespan_termination('翻译可接受句子'):return
        success,title,result = self._translate_acceptable_sentences(title,result)
        if not success:
            self._update_log('error',_('{} 翻译可接受句子失败，后续过程将跳过。原因：{}').format(title_to_print,result))
            return
        else:
            self._update_log('info',_('{} 翻译可接受句子成功').format(title_to_print))
            with lock:self._result_json.update({title:result})

    def _check_lifespan_termination(self,who):
        """超时了（该死了）=true
        """

        cc = time() - self._time > self.lifespan
        if cc: 
            if self._executor:self._executor.shutdown(wait=False)
            self._executor = None # 貌似这样子可以修复重新进入之前的多线程任务、然后瞬间完成的bug 
            print(_('用户终止提取有用语句'))
            exit()
        return cc

    def _convert_pdf_to_article_csv_line(self,pdf_fp:str):
        """第零步。把PDF文件转换为article_csv可用的一行。默认获取前两页

        Args:
            pdf_fp (str): PDF路径

        Raises:
            FileNotFoundError: 文件不存在

        Returns:
            tuple: success, title, txt 或者 failure, title,error_msg
        """
        try:
            if os.path.exists(pdf_fp):
                doi,title,txt = get_pdf_content(pdf_fp,(0,1),True,self._llm_kwargs)
                os.remove(pdf_fp) # 然后把这个PDF删除
                if self._check_already_exist_inf('articles',title):return True,title,''
                return True,title,txt
        except Exception as e:
            return False,'',str(e)

    def _extract_get_useful_sentences(self,title:str,raw_text:str):
        """第一步，根据设定的内容要求，获取原始文本中的有用句子。

        Args:
            title (str): 论文标题
            raw_text (str): 需要分析的原始内容

        Returns:
            tuple: success, title, result/error_msg(空的时候说明之前已经有这个了)
        """
        
        # 摘取可能有用的语句。
        prompt = \
            f'''
            Please read the following content and extract sentences that meet the specified requirements without any modifications,
            ensuring they are exactly as in the original text.
            {self._content_requirements}
            Please provide the specific sentences you want me to extract directly in your response. 
            Use the original text of the sentences without adding any other content, 
            translating, or making any modifications. 
            Place each sentence on a separate line. Thank you.
            '''
        try:
            if self._check_already_exist_inf('useful_sentences',title) or not raw_text.strip():return True,title,''
            success,a = self._request_llm(prompt,raw_text)
            return success,title,a
        except Exception as e:
            return False,title,str(e)
    
    def _extract_acceptable_sentences(self,title:str,useful_sentences:str):
        """第二步。 摘取可以接受的句子

        Args:
            title (str): 文章标题
            useful_sentences (str): 可用句子

        Returns:
            tuple: success, title, result/error_msg(空的时候说明之前已经有这个了) → result:{requirement:translated_sentences}
        """
        
        prompt = \
        '''
        I will provide you with some sentences, which may contain content that meets the following requirements.
        If there is, please directly use the original text of the sentence to tell me, 
        do not add any other content, do not translate, 
        and do not make any modifications, one line per sentence, thank you.
        If not, please reply in Chinese with "无".
        Requirements: {}
        '''
        requirement_and_accecptable_sentences = {}
        try:
            if self._check_already_exist_inf('acceptable_sentences',title) or not useful_sentences.strip():return True,title,''
            
            for requirement in self._content_classification:
                if self._check_lifespan_termination('可接受内部'):return
                this_prompt = prompt.format(requirement)
                success,a = self._request_llm(this_prompt,useful_sentences)
                if not success:return False,title,a
                if '无' in a:a=''
                a = a.replace('。','.').replace('\n',' ').replace('\r',' ') # 取消换行，兼容中文符号
                # 提前切割好句子，方便后面翻译（顺便补一个句号）
                splitted_sentences = a.split('. ')
                for i, sentence in enumerate(splitted_sentences):
                    if not sentence.strip().endswith('.'):
                        splitted_sentences[i] = f'{sentence.strip()}.'
                requirement_and_accecptable_sentences.update({requirement:splitted_sentences}) 
                sleep(0.05)
            return True,title,requirement_and_accecptable_sentences
        except Exception as e:
            return False,title,str(e)
        
    def _translate_acceptable_sentences(self,title:str,acceptable_sentences:dict):
        """ 翻译可接受的句子

        Args:
            title (str):文章标题
            acceptable_sentences (dict):包含着 {requirement:accepted_sentences} 的东西

        Returns:
            tuple : success, title, result/error_msg(空的时候说明之前已经有这个了) → result:{requirement:[original_sentences_0,translated_sentences_0,.......]}
        """
        try:
            if self._check_already_exist_inf('result',title) or not acceptable_sentences:return True,title,''
            
            prompt = f'Please translate the following text into {self._target_language}'
            
            for requirement in self._content_classification:
                if self._check_lifespan_termination('翻译内部1'):return
                
                this_requirement_sentences = acceptable_sentences.get(requirement,[]) # {要求 : [每个句子的List]}

                acceptable_sentences[requirement] = [] # 清空原原文，方便一些
                # 翻译句子
                for sentence in this_requirement_sentences:
                    if self._check_lifespan_termination('翻译内部2'):return
                    stripped_sentence = sentence.strip()
                    if stripped_sentence and stripped_sentence != '.':
                        success,result = self._request_llm(prompt,stripped_sentence) # 请求翻译
                        if not success:return False,title,result
                        else:acceptable_sentences[requirement].extend((stripped_sentence,result))
                        sleep(0.05)
            return True,title,acceptable_sentences
    
        except Exception as e:
            return False,title,str(e)
    
    def deploy(self):
        task_fn = self._exec_multithread
        task_para_list = []
        a,pdf_list, b = get_files_from_everything(os.path.join(self.work_path,'pdf'),'.pdf')
        task_index = 0

        for pdf_fp in pdf_list:
            if os.path.isfile(pdf_fp):
                task_para_list.append((pdf_fp,None,None,task_index))
                task_index += 1
            else: gr.Warning(_('文件 {} 不存在，跳过').format(pdf_fp))
        for task_target in self._articles.items():
            task_para_list.append((None,task_target[0],task_target[1],task_index))
            task_index += 1
        with ThreadPoolExecutor(max_workers=self._max_workers) as self._executor:
            self._time = time()
            features = []
            for para in task_para_list:
                feature = self._executor.submit(task_fn,*para)
                features.append(feature)
            
            
            self._update_log('info',_('任务开始执行'))
            yield '\n'.join(self._log)
            

            while True:
                # 等死或者等结束
                if not self._executor:
                    return '\n'.join(self._log)
                elif self._executor._work_queue.empty() and all(f.done() for f in features):
                    self._executor.shutdown(wait=False)
                    yield '\n'.join(self._log)
                    break
                else:
                    yield '\n'.join(self._log)
                    sleep(0.1)
                    self._time = time()
                    
        return '\n'.join(self._log)
    
    def output(self):
        """ 输出结果文件

        Yields:
            str: 运行日志
        """
        
        # 每一块：{title: {requirement: [original_sentences_0,translated_sentences_0,.......]}}
        
        try:
            self._update_log('info',_('正在导出结果文件...')) 
            yield '\n'.join(self._log)
            
            # 最终的结果
            with open(self._result_csv_fp,'a',encoding='utf-8-sig',newline='') as f:
                writer = csv.writer(f)
                # 一开始先加一个表头
                writer.writerow(['datetime',datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'scholar navis version',VERSION])
                writer.writerow(['Content Requirements',self._content_requirements,'',''])
                writer.writerow(['Qualified Article Title','Content Classification','Original Sentences','Translated Sentences'])
                for title,content in self._result_json.items():
                    csv_line = [] 
                    for requirement in self._content_classification:

                        if isinstance(content,str):continue # 可能是空的字符，不知道为啥
                        if not content[requirement] is []:
                            for index,sentence in enumerate(content[requirement]):
                                if index % 2 == 0 : # 原文
                                    csv_line.extend([title,requirement,sentence])
                                else: # 译文
                                    csv_line.append(sentence)
                                    writer.writerow(csv_line)
                                    csv_line = []
        
            self._update_log('info',_('结果文件导出成功。正在导出中间文件...')) 
            yield '\n'.join(self._log)
        
            # 中间文件
            with open(self._articles_csv_fp,'w',encoding='utf-8-sig',newline='') as f:
                writer = csv.writer(f)
                for title,content in self._articles.items():
                    writer.writerow([title,content])
            with open(self._useful_sentences_json_fp,'w',encoding='utf-8') as f:
                f.write(json.dumps(self._useful_sentences_json,ensure_ascii=False,indent=4))
            with open(self._extract_acceptable_sentences_json_fp,'w',encoding='utf-8') as f:
                f.write(json.dumps(self._extract_acceptable_sentences_json,ensure_ascii=False,indent=4))
            with open(self._result_json_fp,'w',encoding='utf-8') as f:
                f.write(json.dumps(self._result_json,ensure_ascii=False,indent=4))
            with open(self._parameter_json_fp,'w',encoding='utf-8') as f:
                f.write(json.dumps(self._parameter_json,ensure_ascii=False,indent=4))
            
            self._update_log('info',_('中间文件导出完成。正在导出日志...')) 
            yield '\n'.join(self._log)
            
            # 导出一次日志
            with open (self._log_fp,'w',encoding='utf-8') as f:
                f.write('\n'.join(self._log))
        
        except Exception as e:
            self._update_log('error',_('输出结果失败，原因：{}').format(e))
            yield '\n'.join(self._log)
        

def gradio_func(**kwargs):

    # 依赖组件
    cookies :gr.State = kwargs['cookies']
    top_p :gr.Slider = kwargs['top_p']
    temperature :gr.Slider = kwargs['temperature']
    user_custom_data:gr.JSON = kwargs['user_custom_data']
    md_dropdown:gr.Dropdown = kwargs['md_dropdown']
    
    # step 0 新建摘要任务或导入已有任务
    task_name:gr.Textbox = kwargs['task_name']
    create_or_load_task_uploader :gr.File = kwargs['create_or_load_task']
    below_accordion:gr.Accordion = kwargs['below_accordion']
    
    # step 1 增量添加PDF
    upload_extra_pdf:gr.Files = kwargs['add_pdf']
    
    # step 2 设定分析参数 
    content_requirements:gr.Textbox = kwargs['content_requirements']
    content_classification:gr.Textbox = kwargs['content_classification']
    language:gr.Dropdown = kwargs['language']
    max_workers:gr.Slider = kwargs['max_workers']
    
    # step 3 执行
    task_exec_btn:gr.Button = kwargs['task_exec_btn']
    
    # step 4 获取结果
    all_files_dl:gr.DownloadButton = kwargs['all_files_dl']
    result_file_dl:gr.DownloadButton = kwargs['result_file_dl']
    cancel_btn:gr.Button = kwargs['cancel_btn']
    reset_btn:gr.Button = kwargs['reset_btn']
    log:gr.Textbox = kwargs['log']
    
    
    # 更新任务名字
    task_name.change(fn=for_gradio.update_task_name,inputs=[cookies,task_name],outputs=cookies)
    
    # 上传或新建任务
    create_or_load_task_uploader.upload(fn=for_gradio.create_or_load_task,inputs=[cookies,task_name,create_or_load_task_uploader],outputs=[cookies,content_classification,content_requirements,language,below_accordion]).success(
        fn=lambda:gr.update(visible=True),outputs=below_accordion
    )
    # 删除上传的文件
    delete_clear_file = {
        'fn':lambda:gr.update(visible=False),
        'inputs':None,
        'outputs':below_accordion,
    }
    create_or_load_task_uploader.delete(**delete_clear_file)
    create_or_load_task_uploader.clear(**delete_clear_file)
    
    # ミッション　スタート
    exec_1 = task_exec_btn.click(fn=for_gradio.before_start_task,inputs=[cookies,content_classification,content_requirements,language],outputs=[cookies,task_exec_btn,cancel_btn]).success(
        fn=for_gradio.execute_task,
        inputs=[cookies,md_dropdown,top_p,temperature,log,user_custom_data,create_or_load_task_uploader,upload_extra_pdf,language,content_classification,content_requirements,max_workers],
        outputs=[log,all_files_dl,result_file_dl],
    )
    
    # 取消按钮
    # 好像是先cancel再执行fn
    cancel_event = {'fn': lambda cookies: cookies.update({'extract_sentences_already_run':False}) if cookies else {},
                    "inputs":cookies,
                    'outputs':cookies,
                    'cancels':exec_1,
                    }
    
    cancel_btn.click(**cancel_event)
    # 重置按钮
    reset_btn.click(**cancel_event).success(fn=for_gradio.reset,inputs=[cookies,md_dropdown,user_custom_data],outputs=[cookies,task_exec_btn,cancel_btn,below_accordion,content_classification,content_requirements,language,task_name,create_or_load_task_uploader,upload_extra_pdf,all_files_dl,result_file_dl,log])