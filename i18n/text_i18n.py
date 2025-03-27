import os
import gettext
from importlib.resources import files, as_file


SUPPORT_DISPLAY_LANGUAGE = ("zh-Hans", "zh-Hant", "en-US")

# 获取资源目录的 Traversable 对象
lang_dir = files(__package__).joinpath("lang")

class text_i18n:
    def __init__(self,language:str) -> None:
        if not language:
            raise ValueError("language cannot be empty")
        if language not in SUPPORT_DISPLAY_LANGUAGE:
            print(f'{language} is invalid language, defaulting to zh-Hans (Simplified Chinese).')
            language = 'zh-Hans'
        self.update(language)

    def gettext(self,msg:str) -> str:
        return self.trans.gettext(msg)

    def update(self,language:str):
        # 更新语言环境
        with as_file(lang_dir) as i18n_root_path:
            #selected_lang_dir = os.path.join(GPT_ACADEMIC_ROOT_PATH,'i18n',LANGUAGE_DISPLAY)
            self.trans = gettext.translation('Scholar_Navis', i18n_root_path, [language])