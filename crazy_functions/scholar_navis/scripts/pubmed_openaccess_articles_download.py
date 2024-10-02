import os
import json
import shutil
import tarfile
import zipfile
import requests
import threading
from time import time,sleep
from datetime import datetime
from bs4 import BeautifulSoup

from shared_utils.sqlite import SQLiteDatabase, db_type
from .tools.multi_lang import _
from multiprocessing import cpu_count
from requests.adapters import HTTPAdapter,Retry
from shared_utils.config_loader import get_conf
from concurrent.futures import ThreadPoolExecutor
from ...crazy_utils import get_files_from_everything
from .tools.common_plugin_para import common_plugin_para
from toolbox import CatchException,update_ui,update_ui_lastest_msg
from .tools.article_library_ctrl import check_library_exist_and_assistant,download_file,get_data_dir,get_tmp_dir_of_this_user,csv_load



lock = threading.Lock()

# 单独写出来，因为它不需要LLM也可以工作，降低耦合度，方便以后移植

# http://localhost:9961/file=/home/hirasawayui/ai/lab_gpt_academic/gpt_log/default_user/downloadzone/2024-06-07-16-30-39-%E4%B8%8B%E8%BD%BD%E6%97%A5%E5%BF%97.txt

# /home/hirasawayui/ai/lab_gpt_academic/database/pubmedOA

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2774.1 Safari/537.36'}
pubmed_api = 'https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=[PMCID]'



# 网络重试策略
retries = Retry(
    total=3,                           # 总共重试的次数
    backoff_factor=0.3,                  # 重试之间的延迟因子（初值为1）
    status_forcelist=[500, 502, 503, 504,495,496,403],  # 设置需要重试的状态码
    allowed_methods=["HEAD", "GET", "OPTIONS"]  # 设置允许重试的方法
)
adapter = HTTPAdapter(max_retries=retries)

