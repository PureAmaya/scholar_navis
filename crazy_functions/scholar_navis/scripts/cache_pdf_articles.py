import os
import yaml
import glob
import shutil
from shared_utils.multi_lang import _
from shared_utils.sn_config import VERSION
from ...crazy_utils import get_files_from_everything
from .tools.common_plugin_para import common_plugin_para
from .tools.article_library_ctrl import check_library_exist_and_assistant, lib_manifest
from toolbox import CatchException, get_log_folder, get_user, update_ui, update_ui_lastest_msg

@check_library_exist_and_assistant(accept_nonexistent=True, accept_blank=False)
@CatchException
def 缓存pdf文献(txt: str, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    """
    把加载的文章缓存到cache文件夹中。cache中的文章AI不会用于分析。

    txt: 输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs: gpt模型参数, 如温度和top_p等, 一般原样传递下去就行
    plugin_kwargs: 插件的参数
    chatbot: 聊天显示框的句柄，用于显示给用户，一旦分行（输入逗号）就换说话人
    history: 聊天历史，前情提要
    system_prompt: 给gpt的静默提醒
    user_request: 当前用户的请求信息（IP地址等）
    """

    # < -------------------- 读取插件的参数，准备文件夹 --------------- >
    library_name = plugin_kwargs['lib']
    command = plugin_kwargs['command']
    command_para = plugin_kwargs['command_para']

    # 操作的总结库的根目录
    this_library_root_dir = os.path.join(get_log_folder(
        user=get_user(chatbot), plugin_name='scholar_navis'), library_name) # ? 要不要后面把这个放到修饰器里？
    # 缓存与储存目录
    cache_dir = os.path.join(this_library_root_dir, 'cache')
    repo_dir = os.path.join(this_library_root_dir, 'repository')
    manifest_fp = os.path.join(this_library_root_dir, 'lib_manifest.yml')

    # 单独为新建总结库处理一下情况
    if (not os.path.exists(manifest_fp)):
        # 并且没有上传任何可用的文件，提醒后终止程序
        if txt == '' or (not os.path.exists(txt)):# 顺便阻止意外的建立文件夹
            chatbot.append([_("<b>{}</b> 是一个不存在的总结库").format(library_name),
                            _("可以通过上传文章（含压缩包）的方式创建新的总结库")])
            yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
            return
        # 有上传文章，就单独提醒一下就行
        else:
            chatbot.append([_("即将创建一个新的总结库：<b>{}</b>").format(library_name),
                            _("库内将包含您上传的所有文章")])
            yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面

    # < --------------------  事前准备  --------------- >

    if not os.path.exists(this_library_root_dir):
        os.mkdir(this_library_root_dir)
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    if not os.path.exists(repo_dir):
        os.mkdir(repo_dir)

    # 准备好manifest文件
    manifest_dict = None
    if not os.path.exists(manifest_fp):
        manifest_dict = {lib_manifest.library_name.value: library_name,
                         lib_manifest.version.value: VERSION,
                         lib_manifest.key_words.value: []}

        with open(manifest_fp, 'w') as f:
            f.write(yaml.safe_dump(manifest_dict))
    else:
        with open(manifest_fp, 'r') as f:
            manifest_dict = yaml.safe_load(f)


    # 获取必要的信息
    old_keywords = manifest_dict[lib_manifest.key_words.value]
    pdfs_in_cache = glob.glob(f"{cache_dir}/*.pdf")
    summarization_file_fp = os.path.join(this_library_root_dir, "summarization.txt")
    pdfs_in_repo = glob.glob(f"{repo_dir}/*.pdf")  # 测试过了，路径不存在返回[]

    # 检查完成状态
    workflow_done = len(pdfs_in_cache) == 0 and len(
        pdfs_in_repo) > 1 and os.path.exists(summarization_file_fp)

    # < --------------------用户输入：缓存新的pdf--------------- >

    # 要添加新的文章
    if os.path.exists(txt) or txt.lower().startswith('http'):
        chatbot.append([_("接收文章中"),
                                _("正在处理...")])
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
        
        if workflow_done:
            yield from update_ui_lastest_msg(_('文章接收终止，因为已经完成了总结分析'),chatbot,history)
            return

        _1, pdfs_user_uploaded, _2 = get_files_from_everything(txt, type='.pdf')
        if len(pdfs_user_uploaded) == 0:
            chatbot.append([_("没有上传pdf，或者尚未上传任何文件"),
                            _("在左上角上传文献后（支持单个pdf与压缩包），再执行本插件")])
            yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
            return

        # 记录导入文章之前，缓存中有几篇文章
        old_cache_count = len(pdfs_in_cache)

        # 把所有需要分析的pdf放到缓存中。没有文章的话也没问题，移动数量会显示0，不影响总数的显示
        for pdf_user_uploaded in pdfs_user_uploaded:
            dst = os.path.join(cache_dir, os.path.basename(pdf_user_uploaded))
            shutil.move(pdf_user_uploaded, dst)

        # 记录导入文章之后，缓存中有几篇文章
        new_cache_count = len(glob.glob(f'{cache_dir}/*.pdf'))

        chatbot.append(
            [_("pdf加载成功"),
             _("本次<b>上传{upload_count}篇</b>文章，<b>新加载{new_count}篇</b>文章，<b>总计{cache_count}篇</b>文章存在于缓存中待分析（已有<b>{repo}篇</b>文章分析完毕）")
             .format(upload_count=len(pdfs_user_uploaded), new_count=new_cache_count - old_cache_count, cache_count=new_cache_count, repo=len(glob.glob(f'{repo_dir}/*.yml')))
             ])
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面

    # < --------------------更新关键词 --------------- >

    # 查看关键词
    if command == 'key' and command_para == '':
        chatbot.append([_("<b>{}</b>文献总结库目前的关键词如下").format(library_name), ""])
        if old_keywords == []:
            yield from update_ui_lastest_msg(_('目前没有关键词。请创建新的关键词，将用于分析总结'), chatbot, [])
        else:
            yield from update_ui_lastest_msg(f"{'<br>'.join(old_keywords)}", chatbot, [])
        return

    # 更新关键词
    elif command.startswith('key') and command_para != '':

        chatbot.append(
            [_("更新<b>{}</b> 文献总结库的关键词").format(library_name), _("正在处理...")])
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面

        if workflow_done:
            yield from update_ui_lastest_msg(_('关键词更新终止，因为已经完成了总结分析'),chatbot,history)
            return

        # 获取新输入的关键词
        new_keywords = []
        if len(command_para.split(',')) > len(command_para.split('，')):
            _new_keywords = command_para.split(',')
        else:
            _new_keywords = command_para.split('，')
        for key in _new_keywords:
            new_keywords.append(key.strip())

        # 已经有关键词了，然后强制更新
        if len(old_keywords) > 0 and command == 'key-force':
            manifest_dict[lib_manifest.key_words.value] = new_keywords
            with open(manifest_fp, 'w') as f:
                f.write(yaml.safe_dump(manifest_dict))
            yield from update_ui_lastest_msg(_('关键词已更新</br></br><b>现在的关键词为：</b></br>{new}</br></br><b>此前的关键词为：</b></br>{old}')
                                                .format(new="<br>".join(new_keywords), old="<br>".join(old_keywords)), chatbot, [])
            old_keywords = new_keywords

        # 已经有关键词了，但是不强制更新
        elif len(old_keywords) > 0 and command == 'key':
            yield from update_ui_lastest_msg(_('已存在关键词，不会进行修改（如果还没有总结，可以试试关键词强制更新）</br></br><b>现在的关键词为：</b></br>{}')
                                            .format("<br>".join(old_keywords)), chatbot, [])

        # 还没关键词，是否强制随意了
        elif len(old_keywords) == 0:
            manifest_dict[lib_manifest.key_words.value] = new_keywords
            with open(manifest_fp, 'w') as f:
                f.write(yaml.safe_dump(manifest_dict))
            yield from update_ui_lastest_msg(_('关键词已更新</br></br><b>现在的关键词为：</b></br>{new}')
                                            .format(new="<br>".join(new_keywords)), chatbot, [])
            old_keywords = new_keywords

    # < --------------------检查该项工具的流程是否全部完成。--------------- >
    # manifest_fp 直接没了。
    if not os.path.exists(manifest_fp):
        chatbot.append([_("该总结库已损坏：缺少lib_manifest.yml"),
                        _("请尝试重新创建该总结库")])
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
        return

    # 检查一下有没有关键词，没有的话提醒一下。
    with open(manifest_fp, 'r') as f:
        if yaml.safe_load(f)[lib_manifest.key_words.value] == []:
            chatbot.append([_("缺乏关键词，无法总结分析"),
                            _("可以使用 <b>key + 关键词</b> 命令设定新的关键词")])
            yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
            return

    # 看看有没有文章，没有的话也提醒一下
    pdfs_in_cache = glob.glob(f"{cache_dir}/*.pdf")

    if len(pdfs_in_cache) + len(pdfs_in_repo) == 0:
        chatbot.append([_("不存在任何可用pdf，无法总结分析"), _(
            "可以使用 <b>缓存pdf文献</b> 缓存新的文章。")])
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
        return

    chatbot.append([_('所有的工序已经完成，该工具的流程结束。<ul><li>已导入pdf数量：{in_cache}(缓存中), {in_repo}(库中)</li><li>关键词：{keywords}</li></ul>')
                    .format(in_cache=len(pdfs_in_cache), in_repo=len(pdfs_in_repo), keywords=", ".join(old_keywords)),
                    _("在使用 <b>按关键词总结文献</b> 进行AI总结之前，您可以选择继续添加文章、修改关键词。")])
    yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面

execute = 缓存pdf文献 # 用于热更新

class pdf_cacher(common_plugin_para):
    def define_arg_selection_menu(self):
        gui_definition = {}
        gui_definition.update(self.add_file_upload_field(
            description=_('上传1篇pdf文献或多篇pdf的压缩包')))
        gui_definition.update(self.add_lib_field(
            True, _('创建或选择总结库'), _('如要创建新的总结库，请输入一个新名字')))
        gui_definition.update(self.add_command_selector(
            ['key', 'key-force'], [_('查询或更新关键词'), _('强制更新关键词')], [True, True]))
        gui_definition.update(self.add_command_para_field(
            description=_('在此处输入用于更新的关键词（中英文逗号分割）')))
        return gui_definition

    def execute(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
        yield from 缓存pdf文献(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request)
