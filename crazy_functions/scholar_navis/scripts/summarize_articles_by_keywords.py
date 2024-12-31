import os
import yaml
import glob
import shutil
from datetime import datetime
from shared_utils.scholar_navis.other_tools import generate_download_file
from shared_utils.scholar_navis.const_and_singleton import VERSION
from time import sleep,time
from shared_utils.scholar_navis import pdf_reader
from shared_utils.scholar_navis.multi_lang import _
from multiprocessing import cpu_count
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from .tools.common_plugin_para import common_plugin_para
from toolbox import CatchException, get_log_folder, get_user, update_ui, update_ui_lastest_msg
from .tools.article_library_ctrl import check_library_exist_and_assistant, lib_manifest, pdf_yaml,markdown_to_pdf
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive, request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency

lock = Lock()

@check_library_exist_and_assistant(accept_nonexistent=False, accept_blank=False)
@CatchException
def 按关键词总结文献(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    """
    将analyzed中的所有文章进行统一总结

    后续自己写一个gradio，脱离现在用于对话的UI

    txt: 输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs: gpt模型参数, 如温度和top_p等, 一般原样传递下去就行
    plugin_kwargs: 插件的参数
    chatbot: 聊天显示框的句柄，用于显示给用户，一旦分行（输入逗号）就换说话人
    history: 聊天历史，前情提要
    system_prompt: 给gpt的静默提醒
    user_request: 当前用户的请求信息（IP地址等）
    """

    # < --------------------读取插件的参数--------------- >
    library_name = plugin_kwargs['lib']
    # GPT偏好语言
    GPT_prefer_language = plugin_kwargs['gpt_prefer_lang']
    # 命令获取
    command = plugin_kwargs['command']

    # 这个总结库的根目录
    this_library_root_dir = os.path.join(get_log_folder(
        user=get_user(chatbot), plugin_name='scholar_navis'), library_name)
    # 缓存文件夹
    cache_dir = os.path.join(this_library_root_dir, "cache")
    # 处理完的pdf所在的文件夹（归档咯）
    repo_dir = os.path.join(this_library_root_dir, "repository")
    summarization_file_fp = os.path.join(
        this_library_root_dir, "summarization.txt")
    summarization_pdf_fp = f'{summarization_file_fp[:-4]}.pdf'

    # 读一下现在的关键词（得到的是一个列表）
    with open(os.path.join(this_library_root_dir, 'lib_manifest.yml'), 'r') as f:
        keywords = yaml.safe_load(f)[lib_manifest.key_words.value]
    # 如果关键词没有，终止流程
    if len(keywords) == 0:
            # 没完成工作，开始总结流程
        chatbot.append([_("总结终止。没有找到可用的关键词"),
                    _("请在 <b>缓存pdf文献</b> 中设定关键词")])
        yield from update_ui(chatbot=chatbot, history=[]) 
        return

    # < --------------------------------------------事前准备----------------------------------------------- >

    # 判断本工具的工作流是否完成（该有的文件有了，该移动走的文件移走了）。
    # 防止重重复预处理
    pdfs_in_cache = glob.glob(os.path.join(cache_dir,"*.pdf"))
    pdf_yamls_in_cache = glob.glob(os.path.join(cache_dir,"*.yml"))
    pdfs_in_repo =  glob.glob(os.path.join(repo_dir,"*.pdf")) # 测试过了，路径不存在返回[]
    workflow_done = os.path.exists(summarization_file_fp)

    # 完成了所有的工作
    if workflow_done:
        # 强制重新分析的话，按照正常流程来就可以了
        if command == 'force':
            pass
        # 没有强制重新分析，就提醒一下
        else:
            # 读一下此前总结的内容
            with open(summarization_file_fp, "r", encoding='utf-8') as file:
                line1 = _(
                    '总结库 <b>{name}</b> 已经分析完毕，可以使用<b>与AI交流研究进展</b>进一步了解该方面的研究现状，如果得到了某篇感兴趣的文章，也可以使用 <b>精细分析文献</b> 进行精读').format(name=library_name)
                line2 = _('参考关键词')
                line3 = _('如果对分析结果不满意，可以选择强制重新分析（仅对最终总结生效）')
                line4 = _(
                    '<b>注意：</b>执行此操作会<font color=red>删除此前的总结</font>（不会影响预处理和预分析的结果）。如果对此前的总结不满意再使用! ')
                line5 = _('下面是此前的总结内容: ')
                chatbot.append([f"{line1}<br>\
                                <br><ul><li>{line2}: {', '.join(keywords)}</li>\
                                <li>{line3}</li>\
                                <li>{line4}</li></ul>",
                                line5])
                
                summarization_content = file.read()
                # 假如pdf没了，生成一个
                if not os.path.exists(summarization_pdf_fp):
                    markdown_to_pdf(summarization_content,'summarization',os.path.dirname(summarization_pdf_fp))
                chatbot.append([summarization_content,generate_download_file(summarization_pdf_fp,_('点击这里下载pdf格式的总结内容'))])
                # 提醒一下不能用的PDF
                chatbot.append(_unusable_pdf_message(this_library_root_dir))
                # 提醒一下不能对话
                chatbot.append([_('请注意，本功能不支持对话。'),_('如果要使用对话功能，请使用 <b>与AI交流研究进展</b>')])
            yield from update_ui(chatbot=chatbot, history=[])  # 刷新界面
            return

    # 没完成工作，开始总结流程
    chatbot.append([_("现在将对{}中的文献进行总结分析").format(library_name),
                    _("分析参考的关键词是 {}。为加快速度，默认 <b>仅对摘要</b> 进行总结").format(', '.join(keywords))])
    yield from update_ui(chatbot=chatbot, history=[])  # 刷新界面

    # < ---------（支持中断）预处理：对缓存中的pdf预处理（获取标题，摘要，参考文献），方便后续批量问GPT，不进行文件移动---------- >
    # 这里的中断是指，所有没有yaml的都被视为没有预处理，只要发生了预处理，就会有yaml

        
    # 如果缓存中没有待分析的pdf文件
    if len(pdfs_in_cache) < 1:
        # 也没有预处理完的文章
        if len(pdfs_in_repo) < 1:
            yield from update_ui_lastest_msg(_('该总结库中没有任何可用的pdf文章。如果需要进行总结分析，请先使用 <b>缓存pdf文献</b> 添加新的文章'), chatbot, [])
            return

        # 已经有分析过的文章了，缓存里又没有新的说明预处理完成了
        else:
            chatbot.append(
                [_("没有新的文章需要预处理或已预处理完成"),
                 _("目前已经有<b>{}篇文章</b>预处理完毕，即将进行下一步操作...").format(len(pdfs_in_repo))])
            yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面

    # 如果缓存中有待分析的pdf文件，那就先预处理吧
    # 针对重新分析，此时工作流已经完成，及时cache中有没有分析的文章（一般是不能用的），也跳过
    elif not workflow_done:
        
        timer = 0
        
        def _preprocess_multithread(pdfs_fp: list[str]):
            """给 选定的pdf们 提供多线程用获取PDF信息（即所谓的“预处理”）
            Args:
                pdfs_fp (list[str]):需要预处理的pdf们

            """
            # 获取pdf的标题、摘要（并且会在pdf旁边生成一个记录这些内容的yml，文件名与pdf一致）
            _pdf_manifests_fp = []

            for pdf_fp in pdfs_fp:
                # 如果超时，就不获取了
                if time() - timer > 2:
                    sleep(0.1)
                    if time() - timer > 2:
                        return []
                    '''为何又睡了0.1s：
                        实践过程中发现，当数据库不存在时，有的线程刚启动，time() - timer就大于2s了，这样会使线程意外终止（即使父线程还在运行）
                        然后我想，这个现象会不会是因为子线程这里的timer还没反应过来
                        于是就再睡0.1s（反正也不长，感知不明显）
                        如果过了0.1s，还是超时的，说明父线程真的挂了，那么子线程停下来就行
                        反之，如果不超时了，那就继续正常的运行下去就行
                        这里的代码运行挺快的（缓存 + 比较快的LLM，通常情况下能把cache中的pdf全都预处理完成）
                        通过极端测试（总是使用AI辅助 + max_workers = 1 + 超时1s），测试是可以正常终止的
                    '''
                
                # 如果有yaml了，也就没有必要进行预处理了
                if os.path.exists(f'{pdf_fp[:-4]}.yml'):
                    _pdf_manifests_fp.append(f'{pdf_fp[:-4]}.yml')
                    continue
                
                # 没有yaml，就获取一个吧
                usable,_1, pdf_manifest_fp = pdf_reader.get_pdf_inf(pdf_fp,plugin_kwargs['ai_assist'],llm_kwargs)
                # 储存所有的清单文件路径
                if usable: _pdf_manifests_fp.append(pdf_manifest_fp)
                else :
                    with lock:
                        _unusable_pdf_message(lib_dir=this_library_root_dir,unusable_pdf_fp=pdf_fp)
                
            return _pdf_manifests_fp
        
        # 多线程预处理
        max_workers = cpu_count()
        if plugin_kwargs['ai_assist']:max_workers = 3 # 如果有访问AI的情况，限制一下，防止超出最大并发
        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix='article-preprogress-') as executor:
            # 按照核心数划分需要进行预处理的pdf
            # 每一组里面有几篇文章（对于一些已经有yaml的，不需要重复分析）
            group_mumber_count = int(len(pdfs_in_cache)/ cpu_count())
            if group_mumber_count == 0:
                group_mumber_count = 1
            # 划分成几组，每一个task都处理一组pdf预处理的任务
            # 分组数=CPU核心数
            # 每个核心都分一点活干
            group_pdfs_in_cache_wait_process_path = [
                pdfs_in_cache[i:i+group_mumber_count] for i in range(0, len(pdfs_in_cache), group_mumber_count)]
            tasks = []
            for each in group_pdfs_in_cache_wait_process_path:
                timer = time() # 不加不行
                tasks.append(executor.submit(_preprocess_multithread, each))

            # 等待任务执行完毕
            chatbot.append([_('目前有{pdf_count}篇文章处于缓存中（实际需要预处理{jb}篇，{done}篇已经完成流程），即将使用{cpu}个线程进行预处理。全部预处理完成后就会使用GPT进行汇总分析...')
                            .format(pdf_count=len(pdfs_in_cache),jb= len(pdfs_in_cache) - len(pdf_yamls_in_cache),done = len(pdfs_in_repo),cpu=cpu_count()),
                            _('预处理中....')])
            yield from update_ui(chatbot=chatbot, history=history)
            
            while True:
                task_done_num = 0
                for task in tasks:
                    if task.done():
                        task_done_num += 1
                
                yield from update_ui_lastest_msg(_('任务分组 [{done_num}/{task_total}] 预处理中...')
                                                .format(done_num=task_done_num, task_total=len(tasks)), chatbot, [])
                # 处理完了？
                if task_done_num == len(tasks):break
                sleep(0.1)
                timer = time()

        pdf_manifests_fp = []
        for task in tasks:
            # 获取pdf的标题、摘要和一作（并且会在pdf旁边生成一个记录这些内容的yml，文件名与pdf一致）
            _pdf_manifest_fp = task.result() # 
            # 储存所有的清单文件路径
            pdf_manifests_fp.extend(_pdf_manifest_fp)

        yield from update_ui_lastest_msg(_('缓存文章预处理完成'), chatbot=chatbot, history=history)
        chatbot.append(_unusable_pdf_message(lib_dir=this_library_root_dir))
        #  注意，预处理完成后的pdf仍然在cache文件夹中（但是会多一个pdf清单文件md5.yml），因为他们还没有经过GPT分析
        #  总结完摘要的文章会在repo中，并且最后的总结性内容只会把pdf_yml中的analysis喂给AI
        #  这样子就可以实现预处理结束后问AI的阶段“断点续传”了

    # < -------（组间支持中断）预分析：使用GPT，对每组的pdf摘要进行单独分析（设定keywords_analysis值），之后会移动到repo文件夹中------------ >
    # 详细说一下啊，这里的中断是指，在repo里的为处理完的，不会进行分析
    # 所有在cache中，无论是否有被分析过的，都会进行分析
    # 反正差别就5个了，💩山先这个样子吧

        chatbot.append([_("现在开始使用GPT进行预先分析，每5个文章一组,总共有<b>{}</b>篇文章").format(len(pdf_manifests_fp)),
                        _("此过程中可以随时关闭该页面，下次会从 <b>中断的分组</b> 开始")])
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面

        # 对每5个pdf清单（md5.yml）进行总结分析
        # 确定能够分成多少个批次
        num_batches = len(pdf_manifests_fp) // 5 if len(pdf_manifests_fp) >= 5 else 1
        
        if num_batches == 0:
            yield from update_ui_lastest_msg(_('分析终止！因为某些原因，程序并没有找到可以总结分析的内容'), chatbot=chatbot, history=[])
            return

        # 划分列表为包含5个元素的批次
        batches = []
        for i in range(num_batches):
            # print("operation start!")
            start_index = i * 5
            # 还没有到最后一个完整的batch，batch5个内容就可以
            if i < num_batches - 1:
                batch = pdf_manifests_fp[start_index:start_index + 5]
            # 到了最后一个batch了，就把剩下不足5个的内容也归纳进来，就是最后一个batch可能有十多个内容了
            else:
                batch = pdf_manifests_fp[start_index:]
            batches.append(batch)

        # 对每个patch进行GPT 预分析
        for index, batch in enumerate(batches):
            
            # 先对每个文章的摘要单独分析一下
            # 这样子做可以精炼需要的信息，还可以去除提取abstract过程中产生的一些无用文本
            yield from _analyze_abstract_gpt(batch, keywords, index + 1, len(batches), llm_kwargs, GPT_prefer_language,
                                              chatbot, history, system_prompt, user_request)

            # 当前批次的文章分析完成后，就可以移动到analyzed文件夹了
            # 移动之后就不在cache文件夹了，防止多次重复分析
            for _pdf_manifest_fp in batch:
                filename,_1 = os.path.splitext(os.path.basename(_pdf_manifest_fp))
                yml_destination = os.path.join(
                    repo_dir, filename + '.yml')
                pdf_destination = os.path.join(
                    repo_dir, filename + '.pdf')
                # pdf路径
                pdf_fp = os.path.join(os.path.dirname(
                    _pdf_manifest_fp), filename + '.pdf')
                try:
                    os.makedirs(repo_dir, exist_ok=True)
                    shutil.move(pdf_fp, pdf_destination)
                    shutil.move(_pdf_manifest_fp, yml_destination)
                except IOError as e:
                    raise IOError(_("移动文件时出错：{}").format(str(e)))

    # 所有文章、按照所有的关键词都分析完了，就开始最后的总结了

    # < ---- ---- ---- -------总结，（repo文件夹内所有的yaml）具体的执行过程如下：----- ---- ---- ---- ---- ----------- >

    chatbot.append([_('正在总结，总结过程中，请不要关闭该页面...'), _('处理中....')])
    yield from update_ui(chatbot=chatbot, history=[])

    result = yield from _summarize_all_paper(this_library_root_dir, llm_kwargs, GPT_prefer_language, chatbot, [], system_prompt, user_request)

    # 四个🐎。去除代码块
    result = result.replace('```','')

    # 写成txt
    with open(summarization_file_fp, 'w', encoding='utf-8') as f:
        f.write(result)

    # pdf推送下载
    if os.path.exists(summarization_pdf_fp): os.remove(summarization_pdf_fp)
    markdown_to_pdf(result,'summarization',os.path.dirname(summarization_pdf_fp))

    chatbot.clear()
    chatbot.append([_('总结完成。下面是总结的内容: （不支持对话）') , 
                    '<ul><li>' +
                    _('围绕着关键词：{}').format(", ".join(keywords)) +
                    '</li><li>' +
                    _('如果不满意生成的结果（例如内容明显缺失），可以使用尝试重新生成') + 
                    '</li></ul>']) 
    
    chatbot.append([result,generate_download_file(summarization_pdf_fp,_('点击这里下载pdf格式的总结内容'))])
    chatbot.append(_unusable_pdf_message(lib_dir=this_library_root_dir))
    # 提醒一下不能对话
    chatbot.append([_('请注意，本功能不支持对话。'),_('如果要使用对话功能，请使用 <b>与AI交流研究进展</b>')])
    yield from update_ui(chatbot=chatbot, history=[])

