# ! 后续，这个会慢慢的取代gpt_academic自带的multi_language.py，逐步用一套体系完成多语言的开发

import os
import gettext
from .sn_config import CONFIG
from .const import SCHOLAR_NAVIS_ROOT_PATH

class _i18n:
    def __init__(self) -> None:
        pass

    def __init__(self):
        self.update()

    def gettext(self,msg:str):
        return self.trans.gettext(msg)

    def update(self):
        # 更新语言环境
        i18n_root_path = os.path.join(SCHOLAR_NAVIS_ROOT_PATH,'i18n')
        selected_lang_dir = os.path.join(SCHOLAR_NAVIS_ROOT_PATH,'i18n',CONFIG['language_display'])
        # 语言不存在，临时用中文语言包吧
        if not  os.path.exists(selected_lang_dir):CONFIG['language_display'] = 'zh-Hans'
        self.trans = gettext.translation('Scholar_Navis', i18n_root_path, [CONFIG['language_display']])

i18n = _i18n()
_ = i18n.gettext


'''
    def gettext(self,msg:str):
        return self.trans.gettext(msg)
    
    l = i18n.gettext
    
    这样子写，update就可以更新语言
    
    但如果这样子写：
    
    def gettext(self):
        return self.trans.gettext
    
    l = i18n.gettext()
    
    return的内容就被缓存到l里了，update也就没法用了
    
    * 仅供理解


'''







