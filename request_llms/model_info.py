# 由 scholar_navis添加

class model_info_class:
    def __init__(self,data: dict,fn):
        """_summary_

        Args:
            fn (function): 就是bridge_all.py里的local_llm_support（处理one-api的标签）
        """
        self._data = data  # 内部使用一个字典来存储数据
        self.fn =fn
    
    def __getitem__(self, key:str):
        
        if key in self._data:
            return self._data[key] # 返回的是fn_with_ui，fn_without_ui这些
        else: # 如果不存在，通过fn返回
            if key.startswith('ollama-'): label = 'ollama-'
            elif key.startswith('one-api-'): label = 'one-api-'
            elif key.startswith('vllm-'): label = 'vllm-'
            elif key.startswith('custom-'): label = 'custom-'
            return self.fn([key],label)[key]
            
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def __delitem__(self, key):
        if key in self._data:
            del self._data[key]
    
    def __contains__(self, key):
        return key in self._data
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def update(self,dict: dict):
        self._data.update(dict)