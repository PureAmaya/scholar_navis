from gradio.components.base import Component
import gradio as gr
import weakref
from abc import ABC, abstractmethod

from gradio.components.browser_state import BrowserState

from dependencies.i18n import text_i18n

# 需要翻译的所有的组件
TRACKED_COMPONENTS_FOR_I18N = weakref.WeakSet()

class TranslatableMixin:
    """一个 Mixin 类，用于添加追踪和原始文本存储逻辑"""
    # 定义哪些属性需要追踪，子类可以覆盖
    _translatable_attrs = [] # 例如: [('value', 'value_kwarg')]

    def _track_for_i18n(self, **kwargs):
        self._original_translatable_texts = {}
        component_has_translatables = False
        # 获取当前类实际需要追踪的属性
        attrs_to_track = getattr(self, '_translatable_attrs', [])

        for attr_name, kwarg_name in attrs_to_track:
            original_text = None
            # 优先检查 kwargs
            if kwarg_name in kwargs and isinstance(kwargs[kwarg_name], str):
                original_text = kwargs[kwarg_name]
            else:
                 # 也可以尝试从 args 获取，但这比较复杂，需要知道参数顺序
                 # 建议强制使用 kwargs
                 pass

            if original_text is not None:
                self._original_translatable_texts[attr_name] = original_text
                component_has_translatables = True

        if component_has_translatables:
            TRACKED_COMPONENTS_FOR_I18N.add(self)

from gradio.events import Dependency

class Button(gr.Button, TranslatableMixin):
    _translatable_attrs = [('value', 'value')]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._track_for_i18n(**kwargs)

    # 兼容gpt_academic旧的gradio用法，下同
    def style(self, **kwargs):
        self.size = kwargs['size']
        return self
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer

class Textbox(gr.Textbox, TranslatableMixin):
    _translatable_attrs = [('value','value'),('info','info'),('label', 'label'), ('placeholder', 'placeholder')]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._track_for_i18n(**kwargs)

    def style(self, **kwargs):
        self.container = kwargs['container']
        return self
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer


class Tab(gr.Tab, TranslatableMixin):
    _translatable_attrs = [('label','label')]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._track_for_i18n(**kwargs)
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer

class Row(gr.Row):
    def style(self, **kwargs):
        self.equal_height = kwargs['equal_height']
        return self
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer


class Dropdown(gr.Dropdown):
    def style(self, **kwargs):
        self.size = kwargs['container']
        return self
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer


class CheckboxGroup(gr.CheckboxGroup):
    def style(self, **kwargs):
        self.container = kwargs['container']
        return self
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer


class Blocks(gr.Blocks):
    def startup_events(self):
        return self.run_startup_events()


class ChatMessage(gr.ChatMessage):
    def __getitem__(self, index: int):
        return self.content

    def __setitem__(self, index: int, value):
        self.content = value



# 不需要修改的gradio组件（暂时先这么写）
Column = gr.Column
State = gr.State
HTML = gr.HTML
Chatbot = gr.Chatbot
Accordion = gr.Accordion
Markdown = gr.Markdown
update = gr.update
Request = gr.Request
Files = gr.Files
Slider = gr.Slider
BrowserState = gr.BrowserState
JSON = gr.JSON
TextArea = gr.TextArea