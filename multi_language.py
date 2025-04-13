'''
The file of the same name was originally written by gpt_academic@binary-husky.
Now, due to abandoning the original localization method,
the source code has been completely removed and replaced with code from Scholar Navis@PureAmaya.
'''

from typing import Literal
from dependencies.i18n import get_translator
from dependencies.i18n.gradio_i18n import TRACKED_COMPONENTS_FOR_I18N
from shared_utils.config_loader import get_conf
from gradio import update

LANGUAGE_DISPLAY, MULTILINGUAL = get_conf('LANGUAGE_DISPLAY', 'MULTILINGUAL')


def init_language(text: str, specified_language: Literal["zh-Hans", "zh-Hant", "en-US"] = None):
    """
    初始化语言
    """
    if specified_language and MULTILINGUAL:  # 指定语言  + 允许多语言
        return get_translator(specified_language).gettext(text)
    return get_translator(LANGUAGE_DISPLAY).gettext(text)  # 没有指定语言就用设定的语言


# 暂时废弃
def change_language_for_gradio(language_state, new_language_code, tracked_components_list):
    """
    当语言下拉框变化时调用。
    更新 language_state 和所有被追踪组件的文本。
    接收 new_language_code 和当前的追踪组件列表快照。
    """

    # a. 获取新语言的翻译器
    translator = get_translator(new_language_code)

    # b. 准备更新指令字典
    updates_dict = {language_state: new_language_code}  # 更新状态
    processed_count = 0

    # c. 遍历传入的组件列表快照
    #    (理论上也可以直接用全局 TRACKED_COMPONENTS_FOR_I18N，但传入快照更明确)
    current_tracked_components = list(TRACKED_COMPONENTS_FOR_I18N)
    for component in current_tracked_components:
        if not hasattr(component, '_original_translatable_texts'): continue
        component_updates = {}
        original_texts = getattr(component, '_original_translatable_texts', {})
        attrs_to_update = getattr(component, '_translatable_attrs', [])
        for attr_name, kwarg_name in attrs_to_update:
            if attr_name in original_texts:
                original_key = original_texts[attr_name]
                if isinstance(original_key, str):
                    translated_text = translator.gettext(original_key)
                    component_updates[attr_name] = translated_text
        if component_updates:
            updates_dict[component] = update(**component_updates)
            processed_count += 1

    expected_outputs_order = [language_state] + tracked_components_list

    # f. 返回更新字典 (Gradio 会处理)
    result_list = []
    for output_component in expected_outputs_order:
        # Get the corresponding value from our updates dict.
        # Use a default of gr.update() if a component in the output list
        # somehow didn't get an update (safer than returning None).
        update_value = updates_dict.get(output_component, update())
        result_list.append(update_value)
    return result_list
