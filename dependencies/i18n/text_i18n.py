import gettext
import logging
import os
from functools import lru_cache
from importlib.resources import files, as_file
import inspect

SUPPORT_DISPLAY_LANGUAGE = ("zh-Hans", "zh-Hant", "en-US")
SUPPORT_DISPLAY_LANGUAGE_TUPLE =[('简体中文',"zh-Hans"),('繁體中文', "zh-Hant"),('English', "en-US")]


# 获取资源目录的 Traversable 对象
lang_dir = files(__package__).joinpath("lang")

@lru_cache() # 缓存翻译器加载结果
def load_all_translations():
    """应用启动时加载所有支持语言的翻译器"""
    translations = {}

    # 更新语言环境
    with as_file(lang_dir) as i18n_root_path:
        for lang_code in SUPPORT_DISPLAY_LANGUAGE:
            try:
                translator = gettext.translation('Scholar_Navis', i18n_root_path, [lang_code],fallback=True)
                translations.update({lang_code:translator})
                if translator.info() == {}:
                    print(f"Warning: Translation for '{lang_code}' not found or failed. Using fallback.")
                else:
                    pass
            except Exception as e:
                print(f"Error loading translation for language '{lang_code}': {e}")
                # 出错时也提供空翻译器
                translations.update({lang_code: gettext.NullTranslations()})

    return translations

ALL_TRANSLATIONS = load_all_translations()


@lru_cache(maxsize=len(SUPPORT_DISPLAY_LANGUAGE)) # 缓存 get_translator 的结果
def get_translator(language_code):
    """根据语言代码获取预加载的翻译器实例"""

    if not language_code:
        raise ValueError("language cannot be empty")
    if language_code not in SUPPORT_DISPLAY_LANGUAGE:
        print(f'{language_code} is invalid language, defaulting to zh-Hans (Simplified Chinese).')
        language = 'zh-Hans'# 默认语言

    # 从预加载的字典获取，如果失败则回退到默认语言，再失败则回退到空翻译器
    return ALL_TRANSLATIONS.get(language_code, ALL_TRANSLATIONS.get('zh-Hans', gettext.NullTranslations()))
