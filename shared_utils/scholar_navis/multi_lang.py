'''
Author: scholar_navis@PureAmaya
'''

import os
import gettext
from shared_utils.config_loader import get_conf
from .const_and_singleton import GPT_ACADEMIC_ROOT_PATH,SUPPORT_DISPLAY_LANGUAGE

LANGUAGE_DISPLAY = get_conf('LANGUAGE_DISPLAY')

class _i18n:
    def __init__(self) -> None:
        global LANGUAGE_DISPLAY
        if LANGUAGE_DISPLAY not in SUPPORT_DISPLAY_LANGUAGE:
            print(f'{LANGUAGE_DISPLAY} 是无效的语言设定，将使用默认语言 zh-Hans（简体中文）\n{LANGUAGE_DISPLAY} is invalid language, defaulting to zh-Hans (Simplified Chinese).')
            LANGUAGE_DISPLAY = 'zh-Hans'
        self.update()

    def gettext(self,msg:str):
        return self.trans.gettext(msg)

    def update(self):
        # 更新语言环境
        i18n_root_path = os.path.join(GPT_ACADEMIC_ROOT_PATH,'i18n')
        #selected_lang_dir = os.path.join(GPT_ACADEMIC_ROOT_PATH,'i18n',LANGUAGE_DISPLAY)
        self.trans = gettext.translation('Scholar_Navis', i18n_root_path, [LANGUAGE_DISPLAY])

i18n = _i18n()
_ = i18n.gettext

selected_language = LANGUAGE_DISPLAY
'''目前选定的语言（显示）'''


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