execute = 按关键词总结文献 # 用于热更新

def _analyze_abstract_gpt(pdf_manifests_fp: list, keywords: list[str], start_batch: int, total_batch: int, llm_kwargs, GPT_prefer_language, chatbot, history, system_prompt, user_request):
    """ 对提供的每个pdf的摘要进行预分析，并将分析结果写到pdf清单（md5.yml）中
        现在主要是用于预分析，以后可能也有其他的功能吧

    Args:
        pdf_manifests_fp (list): pdf清单（md5.yml）列表
        keywords (list[str]): 关键词序列
        start_batch (int): 这是第几个batch
        total_count (int): 总共有几个batch
        analyzed_folder_fp (str): analyzed文件夹的绝对路径
        llm_kwargs (_type_): _description_
        plugin_kwargs (_type_): _description_
        chatbot (_type_): _description_
        history (_type_): _description_
        system_prompt (_type_): _description_
        user_request (_type_): _description_

    Yields:
        _type_: _description_
    """

    # GPT的访问参数
    inputs_array = []
    inputs_show_user_array = []
    history_array = []
    sys_prompt_array = []

    # 本地文章参数
    yml_array = []

    # 多线程问GPT
    for index, fp in enumerate(pdf_manifests_fp):   # 获取每一个pdf清单文件，用于读取摘要

        with open(fp, 'r') as f:
            yml_array.append(yaml.safe_load(f))

        # 如果没有摘要，就跳过吧
        abstract = yml_array[index][pdf_yaml.abstract.value]
        if abstract is None:
            continue

        i_say = f"I will provide you with a text next, and you are to analyze and summarize it. \
                There may be some extraneous content within these texts, \
                so please disregard any copyright or authorship information.\
                The text you are to summarize is: {abstract}, and you should focus on these keywords: {', '.join(keywords)}.\
                In addition, if the text mentions any experimental flaws, unmet objectives, \
                or the innovative aspects of the experiment, please also summarize those.\
                While ensuring accuracy and comprehensiveness, \
                use English to condense the summary content as much as possible."

        i_say_show_user = _("[批次进度：{a}/{b}] 请对这篇文章的摘要进行总结概括\n\n围绕: {key}").format(
            a=start_batch, b=total_batch, key=', '.join(keywords))

        inputs_array.append(i_say)
        inputs_show_user_array.append(i_say_show_user)
        history_array.append([])
        sys_prompt_array.append('')

    # 多线程请求GPT
    if inputs_array is []:     # 针对这个关键词，如果所有文章都已经单独分析过了，那么inputs_array就是空，也就没有必要请求GPT了
        return

    gpt_response_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
        inputs_array=inputs_array,
        inputs_show_user_array=inputs_show_user_array,
        history_array=history_array,
        sys_prompt_array=sys_prompt_array,
        llm_kwargs=llm_kwargs,
        chatbot=chatbot,
        show_user_at_complete=False
    )

    # gpt_response_collection.extend([inputs_show_user, gpt_res])

    # < -------围绕某个关键词、摘要总结完后，把总结的内容写到md5.yml中------------ >

    # 遍历GPT输出的结果
    yml_index = -1
    for index, content in enumerate(gpt_response_collection):
        # 奇数，获取的是gpt_res，里面是GPT对于单个文章的总结归纳
        if index % 2 != 0:  # 1 3 5 7 9 
            # 写入当前关键词总结的内容（没有摘要的不写）
            # 如果没有摘要，就跳过吧
            yml_index += 1
            abstract = yml_array[yml_index][pdf_yaml.abstract.value]
            if not abstract is None:
                yml_array[yml_index][pdf_yaml.analysis.value] = content
                with open(pdf_manifests_fp[yml_index], 'w') as f:
                    f.write(yaml.safe_dump(yml_array[yml_index]))