class openaccess_download:


    def __init__(self) -> None:
        
        # 下载文件夹创建和获取
        self._local_pdf_storage_dir  = get_data_dir('pubmedOA_download')
        # 下载总数
        self._total = 0
        # 下载完成（含下载失败）数
        self._n = 0
        # 下载日志
        self._download_log = []
        # 记录着所有请求的下载状态，就是每一个PMID都有一个元素
        self._each_download_status_dict_list = []        
        # 用于防止在超时终止下载后，仍然有新的线程执行下载的问题
        self.timeout_terminated = False
        
        # 总体上的下载情况
        self.download_status = {'status':'waiting','success_pmid':[],'success_fp':[],'failed_pmid':[],'log_fp':''}
        
        self.timer = None
        

    # 只能在这里加一个proxy了。。
    def download(self,proxies:str,PMIDs: list[str],PMCIDs: list[str],chatbot): # 用chatbot得了
        """ 使用API下载PubMed上的OA文章。另外还有网络代理功能
            兼容（杂糅）着后台下载的功能（仅限web界面）
            只有OA才有PMCID
            
        Returns:
            - 返回成功下载到的文章路径列表
            - 返回下载成功的文章PMCID列表
            - 返回下载失败的文章PMCID列表
        """
        #此次下载任务的临时保存目录
        tmp_dir = get_tmp_dir_of_this_user(chatbot,'PubmedOpenAccessDownload',['download'])    
            
        # 初始化下载状态
        for index, pmid in enumerate(PMIDs):
            self._each_download_status_dict_list.append({'PMID':pmid,'PMCID':PMCIDs[index],"STATUS":'waiting',"INFO":'OK'})

        # <--------------- 检查是否本地存在，顺便检查一下有没有PMCID------------------->
        # 本地数据库的文件夹
        if not os.path.exists(self._local_pdf_storage_dir): os.makedirs(self._local_pdf_storage_dir)
        
        
        # 记录一下无需网络请求的（本地储存 + 没有PCMID）
        without_network_requirement = 0
        # self.download_status_table_dict_list 与 PMID是一致的，用这个方便一些
        for index, status in enumerate(self._each_download_status_dict_list):
                pmcid = status['PMCID']
                
                # 检查有没有PMCID
                if pmcid == '':
                    # 记录一下，这个PMID没有PMCID
                    self._each_download_status_dict_list[index]['STATUS'] = 'failed'
                    self._each_download_status_dict_list[index]['INFO'] = 'no PMCID found'
                    #print(f'PMID = {PMIDs[index]} 并没有对应的PMCID ')
                    without_network_requirement += 1
                
                # 检查是否本地存在
                elif os.path.exists(os.path.join(self._local_pdf_storage_dir,f'{pmcid}.pdf')):
                    #print(f'在本地数据库中检索到 {pmcid}（PMID = {PMIDs[index]}） ')
                    # 记录一下，这个PMCID在本地数据库中找到了
                    self._each_download_status_dict_list[index]['STATUS'] = 'cached'
                    without_network_requirement += 1
        yield from update_ui_lastest_msg(_('完成已有文章的检查'),chatbot=chatbot,history=[])

        # 如果不用网络请求的和总数一致，就不用进行网络请求了
        if without_network_requirement == len(PMIDs):
            yield from update_ui_lastest_msg(_('所有需要下载的文章已经缓存'),chatbot=chatbot,history=[])
            # 输出结果
            self.__update_conclusion_list_to_export_path(tmp_dir=tmp_dir)
            self.__download_log_updater()
            return
        
    # * 只有有PMCID的才会执行后面的网络请求
        
    # <--------------- 决定是否使用网络代理 ------------------->
    
        # UA 和 重试策略
        session = requests.session()
        session.headers.update(headers)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        if not proxies is None:
            # 先解析程序所在的地理位置，如果是大陆则使用代理
            print(_("检测网络情况..."))      
            yield from update_ui_lastest_msg(_('检测网络情况...'),chatbot=chatbot,history=[])
            try:
                response = session.get(url='https://searchplugin.csdn.net/api/v1/ip/get',timeout=(3,3))
                
                if response.status_code == 200:
                    # 解析返回的内容
                    json_ip = json.loads(response.text)
                    ip = json_ip['data']['ip'];address = json_ip['data']['address']
                    print(ip +'   '+address)
                    
                    # 如果是中国大陆，尝试启用代理
                    if '中国' in address:           
                        # 尝试代理是否生效（以能否访问谷歌为准）
                        session.proxies = proxies
                        try:
                            response = session.get(url='https://www.google.com/',timeout=(3,3))
                            if response.status_code == 200:  
                                print(_('代理生效'))
                            
                            else : raise ConnectionAbortedError(_('连接超时'))
                        except : 
                            print(_('代理服务失效，使用直连'));proxies = None
                #无法获取地理位置，直接直连
                else:print(_('地理位置获取失败。使用直连')); proxies = None      
            except:print(_('网络监测失败。使用直连')); proxies = None      
        else: print(_('不使用网络代理')) ; proxies = None
        
        if not proxies is None:yield from update_ui_lastest_msg(_('下载将使用网络代理'),chatbot=chatbot,history=[])
        else:yield from update_ui_lastest_msg(_('下载不使用网络代理'),chatbot=chatbot,history=[])

        
        # <--------------- 多线程下载 ------------------->     
        
        # 记录一下下载数
        total = len(self._each_download_status_dict_list) - without_network_requirement
        self.download_status['total'] = total
        self._total = total
        
        # 多线程任务进行下载
        def thread_task(PMCID):
            self.__multi_thread_request(PMCID,tmp_dir,session)
            
        # 创建并启动线程
        with ThreadPoolExecutor(max_workers=cpu_count() * 2) as executor:
            
            # 只有有PMCID的、没有被缓存的才进行下载
            # 这也说明了，不必要下载的其实也在列表里
            features = []
            for index, status_dict in enumerate(self._each_download_status_dict_list):
                pmcid = status_dict['PMCID']
                if  pmcid != '' and status_dict['STATUS'] != 'cached': 
                    self.timer = time() # 这边也加上吧
                    features.append(executor.submit(thread_task, pmcid,))
            
            print(_('下载中，请等待...'))
            yield from update_ui_lastest_msg(_('下载中，请等待...'),chatbot=chatbot,history=[])
            
            # ! 按理来说，这里不应该有chatbot的，但是为了能实现终止，就只能在这放一个了
            # 这里别问，问就是从外部移动来的，凑合用吧
            _download_title = _('当前下载进度')
            _downlaod_count = _('下载数');_download_count_msg = _('已经存在的文章不含在内')
            _download_precent = _('完成百分比')
            _download_no_proxy = _('不使用网络代理');_download_with_proxy = _('使用网络代理')
            while True:
                #如果还没下载完
                if not self._n == self._total:
                    yield from update_ui_lastest_msg(lastmsg=f"### {_download_title }：\
                                \n\n - {_downlaod_count}： {self._n}/{self._total} （{_download_count_msg}）\
                                \n\n - {_download_precent}：{round(self._n / self._total * 100,2)}%\
                                \n\n - { _download_no_proxy if proxies is None else _download_with_proxy}",chatbot=chatbot,history=[])
                    # 给下载器的计时器续命
                    self.timer = time()
                    sleep(0.2)
                    
                #如果下载完了，破坏循环
                else: break
    
        print(_("所有文件下载完成"))
        session.close() # 关闭所有网络请求
        
        # <--------------- 输出文件 -------------------> 

        # 删除临时目录
        #shutil.rmtree(tmp_dir) # 交由每个负责下载的线程处理了。
        
        # 更新结果，输出
        self.__update_conclusion_list_to_export_path(tmp_dir=tmp_dir)
        self.__download_log_updater()
        
        
    def __multi_thread_request(self,PMCID,tmp_dir,session:requests.Session):
        """_summary_

        Args:
            PMCID (_type_): _description_
            tmp_dir (str): 一个根据当前时间创建的临时文件夹。其目录下应当是下载得到的pdf文件
            proxies (_type_): _description_

        Raises:
            ConnectionAbortedError: _description_
        """
        
        # 已经由于超时终止下载了，别动了
        if self.timeout_terminated:session.close();return  
        
        # 确定自己在 self.download_status_table_dict_list 里的 序号
        for index , download_status_table_dict in enumerate(self._each_download_status_dict_list):
            if download_status_table_dict['PMCID'] == PMCID:id = index
            # self.download_status_table_dict_list[id] 用来刷新自己这个格子的下载状态
    
        # api提供的xml里面只有tar.gz
        only_tgz = True
        
        # <--------------- 使用api请求下载地址 -------------------> 
        # 解析api得到的xml
        try:
            response = session.get(url=pubmed_api.replace('[PMCID]',PMCID),timeout=(3,3))
            self._each_download_status_dict_list[id]['STATUS'] = 'API parsing...'
            self.__download_log_updater()
        except:
            self._each_download_status_dict_list[id]['STATUS'] = 'failed'
            self._each_download_status_dict_list[id]['INFO'] = _('api解析失败')
            self._n += 1 # 解析错误，进度 +1
            self.__download_log_updater()
            return
        
        response.close()
        self._each_download_status_dict_list[id]['STATUS'] = _('api解析成功')
        self.__download_log_updater()
        soup = BeautifulSoup(response.text, "xml")
        
        # <--------------- 解析下载地址 -------------------> 
        url = None
        # 查找所有的<link>标签
        
        links = soup.find_all('link')
        
        # 如果没有这篇文章，或者说其他问题，报个错，然后停下
        if len(links) == 0:
            self._each_download_status_dict_list[id]['STATUS'] = 'failed'
            self._each_download_status_dict_list[id]['INFO'] = soup.error.get("code")
            self._n += 1 # 没有这个文章，进度 +1
            self.__download_log_updater()
            #print(f'{PMCID} 获取失败。error_code = {soup.error.get("code")}')
            return
        
        # 遍历所有找到的<link>标签，检查是否有PDF文件
        for link in links:
            format = link.get('format')
            # 如果有，优先使用pdf格式
            if format == 'pdf':
                only_tgz = False
                url = link.get('href').replace('ftp://','https://')
                break
            #没有的话，那就用tar.gz把
            elif format == 'tgz':
                only_tgz = True
                url = link.get('href').replace('ftp://','https://')
        
        # <--------------- 下载 -------------------> 

        # 下载临时路径
        download_tmp_file_fp = os.path.join(tmp_dir,f'{PMCID}.tar.gz') if only_tgz else os.path.join(tmp_dir,f'{PMCID}.pdf')

        try:
            
            # 已经由于超时终止下载了，别动了
            if self.timeout_terminated:session.close();return  
            
            response = session.head(url)
            # 下载  连接超时短点，毕竟已经有代理了
            response = session.get(url=url,stream=True,timeout=(3,10))
            self._each_download_status_dict_list[id]['STATUS'] = 'downloading'
            self.__download_log_updater()

            with open(download_tmp_file_fp, 'wb') as local_file:
                # 分块下载
                for chunk in response.iter_content(chunk_size=8192):
                    # 已经由于超时终止下载了，别动了
                    if self.timeout_terminated:session.close();return  
                    
                    if chunk:local_file.write(chunk)
                    
                    # 超时，停止
                    if time() - self.timer > 2:

                        self.timeout_terminated = True
                        response.close()
                        session.close()
                        print(_('用户终止下载'))
                        raise RuntimeError(_('用户终止下载'))
        
        except Exception as e :
            self._each_download_status_dict_list[id]['STATUS'] = 'failed'
            self._each_download_status_dict_list[id]['INFO'] = str(e)
            self._n += 1 #下载完成，进度+1
            self.__download_log_updater()
            #print(f'{PMCID} 下载出错  {str(e)}' )   
            return
        
        response.close()
            
        # 下载成功的话，更新输出信息
        self._each_download_status_dict_list[id]['STATUS'] = 'success'
        
        # <--------------- 解压缩，遗弃无用内容，仅保留需要的pdf ------------------->   
        
        try:
            if only_tgz:
                # 打开.tar.gz文件
                with tarfile.open(download_tmp_file_fp, 'r:gz') as tar:
                # 解压所有文件到指定目录，产生了一个PMCxxxxxxxx的目录
                    tar.extractall(tmp_dir)
                #解压缩的根目录
                tgz_root = os.path.join(tmp_dir,PMCID) 
                        
                #找pdf的路径
                for tgz_root_file in os.listdir(tgz_root):
                    if tgz_root_file.lower().endswith('.nxml'):
                        pdf_basename =  tgz_root_file.replace('.nxml','.pdf')
                        break
                    
                # 把需要的pdf移动到该去位置（就是tmp_dir）
                src = os.path.join(tgz_root,pdf_basename)
                dst = os.path.join(tmp_dir,f'{PMCID}.pdf')  # dst:把下载得到的pdf移动到tmp_dir目录下了
                shutil.move(src,dst)
                
                '''
                现在有这些无用的文件：
                download_tmp_file_fp：下载的tgz文件
                tgz_root (tmp_dir/PMCxxxxxxxx) ：tgz解压产生的文件夹
                这些东西都需要删除
                '''
                if os.path.exists(download_tmp_file_fp): os.remove(download_tmp_file_fp)
                if os.path.exists(tgz_root): shutil.rmtree(tgz_root)
                
                # 把download_tmp_file_fp设定成解压出来的pdf路径（毕竟download_tmp_file_fp之前的tgz的路径）
                download_tmp_file_fp = dst
        
    # <--------------- 把PDF移动到本地数据库中 ------------------->  
    
            # 移动到本地数据库
            filename = os.path.basename(download_tmp_file_fp)
            dst_local_db = os.path.join(self._local_pdf_storage_dir,filename)
            shutil.move(download_tmp_file_fp,dst_local_db)    
            
            self._n += 1 #下载完成，进度+1
            #完成任务，记录一下
            self.__download_log_updater()
        except Exception as e:# 只有IO那部分可能会出错
            self._each_download_status_dict_list[id]['STATUS'] = 'failed'
            self._each_download_status_dict_list[id]['INFO'] = str(e)
            # IO又出错了，进度+1
            self._n += 1 #下载完成，进度+1
            self.__download_log_updater()
            #print(f'对 {PMCID}.tar.gz 的解压缩操作出现错误')
                    
    def __download_log_updater(self):
        """ (配有多线程锁)
        - 更新下载日志
        - （可选）更新多进程消息队列，用于向主进程汇报下载进度
        """
        with lock:
            # <--------------- 对于 日志 的更新 -------------------> 
            self._download_log.clear()
            for download_status_dict in self._each_download_status_dict_list:
                self._download_log.append(f'[{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}]\t[{download_status_dict["PMID"]}]\t[{download_status_dict["PMCID"]}]\t{download_status_dict["STATUS"]}\t{download_status_dict["INFO"]}')
        
    def __update_conclusion_list_to_export_path(self,tmp_dir):
        """ 更新下载结果，并输出路径
            也会把下载日志写进 .log 文件里
        """
        
        # <--------------- 下载结果更新整理，便于输出 -------------------> 
        
        # 下载完成的文件路径
        success_files_fp = []
        # 下载完成的PMIDs
        success_files_pmid = []
        # 下载失败的PMIDs
        failed_files_pmid = []
        
        
        # 根据dict记载的信息，更新输出结果
        for status_dict in self._each_download_status_dict_list:
            # 下载失败的文件
            if 'failed' in status_dict['STATUS']:failed_files_pmid.append(status_dict['PMID'])
            # 下载成功的文件
            if status_dict['STATUS'] == 'success' or status_dict['STATUS'] == 'cached':
                success_files_pmid.append(status_dict['PMID'])
                success_files_fp.append(os.path.join(self._local_pdf_storage_dir,f'{status_dict["PMCID"]}.pdf'))
                
        print(f"download success：{', '.join(success_files_pmid)}\ndownload failed：{', '.join(failed_files_pmid)}")
        
        # 写入下载日志
        log_fp = os.path.join(tmp_dir,'download_log.log')
        with open(log_fp,"w",encoding='utf-8') as log:
            log.write('\n'.join(self._download_log))
        
        
        # 更新下载状态
        self.download_status['status'] = 'success'
        self.download_status['success_pmid'] = success_files_pmid
        self.download_status['success_fp'] = success_files_fp
        self.download_status['failed_pmid'] = failed_files_pmid
        self.download_status['log_fp'] = log_fp
        

