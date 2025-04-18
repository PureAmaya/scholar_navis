'''
Original Author: gpt_academic@binary-husky
'''

model_name = "ChatGLM3"
cmd_to_install = "`pip install -r request_llms/requirements_chatglm.txt`"


from toolbox import ProxyNetworkActivate
from shared_utils.config_loader import get_conf
from .local_llm_class import LocalLLMHandle, get_local_llm_predict_fns


# ------------------------------------------------------------------------------------------------------------------------
# 🔌💻 Local Model
# ------------------------------------------------------------------------------------------------------------------------
class GetGLM3Handle(LocalLLMHandle):

    def load_model_info(self):
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 子进程执行
        self.model_name = model_name
        self.cmd_to_install = cmd_to_install

    def load_model_and_tokenizer(self):
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 子进程执行
        from transformers import AutoModel, AutoTokenizer
        import os, glob
        import os
        import platform

        LOCAL_MODEL_QUANT, device = get_conf("LOCAL_MODEL_QUANT", "LOCAL_MODEL_DEVICE")
        _model_name_ = "THUDM/chatglm3-6b"
        # if LOCAL_MODEL_QUANT == "INT4":  # INT4
        #     _model_name_ = "THUDM/chatglm3-6b-int4"
        # elif LOCAL_MODEL_QUANT == "INT8":  # INT8
        #     _model_name_ = "THUDM/chatglm3-6b-int8"
        # else:
        #     _model_name_ = "THUDM/chatglm3-6b"  # FP16
        with ProxyNetworkActivate("Download_LLM"):
            chatglm_tokenizer = AutoTokenizer.from_pretrained(
                _model_name_, trust_remote_code=True
            )
            if device == "cpu":
                chatglm_model = AutoModel.from_pretrained(
                    _model_name_,
                    trust_remote_code=True,
                    device="cpu",
                ).float()
            elif LOCAL_MODEL_QUANT == "INT4":  # INT4
                chatglm_model = AutoModel.from_pretrained(
                    pretrained_model_name_or_path=_model_name_,
                    trust_remote_code=True,
                    device="cuda",
                    load_in_4bit=True,
                )
            elif LOCAL_MODEL_QUANT == "INT8":  # INT8
                chatglm_model = AutoModel.from_pretrained(
                    pretrained_model_name_or_path=_model_name_,
                    trust_remote_code=True,
                    device="cuda",
                    load_in_8bit=True,
                )
            else:
                chatglm_model = AutoModel.from_pretrained(
                    pretrained_model_name_or_path=_model_name_,
                    trust_remote_code=True,
                    device="cuda",
                )
            chatglm_model = chatglm_model.eval()

        self._model = chatglm_model
        self._tokenizer = chatglm_tokenizer
        return self._model, self._tokenizer

    def llm_stream_generator(self, **kwargs):
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 子进程执行
        def adaptor(kwargs):
            query = kwargs["query"]
            max_length = kwargs["max_length"]
            top_p = kwargs["top_p"]
            temperature = kwargs["temperature"]
            history = kwargs["history"]
            return query, max_length, top_p, temperature, history

        query, max_length, top_p, temperature, history = adaptor(kwargs)

        for response, history in self._model.stream_chat(
            self._tokenizer,
            query,
            history,
            max_length=max_length,
            top_p=top_p,
            temperature=temperature,
        ):
            yield response

    def try_to_import_special_deps(self, **kwargs):
        # import something that will raise error if the user does not install requirement_*.txt
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 主进程执行
        import importlib

        # importlib.import_module('modelscope')


# ------------------------------------------------------------------------------------------------------------------------
# 🔌💻 GPT-Academic Interface
# ------------------------------------------------------------------------------------------------------------------------
predict_no_ui_long_connection, predict = get_local_llm_predict_fns(
    GetGLM3Handle, model_name, history_format="chatglm3"
)