def _summarize_all_paper(this_library_fp: str, llm_kwargs, GPT_prefer_language, chatbot, history, system_prompt, user_request):
    '''
    # ! 改成每10个总结内容（数量或许可以更多点？）让LLM进行分析总结。内容如下：
    -   他们的研究方向：........ （尽可能简短，每一个都要有）
    -   这些研究的共同之处：........
    -   这些研究的差异点：.........
    -   这些研究的创新之处:.......
    -   这些研究得到的结论：......,..
    -   这些研究中出现的问题或错误：........
    
    # ! 所有的10个都分析完成之后，针对得到的总结内容，按照相同的格式，再次总结。这次就是把每个总结内容每一个之间彼此分析一次
    
    # ! 这样子的话也可以实现中断后继续分析，毕竟让LLM分析的过程还挺煎熬的
    '''
    #  < ---------------------- 事前准备 --------------------------- >

    repo_dir = os.path.join(this_library_fp, "repository")

    # 获取所有pdf的分析内容
    all_pdf_yml = []  # 文件名（含拓展名）
    for pdf in os.listdir(repo_dir):
        if pdf.lower().endswith('yml'):
            all_pdf_yml.append(pdf)

    #  < ---------------------- 任务分配 --------------------------- >

    if len(all_pdf_yml) == 0:  # 没有需要分析的也就没必要分析了
        return

    # 每个批次需要总结的内容（每个元素就是五篇文章的分析内容）
    batch_content = []

    # 对每5个pdf进行总结分析
    # 确定能够分成多少个批次
    num_batches = len(all_pdf_yml) // 5 if len(all_pdf_yml) >= 5 else 1

    for i in range(num_batches):
        start_index = i * 5
        # 还没有到最后一个完整的batch，batch  5个内容就可以
        if i < num_batches - 1:
            end_index = (i + 1) * 5
            batch = all_pdf_yml[start_index:end_index]
        # 到了最后一个batch了，就把剩下不足5个的内容也归纳进来，就是最后一个batch可能有十多个内容了
        else:
            batch = all_pdf_yml[start_index:]

        content = ''
        for index, yml_each_batch in enumerate(batch):
            with open(os.path.join(repo_dir, yml_each_batch)) as yml:
                content = f'{content} \n\n   {yaml.safe_load(yml)[pdf_yaml.analysis.value]}'
        batch_content.append(content)

    #  < ---------------------- 对分配下去的内容进行总结 --------------------------- >

    input_array = []
    prompt_array = []
    history_array = []
    inputs_show_user_array = []
    input = ''

    prompt = 'You are good at summarizing and analyzing. When answering my questions, try to be as detailed as possible.\
            And, please remember to respond to me in English.\
            Ensure that your thinking process includes a thorough examination of \
            what materials or tools were used, what was done, why it was done that way, \
            and what the significance or potential drawbacks of this approach are.\
            Please donnot specify which study it is, as they may have similarities. Use JSON and reply to me in this format (markdown):\n \
                    - Research Direction\n\
                    - The Commonalities in These Studies\n\
                    - Differences in These Studies\n\
                    - Innovative Aspects of These Studies\
                    - Conclusions from These Studies\n\
                    - Issues or Errors in These Studies'

    for content in batch_content:

        input = f'There are now five research topics: {content}. Please answer my questions based on these topics:\
                1. What are the research directions of these studies? please provide a brief answer for each.\
                2. What are the commonalities among these studies?\
                3. What are the differences among these studies?\
                4. What innovative aspects do these studies have?\
                5. What conclusions have these studies drawn (as detailed as possible)?\
                6. What issues, errors, or shortcomings have been mentioned in these studies?'

        prompt_array.append(prompt)
        input_array.append(input)
        history_array.append('')
        inputs_show_user_array.append(_('处理中...'))

    gpt_say = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
        inputs_array=input_array,
        inputs_show_user_array=inputs_show_user_array,
        llm_kwargs=llm_kwargs,
        chatbot=chatbot,
        history_array=history_array,
        sys_prompt_array=prompt_array,
    )

    yield from update_ui_lastest_msg(_('多线程操作完成'), chatbot=chatbot, history=[])
    #  < ---------------------- 对每一个批次总结得到的内容进行合并 --------------------------- >

    batch_analysis_content = ''
    for index, s in enumerate(gpt_say):
        if index % 2 == 1:
            batch_analysis_content = f'{batch_analysis_content}\n\n{s}'

    input = f'I will give you a large batch of similar JSONs.\
        Can you merge them into one JSON without modifying, removing, or adding any content, \
            and without changing the structure of the JSON? Thank you. \
                Here is the batch of JSONs for you: {"  ".join(batch_analysis_content)}'

    # combine = yield from request_gpt_model_in_new_thread_with_ui_alive(
    #     inputs=input,
    #     inputs_show_user=_('合并优化中...'),
    #     llm_kwargs=llm_kwargs,
    #     chatbot=chatbot,
    #     history=[],
    #     sys_prompt=prompt
    # )
    # yield from update_ui_lastest_msg(_('优化完成'), chatbot=chatbot, history=[])
    combine = "  ".join(batch_analysis_content)

    #  < ---------------------- 最后的处理，准备输出内容（使用偏好语言） --------------------------- >

    input = f'I will provide you with a JSON file. \
            Please remove any duplicated content and then provide a comprehensive summary at the end. \
            Present the result in a visually appealing Markdown format, \
            and please provide me with the processed results directly, without any other information. \
            The JSON is as follows: {combine}'
    gpt_summary = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=input,
        inputs_show_user=_('最后总结中.....'),
        llm_kwargs=llm_kwargs,
        chatbot=chatbot,
        history=[],
        sys_prompt=f'please answer me in {GPT_prefer_language}. Please just show me the Markdown, without using code blocks (````). I want to see the rendered result of the Markdown.'
    )

    yield from update_ui_lastest_msg(_('总结完成'), chatbot=chatbot, history=[])
    return gpt_summary