@check_library_exist_and_assistant(accept_nonexistent=True,accept_blank=True)
@CatchException
def PubMed_OpenAccess文章获取(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    """ 
    - 通过PubMed的API下载文章。
    - 输出下载文章（ZIP压缩）和下载日志
    - 下载的链接可以放到输入框中作为缓存地址

    """
    line1 = _('上传您在PubMed中保存的csv格式的引文（citations）文件以执行新的下载任务')
    line2 = _('按下 <b>停止</b> 按钮以终止该下载进程')
    line3 = _('下载的时间比较耗时，可以打开新的页面进行ai对话')
    line4 = _('<font color=red>[提醒]</font> 当前一次下载任务终止后，再次运行可能会显示出之前的下载内容，尚未知如何修复。可以尝试`重置`')
    chatbot.append([_("批量从PubMed上下载 OpenAccess 文章") + f'\n\n{line4}',
                    f" - {line1}\
                    \n\n - {line2}\
                    \n\n - {line3}"])
    yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
    
    
# < -------------------- 开始获取csv中的pmcid --------------- >

    yield from update_ui_lastest_msg(_('正在处理...'),chatbot,[])
    
    _1,citations_csv_fp,_2 = get_files_from_everything(txt,'.csv')   
    
    if len(citations_csv_fp) == 0:
        yield from update_ui_lastest_msg(_('注意，上传的文件不是可用的csv文件'),chatbot,[])
        return
    
    # 获取PMCID PMID title doi
    pmcids = [];pmids=[];titles = []; dois =[]
    try:
        csv = csv_load(citations_csv_fp[0])
        
        for c in csv:
            pmcids.append(c['PMCID'])
            pmids.append(c['PMID'])
            titles.append(c['Title'])
            dois.append(c['DOI'])
    except:
        yield from update_ui_lastest_msg(_('读取出错！可能是文件内容缺失或错误，请检查"PMID", "PMCID", "Title", "DOI"及其内容是否是使用英文逗号分割，以及内容是否正确'),chatbot,[])
        return
        
    if len(pmcids) == 0 or len(pmids) == 0 or len(titles) == 0 or len(dois) == 0:
        yield from update_ui_lastest_msg(_('上传的文件中，缺少 "PMID", "PMCID", "Title", "DOI"其中的若干项目，或拼写错误，请检查'),chatbot,[])
        return
    
    #print(''.join(pmcids));print(''.join(pmids))
    #print(''.join(titles));print(''.join(dois))
    

    # 建立自己的sqlite数据库，用于储存从pubmed上下载得到的信息。方便后续根据doi获取title
    # pubmed的毕竟都是准确的信息
    # 文件太大的话，提醒一下
    file_size_mib = os.path.getsize(citations_csv_fp[0]) 
    if file_size_mib >= 1048576:
        yield from update_ui_lastest_msg(_('正在记录文章信息... ') + _('(文件较大，请等待)'),chatbot,[])
    else:yield from update_ui_lastest_msg(_('正在记录文章信息... '),chatbot,[])
    
    with  SQLiteDatabase(type=db_type.article_doi_title) as db:
        for index , doi in enumerate(dois):
            if doi is None or doi == '':# 还真有文章没有doi，那就没办法了
                pass
            else:
                db.insert_ingore(doi,('title','info'),(titles[index],'inserted from pubmed'))
        #print('数据库记录完成')
        yield from update_ui_lastest_msg(_('文章信息记录完成'),chatbot,[])
        # 测试一下
        #print(f"测试一下：{db.select('doi',dois[5],('title','info'))}")
    
    #return
    # < -------------------- 执行下载逻辑 --------------- >
    
    yield from update_ui_lastest_msg(_('正在下载文章...'),chatbot,[])
    proxies = get_conf('proxies')

    try:
        # 内含：下载与终止
        # 会一直阻塞，直到终止 or 下载完毕
        dl = openaccess_download()
        yield from dl.download(proxies,pmids,pmcids,chatbot) 
        
    except Exception as e:
        chatbot.append([_("出现错误。请检查上传的csv是否正确、代理格式是否正确、网络条件是否良好或其他可能存在的问题"),str(e)])
        yield from update_ui(chatbot=chatbot, history=[])  # 刷新界面
        return

                # < -------------------- 输出下载信息和下载文件  --------------- >
    
    # 获取下载信息
    success_files_pmid = dl.download_status['success_pmid']
    failed_files_pmid = dl.download_status['failed_pmid']
    success_files_fp = dl.download_status['success_fp']
    
    
    # 输出下载信息
    success_files_pmid_with_url = [f'<a href="https://pubmed.ncbi.nlm.nih.gov/{pmid}" target="_blank">{pmid}</a>' for pmid in success_files_pmid]
    failed_files_pmid_with_url = [f'<a href="https://pubmed.ncbi.nlm.nih.gov/{pmid}" target="_blank">{pmid}</a>' for pmid in failed_files_pmid]
    success_percent = round(len(success_files_pmid_with_url) / (len(success_files_pmid_with_url) + len(failed_files_pmid_with_url)) * 100 ,2)
    
    # 弄个缓存，便于弄压缩包
    tmp_dir = get_tmp_dir_of_this_user(chatbot,'PubmedOpenAccessDownload',['output'])
    # 获取下载日志
    log_path = dl.download_status['log_fp']
    
    # 把下载的文章压缩成zip
    zip_path = os.path.join(tmp_dir,'pubmed_openaccess_download.zip')
    with zipfile.ZipFile(zip_path, 'w') as zip:
        # 把pdf逐个添加到ZIP文件中
        for file in success_files_fp:
            zip.write(file, os.path.basename(file),compress_type=zipfile.ZIP_DEFLATED)
    
    
    title = _('此次 PubMed Open Access 下载任务执行完成')
    dl_success_msg = _('下载成功的文章')
    dl_failed_msg = _('下载失败的文章')
    dl_percent_msg = _('下载成功率')
    dl_failed_msg_note = _('如果下载失败，则需要手动下载')
    dl_failed_why = _('为什么会这样')
    dl_success_note = download_file(zip_path,_('点击获取下载的文章')) + '\t' + download_file(log_path,_('点击获取下载日志')) 
    dl_msg = _('可以直接将下载完成的文章进行分析: 用<b>缓存pdf文献</b>开始总结分析这些文章')
    
    chatbot.append([f'{title}</br>',
                    f'<ul><li>{dl_success_msg}: {", ".join(success_files_pmid_with_url)}</li>\
                        <li>{dl_failed_msg}: {", ".join(failed_files_pmid_with_url)}</li>\
                        <li>{dl_percent_msg}: {success_percent}%</li>\
                        <li>{dl_failed_msg_note}  <a href="https://www.ncbi.nlm.nih.gov/pmc/tools/developers/" target="_blank">[{dl_failed_why}]</a></li>\
                        <li>{dl_success_note}</li>\
                        <li>{dl_msg}</li></ul>'])
    
    yield from update_ui(chatbot=chatbot, history=history)

execute = PubMed_OpenAccess文章获取 # 用于热更新

class PubMed_Open_Access_Articles_Download(common_plugin_para):
    def define_arg_selection_menu(self):
        gui_definition = {}
        gui_definition.update(self.add_file_upload_field(title=_('上传保存的文章列表'),description=_('一般为csv格式')))
        gui_definition.update(self.add_command_selector([],[],[]))
        return gui_definition

    def execute(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
        yield from PubMed_OpenAccess文章获取(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request)