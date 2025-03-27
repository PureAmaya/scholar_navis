'''
Author: scholar_navis@PureAmaya
'''

import gradio as gr

from gradio.events import Dependency

class Textbox(gr.Textbox):
    def style(self,**kwargs):
        self.container = kwargs['container']
        return self
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer
    
class Row(gr.Row):
    def style(self,**kwargs):
        self.equal_height = kwargs['equal_height']
        return self
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer
    
class Button(gr.Button):
    def __init__(self, value = "Run", *, every = None, inputs = None, variant = "secondary", size = None, icon = None, link = None, visible = True, interactive = True, elem_id = None, elem_classes = None, render = True, key = None, scale = None, min_width = None,info_str=None):
        super().__init__(value, every=every, inputs=inputs, variant=variant, size=size, icon=icon, link=link, visible=visible, interactive=interactive, elem_id=elem_id, elem_classes=elem_classes, render=render, key=key, scale=scale, min_width=min_width)
    
    def style(self,**kwargs):
        self.size = kwargs['size']
        return self
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer

class Dropdown(gr.Dropdown):
    def style(self,**kwargs):
        self.size = kwargs['container']
        return self
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer
    
class JSON(gr.JSON):
    def __init__(self, value = None, *, label = None, every = None, inputs = None, show_label = None, container = True, scale = None, min_width = 160, visible = True, elem_id = None, elem_classes = None, render = True, key = None, open = False, show_indices = False, height = None, max_height = 500, min_height = None,interactive=None):
        super().__init__(value, label=label, every=every, inputs=inputs, show_label=show_label, container=container, scale=scale, min_width=min_width, visible=visible, elem_id=elem_id, elem_classes=elem_classes, render=render, key=key, open=open, show_indices=show_indices, height=height, max_height=max_height, min_height=min_height)
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer

class CheckboxGroup(gr.CheckboxGroup):    
    def style(self,**kwargs):
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
    def __getitem__(self, index:int):
        return self.content
    
    def __setitem__(self, index:int, value): 
        self.content = value
        