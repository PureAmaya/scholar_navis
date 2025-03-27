from gradio.components.base import Component
import gradio as gr
import weakref
from abc import ABC, abstractmethod
from i18n import text_i18n

def copy_parameters(source_cls):
    """装饰器：将源类的参数复制到目标类"""
    def decorator(target_cls):
        original_init = source_cls.__init__
        def new_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)  # 调用源类的 __init__
            target_cls.__init__(self, *args, **kwargs)  # 调用目标类的 __init__
        target_cls.__init__ = new_init
        return target_cls
    return decorator


class base_component(ABC):
    _instances = weakref.WeakSet() # 弱引用防止内存泄漏

    def __init__(self):
        super().__init__()
        base_component._instances.add(self)
    
    @classmethod
    def get_list(cls):
        return list(cls._instances)
    
    @classmethod
    def update_component(cls,i18n:text_i18n,target_language:str):
        i18n.update(target_language)

        _list = []
        for instance in cls._instances:
            _dict = {}
            try:
                _dict.update({'value': instance.value})
            except:
                pass
            try:
                _dict.update({'label': instance.label})
            except:
                pass
            try:
                _dict.update({'placeholder': instance.placeholder})
            except:
                pass
            _list.append(gr.update(**_dict))
        return _list
        

from gradio.events import Dependency

class Textbox(gr.Textbox,base_component):
    def __init__(self,**kwargs: int | str | float):
        return super().__init__(**kwargs)
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer
    
class Markdown(gr.Markdown,base_component):
    def __init__(self,text: str, **kwargs: int | str | float):
        return super().__init__(text,**kwargs)
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer
    
class Button(gr.Button,base_component):
    def __init__(self,label: str, **kwargs: int | str | float):
        return super().__init__(label,**kwargs)
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer
    
class HTML(gr.HTML,base_component):
    def __init__(self,html: str, **kwargs: int | str | float):
        return super().__init__(html,**kwargs)
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer