'''
Author: scholar_navis@PureAmaya
'''

import os
import yaml
import zipfile
from shared_utils.scholar_navis.other_tools import generate_download_file
from shared_utils.scholar_navis.multi_lang import _
from .tools.common_plugin_para import common_plugin_para
from .tools.article_library_ctrl import check_library_exist_and_assistant,lib_manifest,pdf_yaml,get_tmp_dir_of_this_user
from toolbox import CatchException, get_log_folder,get_user,update_ui,update_ui_lastest_msg
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive,request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from ...生成多种Mermaid图表 import 生成多种Mermaid图表

@check_library_exist_and_assistant(accept_nonexistent=False,accept_blank=False)
@CatchException
def 与AI交流研究进展(txt: str, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    """显示总结内容，提供某个单独文章的下载（pdf+分析），与AI对话有关内容，分析某个特定单一pdf
        此外，也使用它，配合用户输入，与其他作图等工具结合，统一化分析
        执行后，会清除聊天的历史记录与聊天内容

    Args:
        this_paper_archive_fp (str):这个总结库的绝对路径
        keywords (list): 关键词
        llm_kwargs (_type_): 大语言模型参数
        plugin_kwargs (_type_): 插件的参数
        chatbot (_type_): 聊天句柄，显示给用户
        history (_type_): 聊天历史
        system_prompt (_type_): 给GPT的静默提醒
        user_request (_type_): _当前用户的请求信息

    """

    # < --------------------读取插件的参数--------------- >

    library_name = plugin_kwargs["lib"]
    # GPT偏好语言
    GPT_prefer_language = plugin_kwargs['gpt_prefer_lang']
    command = plugin_kwargs['command']
    command_para = plugin_kwargs['command_para']
    

    # 工具的根目录与各种目录
    tool_root = get_log_folder(user=get_user(chatbot), plugin_name='scholar_navis')
    this_library_fp = os.path.join(tool_root, library_name)
    repo_dir = os.path.join(this_library_fp, 'repository')
    with open(os.path.join(this_library_fp,'lib_manifest.yml'),'r') as yml:
        keywords = yaml.safe_load(yml)[lib_manifest.key_words.value]

    # 能找到一个合法的总结库，进入后续的操作
    summarization_file_fp = os.path.join(this_library_fp, "summarization.txt")

    if os.path.exists(summarization_file_fp):
        try:
            with open(summarization_file_fp, "r",encoding='utf-8') as file:
                summarization = file.read()  # 先暂时用这个吧，就是总结文件里面只有总计内容了
        except Exception as e:
            chatbot.append([_('读取总结文件失败！具体原因如下：'),str(e)])
            yield from update_ui(chatbot=chatbot, history=[])
            return
    else:
        chatbot.append([_('出现问题'),_('该总结库不含总结文件，可能是尚未完成总结或者意外删除？可以尝试重新总结')])
        yield from update_ui(chatbot=chatbot, history=[])
        return
    
    # < --------------------根据用户命令决定输出什么内容（含命令command内容，help交给了修饰器）------------------------ >、、

    # 预存一个历史，便于后续问AI
    # 就是说，history 里面有总结的内容，以及对于更精细内容的提醒
    history = [f'Rmember, please answer me in {GPT_prefer_language}.']
    history.append(f'For subsequent responses and any questions regarding the article, the above content, \
            or any other materials that may have been mentioned , please refer to this content: {summarization}')
    history.append(_('如果有问道某些内容的出处、来源，或者是其他的你不知道的内容、没有给你提供的内容时，请说“如果要确定详细的内容或者是寻找来源，请使用 find 命令 和 精细分析文献 功能'))

    # 没有特别输入什么，把历史记录重置为原始的总结内容，然后清理一下聊天，方便使用普通的对话
    if  command == '':
        chatbot.append(
            [_("现在可以直接与AI交流总结的内容。也可以使用帮助指令查询还可以做些什么 \n\n总结库 <b>{name}</b> 在 <b>{key}</b> 方面的总结如下：")
            .format(name = library_name,key = '</b>,<b>'.join(keywords))
            ,summarization])
        # 记录history，这样子就可以更新全局的history了
        yield from update_ui(chatbot=chatbot,history=history)
        return

    # 希望绘制思维导图等
    elif command == 'draw':
        chatbot.append(
            [_("尝试绘制图表（可能会作图失败，那时就多运行几次吧）...\n\n总结库 <b>{name}</b> 在 <b>{key}</b> 方面的总结如下：<details><summary><u>展开以检视总结的内容...</u></summary>{ov}</details>")
            .format(name = library_name,key = '</b>,<b>'.join(keywords),ov = summarization),
            _("等待绘制.....")])
        yield from update_ui(chatbot=chatbot, history=history)

        # 把参数转成数字
        try:
            index = int(command_para)
        except:
            # 参数不是数字，比如全都是空格，或者压根就没有，亦或者是别的奇怪的内容，就用默认的思维导图
            yield from update_ui_lastest_msg(_('参数 <b>{}</b> 不合适或超出范围，修正为 9（思维导图）').format(command_para), chatbot=chatbot, history=history)
            index = 9

        # 尝试调用方法，反正出问题会提醒
        try:
            yield from 生成多种Mermaid图表(summarization, llm_kwargs, {'index':index,'gpt_prefer_lang':GPT_prefer_language}, chatbot, history, system_prompt, 9961)
        except Exception as e:
            yield from update_ui_lastest_msg(_('无法生成图表。具体原因如下: \n{}').format(str(e))
                                            , chatbot=chatbot, history=history)
        return

    # 从总结的内容中找到自己感兴趣的文章
    elif command == 'find':
        chatbot.append([_("开始查找可能是来源的文章... "), _("请等待...")])
        yield from update_ui(chatbot=chatbot, history=history)

        # 如果就一个find（没有参数），提醒一下
        if command_para == '':
            yield from update_ui_lastest_msg(_('请输入希望溯源的内容'), chatbot=chatbot, history=history)
            return
        else:
            # 尝试调用方法，反正出问题会提醒
            try:
                yield from __find_article_from_summarization(this_library_fp, command_para, GPT_prefer_language, llm_kwargs,system_prompt, chatbot,history)
            except Exception as e:
                yield from update_ui_lastest_msg(_('无法溯源。具体原因如下: \n{}').format(str(e)), chatbot=chatbot, history=history)
            return

    # 想拟定几个课题
    elif command == 'topic':

        chatbot.append([_("尝试拟定课题中..."), _("请等待...")])
        yield from update_ui(chatbot=chatbot, history=history)

        # 拟定要求
        request = "First off, the topic has to be right, with a solid basis for it to be pursued; secondly, it needs to have a pretty good amount of originality, something that differs from the info I'm giving you; and lastly, it should be somewhat pioneering, aiming to focus on areas that haven't been touched on by others yet."
        try:
            if not command_para == '':request = command_para # 如果有设定自己的要求，就用这个了

            yield from __come_up_with_topic(request, summarization, GPT_prefer_language,llm_kwargs,system_prompt, chatbot,history)

        except Exception as e:
            yield from update_ui_lastest_msg(_("拟定课题出错了！错误原因是：\n{}").format(str(e)), chatbot, history)
        return

    # 其他情况下就当作与AI交流一下总结的内容了，保存了历史，之后就可以用普通对话了
    else:
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=f'Please answer me in {GPT_prefer_language}',# 再重复一次吧，有的憨憨会忘掉。。
            inputs_show_user=txt,   
            llm_kwargs=llm_kwargs,  
            chatbot=chatbot,        
            history=history,     
            sys_prompt=f"If you are asked about the origin or source of certain content, or if there is something else you are unsure about, please say: To determine the detailed content or to find the source, please use the 'find' command and the 'Fine-grained Analysis of Article' feature."
        )
        # 聊天完成之后，把历史改成总结内容与刚刚GPT的回复
        history.extend([txt, gpt_say])
        # 记录history，这样子就可以更新全局的history了
        yield from update_ui(chatbot=chatbot, history=history)
        return

execute = 与AI交流研究进展 # 用于热更新

def __find_article_from_summarization(library_root_dir: str, txt: str, gpt_prefer_lang: str, llm_kwargs,system_prompt, chatbot,history):
    """ 从总结中找到自己感兴趣的文章，提供文章下载 + 把这些感兴趣的文章的摘要放到历史记录中便于咨询

    Args:
        pdf_manifests_fp (list): pdf清单（md5.yml）列表
        start_batch (int): 这是第几个batch
        total_count (int): 总共有几个batch
        analyzed_folder_fp (str): analyzed文件夹的绝对路径
        llm_kwargs (_type_): _description_
        plugin_kwargs (_type_): _description_
        chatbot (_type_): _description_
        history (_type_): _description_
        system_prompt (_type_): _description_
        user_request (_type_): _description_

    """

    inputs_array = []
    inputs_show_user_array = []
    history_array = []
    sys_prompt_array = []

    repo_dir = os.path.join(library_root_dir, 'repository')
    tmp_dir = get_tmp_dir_of_this_user(chatbot,'find-origin',[os.path.basename(library_root_dir)])

    # 获取所有已经分析过的文章的yml，以便得到摘要/预分析结果、文件名
    all_analyzed_ymls = []
    for file in os.listdir(repo_dir):
        if file.endswith('yml'):
            all_analyzed_ymls.append(os.path.join(repo_dir,file))
            
    # 用于记录所有的预分析结果（在这里搜索）
    contents = []
    # 用于所有文章的文件名
    filenames = []
    # 用于记录符合要求文章的选定理由
    reason = []
    # 符合要求的文件名与预分析 以及 doi
    filenames_meet_requirement = []
    content_meet_requirement = []

    for yml_fp in all_analyzed_ymls:
        with open(yml_fp, "r") as file:
            yml = yaml.safe_load(file)
            contents.append(yml[pdf_yaml.analysis.value])
            filenames.append(yml[pdf_yaml.filename.value])

    # 多线程问GPT哪一篇文章符合用户的兴趣
    for index, content in enumerate(contents):

        i_say = \
        f'''Please respond in {gpt_prefer_lang}. Here's the [Article]: “{content}”.
            The [Query] is: “{txt}”.  
            [Query] may not be the exact wording from the [Article],
            but as long as the meanings are similar or there is some connection between the two, 
            [Query] can be considered a part of the [Article].
            If the two can be considered as part of each other or related, please reply with 'yes'; 
            if they are completely unrelated, please reply with 'nonono'. 
            Also, please share your reasoning for your decision.
            '''
        
        i_say_show_user = str(index) # 这里就不是给用户看的，是方便定位文章文件的
        
        # 装载请求内容，这里有四个列表，列表的长度就是子任务的数。比如10个文件，列表的长度就是10。
        inputs_array.append(i_say)
        inputs_show_user_array.append(i_say_show_user)
        history_array.append([])  # 因为是对每个文章的摘要单独进行总结的，所以这里不需要上下文也能分析
        sys_prompt_array.append(f"Make sure to let me know the reason for such a decision. Please respond in {gpt_prefer_lang}.")

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

    # < ----------------------------找到符合要求的文章---------------------------------------- >

    # 遍历GPT输出的结果
    for index, content in enumerate(gpt_response_collection):
        # 奇数，获取的是gpt_res，里面是GPT的回复 偶数是这个文章的index
        if index % 2 != 0:

            # 毕竟有时候AI会发飙..宁可错杀不能放过
            # After all, sometimes AI can go rogue — it's better to be safe than sorry.
            if 'yes' in content:
                # 找到符合要求的文章
                filenames_meet_requirement.append(filenames[int(gpt_response_collection[index - 1])])
                # 记录这个文章的总结内容
                content_meet_requirement.append(contents[int(gpt_response_collection[index - 1])])
                # 记录理由
                reason.append(content)

    # 把符合要求的文件整理一下，并把这些文章提供下载与历史记录（如果有）
    if len(filenames_meet_requirement) == 0:
        yield from update_ui_lastest_msg(_("搜索完成！暂时没有找到与搜索内容相匹配的文章。可以多尝试几次（<b>不排除AI出问题</b>），或与AI对总结内容进行交流")
                                        ,chatbot,history)
        return
    
    zip_fp = os.path.join(tmp_dir, "articles_retrieved.zip")
    # 把符合要求的文章放到压缩文件中
    with zipfile.ZipFile(zip_fp,'w') as zip:
        for index, name_no_extension in enumerate(filenames_meet_requirement):
            pdf_fp = os.path.join(repo_dir, f'{name_no_extension}.pdf')
            zip.write(pdf_fp,f'{name_no_extension}.pdf')
            # 理由也来一份
            reason_file_fp = os.path.join(tmp_dir, f'{name_no_extension}.txt')
            with open(reason_file_fp, 'w',encoding='utf-8') as file:
                file.write(reason[index])
            zip.write(reason_file_fp,f'{name_no_extension}.txt')

    # < ----------------------------信息输出---------------------------------------- >

    history.extend(content_meet_requirement)
    history.append(f'If asked for the reason, please refer to this content: {", ".join(reason)}')
    # 历史记录中有找到的文章的分析内容和原有
    
    line1 = _('搜索完成！')
    line2= _('有 <b>{}</b> 篇文章可能符合期望。在下面可以下载这些文章（以及选中的理由），此外现在<b>可以直接进行对话</b>、了解<b>这几篇</b>文章了').format(len(filenames_meet_requirement))
    line3 = _('对话文章仅包含摘要，如果要细致分析请使用 <b>精细分析文献</b> 工具')
    line4 = _('由于人工智能的能力各不相同，<b>回答的理由可能并不能使人满意</b>，请仔细鉴别')
    line5 = _('当对结果不满意时，可以重新搜索一次')
    line6 = _('[文章]：指文献。[搜索内容]：指左上角输入的、需要搜索的内容')
    yield from update_ui_lastest_msg(f"{line1}\n\
                                        {line2}\n\
                                        \n - {line3}\
                                        \n - {line4}\
                                        \n - {line5}\
                                        \n - {line6}"
                                        ,chatbot,history)
    
    chatbot.append([_('下载文章：'),generate_download_file(zip_fp)])
    yield from update_ui(chatbot=chatbot,history=history)
    

