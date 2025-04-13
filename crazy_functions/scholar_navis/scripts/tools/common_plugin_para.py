'''
Author: scholar_navis@PureAmaya
'''

from abc import ABC, abstractmethod
from multi_language import init_language
from shared_utils.scholar_navis.const_and_singleton import GPT_SUPPORT_LAMGUAGE
from shared_utils.config_loader import get_conf
from crazy_functions.plugin_template.plugin_class_template import GptAcademicPluginTemplate, ArgProperty

AUTHENTICATION,LANGUAGE_GPT_PREFER,PRIORITIZE_USE_AI_ASSISTANCE = get_conf('AUTHENTICATION','LANGUAGE_GPT_PREFER','PRIORITIZE_USE_AI_ASSISTANCE')


# ! 后续考虑一下用js的方式暂存输入的内容

class common_plugin_para(GptAcademicPluginTemplate,ABC):
    """再次封装的插件面板（
        只需要重写define_arg_selection_menu和execute就行
        减少不必要的重复劳动（

    """

    def __link_command(self,command:str,command_natural_language:str,need_para: bool):
        """ 注册命令（将自然语言与命令本体连接起来）
            连接后形如： help: 帮助文档

        Args:
            command (str): 命令本体
            command_natural_language (str): 自然语言描述 
            need_para (bool): 是否需要参数

        Returns:
            命令本体: 自然描述
        """
        
        if need_para:
            return f'{command}: {command_natural_language} ({self._('需要参数')})'
        else:
            return f'{command}: {command_natural_language}'
        
    def add_file_upload_field(self,title: str=None,description : str=None):
        """现在把主输入直接定义成文本上传了，减少上手难度

        Args:
            title (str, optional):自定义标题。默认值：文件上传路径或网址
            description (str, optional): 自定义描述（不要加标点符号和括号）  默认值：请上传文件后，再点击该插件

        Returns:
            gui_definition直接可以用的参数
        """
        title = self._('文件上传路径或网址')
        description = self._('请上传文件后，再点击该插件')
        
        return  {"main_input":ArgProperty(title=title, description=description , default_value="", type="string").model_dump_json()} # 主输入，自动从输入框同步
    
    def add_command_selector(self,command: list[str],command_natural_lang: list[str],need_command_para: list[bool],default_value:str = None):
        """添加命令用的东西。默认的命令已经添加了  plugin_kwargs['command']
        help license about 这些东西就已经有啦

        Args:
            command (list[str]): 命令本体
            command_natural_lang (list[str]): 除了help等命令的，使用简短的自然语言。无需写明命令本体
            need_command_para (list[bool]): 这些额外的命令需要参数吗（需要的话会给一个提示）

        Returns:
            gui_definition直接可以用的参数
        """

        assert len(command) == len(command_natural_lang) == len(need_command_para)

        if not default_value:default_value = self._ ('无')
        else: assert default_value in command
        
        command_to_show = [self._('无')]
        if len(command) >= 1:
            for index , natural_lang in enumerate(command_natural_lang):
                # 注册额外的指令
                command_with_natural_description = self.__link_command(command[index],natural_lang,need_command_para[index])
                command_to_show.append(command_with_natural_description)
                # 也为默认值补全自然语言描述
                if default_value == command[index]:default_value = command_with_natural_description

        # 三个通用的命令
        command_to_show.extend([self.__link_command('help',self._ ('帮助文档'),False),
                        self.__link_command('license',self._ ('版权信息'),False),
                        self.__link_command('about',self._ ('关于'),False)])
        para =  {'title':self._ ('辅助指令'),'description':self._ ('使用辅助指令可以实现额外的操作'),'options':command_to_show,'default_value':default_value,'type':"dropdown"}
        return {'command':ArgProperty(**para).model_dump_json()}


    def add_command_para_field(self,title:str =None,description :str = None):
        """如果有的命令需要参数，再加上这个

        Returns:
            gui_definition直接可以用的参数
        """
        title = self._('指令参数')
        description = self._('如需要，在此处输入辅助指令的参数')

        return  {"command_para":ArgProperty(title=title, description=description, default_value="", type="string").model_dump_json()} # 主输入，自动从输入框同步


    def add_lib_field(self,always_field:bool,title:str=None,description:str = None):
        """ 如果需要选择总结库，gui_definition就加上这个

        Args:
            always_field (bool): 总是要用输入框（而不是下拉框）吗
            title (str, optional): 标题. Defaults to 总结库.
            description (str, optional): 描述. Defaults to 选择总结库进行操作.

        Returns:
            gui_definition直接可以用的参数
        """
        title = self._('总结库')
        description = self._('选择总结库进行操作')

        always_field =True # 先暂时总是使用输入框吧，啥时候前端的下拉列表是动态的再去掉这个
        
        # 如果没有设定用户（也没有总是要求输入框），即所谓的默认用户，就使用下拉式的总结库选择栏
        if not AUTHENTICATION and (not always_field):
            pass
            all = [self._('不选择')]
            all.extend(get_def_user_library_list())
            para = {'title':title,'description':description,'options':all,'default_value':self._('不选择'),'type':"dropdown"}
        # 如果设定用户了（或者要求总是有输入框），就先暂时用传统的输入总结库的方法把（同样的，如果总结库不存在，还是会给提示的
        else:
            para = {'title':title,'description':description,'default_value':'','type':"string"}
        return {'lib':ArgProperty(**para).model_dump_json()}
        
    def add_GPT_prefer_language_selector(self):
        """添加一个GPT偏好语言选择器

        Returns:
            gui_definition直接可以用的参数
        """
        try:
            index = GPT_SUPPORT_LAMGUAGE.index(LANGUAGE_GPT_PREFER)
        except:
            index = GPT_SUPPORT_LAMGUAGE.index('English')
        
        para = {'title':self._('调整GPT偏好语言'),'description':self._('LLM通常会按照此语言进行回答'),'options':GPT_SUPPORT_LAMGUAGE,'default_value':GPT_SUPPORT_LAMGUAGE[index],'type':"dropdown"}
        return {'gpt_prefer_lang':ArgProperty(**para).model_dump_json()}
    
    def add_use_AI_assistant_selector(self):
        if PRIORITIZE_USE_AI_ASSISTANCE:default = self._('启用')
        else:default = self._('禁用')
        
        para = {'title':self._('使用AI辅助功能'),'description':self._('AI补全信息，速度较慢'),'options':[self._('启用'),self._('禁用')],'default_value':default,'type':"dropdown"}
        return {'ai_assist':ArgProperty(**para).model_dump_json()}
    
    def define_arg_selection_menu(self,lang):
        """规范化的添加菜单。gui_definition可以添加下面这些东西（别忘了return）
        - add_file_uploader: 主输入框，主要是负责了文件上传
        - add_lib_selector: 总结库选择器
        - add_command_selector: 添加命令（包含了help等默认命令）
        - add_command_para_field: 如果命令需要参数，添加一个这个

        """
        self._  = lambda text: init_language(text, lang)
        return self.add_command_selector([],[],[])
    
        
    @abstractmethod
    def execute(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
        """ 开一个新的线程执行该方法
            (check_library_exist_and_assistant负责处理就行，execute只要执行该执行的方法就行)
            
        - plugin_kwargs['command']: 命令本体: 自然语言描述 .  l('无'): 不选择任何命令.  经过check_library_exist_and_assistant处理成只有命令本体的
        - txt: 主输入。在这里就是指文件上传框
        - plugin_kwargs['lib']: 输入的总结库. 
        - plugin_kwargs['command_para']: 命令的参数
        - plugin_kwargs['gpt_prefer_lang']: GPT偏好语言
        - plugin_kwargs['ai_assist']: AI辅助获取文献信息
        """
        pass
    
    

# 关于为什么要这样做：因为写好工具之前是没有这个面板的，为了兼容后续加上去的（
# 而且这样子做不影响从输入框中执行命令，感觉还可以