def _unusable_pdf_message(lib_dir:str,unusable_pdf_fp: str = None):
    # 预处理（得到DOI标题啥的）那里提醒一次
    # 总结结束那里再提醒一次
    # 也提供一下下载，让用户知道是哪个文章不能用
    # 同样的，支持中断
    
    unusable_pdf_yml_content = {'latest_datetime':datetime.now().strftime("%Y-%m-%d %H-%M-%S"), # 因为支持中断，所以记录最新的更新日期
                                'preprocess_done':False, # 所有的预处理完成了吗？
                                'scholar_navis_version':VERSION,
                                'reason':'Chinese dissertations, encrypted files, non-PDF files or damaged files',
                                'list':[]}

    unusable_pdf_yml_fp = os.path.join(lib_dir,'unusable_pdf_list.yml')
    
    if not os.path.exists(unusable_pdf_yml_fp):
        with open(unusable_pdf_yml_fp,'w',encoding='utf-8') as f:
            f.write(yaml.safe_dump(unusable_pdf_yml_content))
            
    # 记录这些不能用的文章，生成一个txt，便于后面的提示和下载
    with open(unusable_pdf_yml_fp,'r',encoding='utf-8') as f:
        unusable_pdf_yml_content = yaml.safe_load(f)
    
    # 新产生的无用PDF
    if unusable_pdf_fp:
        # 把新的，不重复的添加进来
        if unusable_pdf_fp not in unusable_pdf_yml_content['list']:
            unusable_pdf_yml_content['list'].append(unusable_pdf_fp)
            unusable_pdf_yml_content['latest_datetime'] = datetime.now().strftime("%Y-%m-%d %H-%M-%S") # 记录更新日期
    # 没有新产生的，就用之前保存的提示。反正不能添加新的文章了
    else:
        unusable_pdf_yml_content['preprocess_done'] = True

    # 记录咯
    with open(unusable_pdf_yml_fp,'w',encoding='utf-8') as f:
        f.write(yaml.safe_dump(unusable_pdf_yml_content))

    if len(unusable_pdf_yml_content['list']) > 0:
        download_list = '<ul>\n'
        for file in unusable_pdf_yml_content['list']:
            download_list +=  f'<li>{generate_download_file(file)}</li>\n'
        download_list += '\n</ul>'
        return [_('存在不可使用的PDF（中文学位论文、加密文件、非PDF文件或损坏文件），这些文件不会参与总结。文件如下：'),download_list]
    else: return [_('全部PDF可用！'),_('不存在不可用的PDF')]
        
class Summarize_Articles_Keywords(common_plugin_para):
    def define_arg_selection_menu(self):
        gui_definition = super().define_arg_selection_menu()
        gui_definition.update(self.add_lib_field(False))
        gui_definition.update(self.add_GPT_prefer_language_selector())
        gui_definition.update(self.add_command_selector(['force'], [_('强制重新分析')], [False]))
        gui_definition.update(self.add_use_AI_assistant_selector())
        return gui_definition

    def execute(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
        yield from 按关键词总结文献(txt, llm_kwargs,plugin_kwargs,chatbot,history,system_prompt,user_request)