def __come_up_with_topic(request: str, summarization: str, GPT_prefer_language,llm_kwargs,system_prompt, chatbot,history):
    """根据总结的内容/摘要/预分析内容拟定一些课题

    Args:
        archive_folder_fp (str): _description_
        use_all_abstract (bool): 是要用所有的摘要/预处理吗
        ex_request (str): 用户的要求
        summarization (str): 总结的内容
        llm_kwargs (_type_): _description_
        chatbot (_type_): _description_

    Yields:
        _type_: _description_
    """

    # 输入给AI的内容：
    i_say = f'please answer me in {GPT_prefer_language}. \
        Now, I hope you can help me identify some topics. \
        The requirements for determining the topics are: {request}; \
        the information available for use in topic determination (these are also the experiences of predecessors) is as follows: {summarization}'

    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say,
        inputs_show_user=_("课题拟定中...") + '\n' +_("拟定要求: {}").format(request),
        llm_kwargs=llm_kwargs,
        chatbot=chatbot,
        history=[],
        sys_prompt=f'You are a professional professor skilled in proposing innovative topics. Now, I need some inspiration; please suggest several valuable and research-aligned topics for me. When you give me topics, please reply in Markdown format and inform me of the reasons for drafting the topic.'
    )
    yield from update_ui_lastest_msg(_('课题拟定完成！'),chatbot=chatbot,history=[])
    chatbot.append([_('下面是AI拟定的课题及其理由（此时亦可以追问）: '), gpt_say])
    history.append(f'Also, refer to this content for the conversation: {gpt_say}')
    yield from update_ui(chatbot=chatbot, history=history)


class Communicate_with_AI_about_research_progress(common_plugin_para):
    def define_arg_selection_menu(self):
        gui_definition = super().define_arg_selection_menu()
        gui_definition.update(self.add_lib_field(
            True, _('选择总结库'), _('可以在总结库中选择文章')))
        
        gui_definition.update(self.add_command_selector(
            ['draw', 'find','topic'], [_('绘制思维导图'), _('寻找总结内容来源'),_('拟定课题')], [True,True, True]))
        
        gui_definition.update(self.add_command_para_field(
            description=_('在此处输入思维导图类型代码/要溯源的内容/课题拟定要求')))
        
        gui_definition.update(self.add_GPT_prefer_language_selector())
        return gui_definition

    def execute(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
        yield from 与AI交流研究进展(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request)
