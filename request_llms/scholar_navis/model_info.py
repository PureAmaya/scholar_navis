'''
Author: scholar_navis@PureAmaya
'''

class model_info_class:
    def __init__(self,data: dict,fn):
        """_summary_

        Args:
            fn (function): 就是bridge_all.py里的local_llm_support（处理one-api的标签）
        """
        self._data = data  # 内部使用一个字典来存储数据
        self.fn =fn
    
    def __getitem__(self, model:str):
        
        if model in self._data:
            return self._data[model] # 返回的是fn_with_ui，fn_without_ui这些
        else: # 如果不存在，通过fn返回
            if model.startswith('ollama-'): label = 'ollama-'
            elif model.startswith('one-api-'): label = 'one-api-'
            elif model.startswith('vllm-'): label = 'vllm-'
            elif model.startswith('custom-'): label = 'custom-'
            return self.fn([model],label)[model]
            
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def __delitem__(self, key):
        if key in self._data:
            del self._data[key]
    
    def __contains__(self, key):
        return key in self._data
    
    def __str__(self):
        return str(self._data)
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def update(self,dict: dict):
        self._data.update(dict)