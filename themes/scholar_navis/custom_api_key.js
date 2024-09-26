// 由 Scholar Navis 添加
// 不会玩js emm，有些地方先凑合吧

const NORMAL_HELP_MSG = `
<p>在此处自定义您的api-key，访问更多模型。</p>
<p>
目前仅OpenAI支持使用其他重定向服务<br>
其他提供商均使用的是官方服务<br></p>

<p>
OpenAI重定向服务只适用于OpenAI的大部分模型<br>
如果要使用重定向服务的其他模型，请使用 <em>自定义</em> 功能
</p>

<details>
<summary>点击查看 API-KEY 获取地址</summary>
<ul>
<li><a href="https://platform.openai.com/api-keys" target="_blank">OpenAI</a>：GPT系列模型</li>
<li><a href="https://open.bigmodel.cn/usercenter/apikeys" target="_blank">智谱(Zhipu)</a>：GLM系列模型</li>
<li><a href="https://bailian.console.aliyun.com/?apiKey=1#/api-key" target="_blank">通义千问(Qwen)</a>：qwen系列模型</li>
<li><a href="https://platform.moonshot.cn/console/api-keys" target="_blank">月之暗面(Moonshot)</a>：moonshot系列模型</li>
<li><a href="https://platform.deepseek.com/api_keys" target="_blank">深度求索(Deepseek)</a>：deepseek系列模型</li>
</ul>
</details>
`;


const CUSTOM_HELP_MSG = `
<p>使用该功能添加自定义模型或使用openAI重定向服务。
<br>自定义模型将使用 custom- 前缀，并使用本页面的信息发送请求</p>
如果仅需使用openAI重定向服务，请在 <em>OpenAI</em> 项目中修改重定向地址

<details>
<summary>点击查看 第三方中转服务</summary>
<p><em>使用前请阅读中转服务的帮助文档</em></p>
<ul>
<li><a href="https://api2d.com/" target="_blank">API2d</a>：支持多功能接口，中国大陆优化</li>
<li><a href="https://aiproxy.io/" target="_blank">AI Proxy</a>：位于新加坡，支持英文页面，支持大部分支付方式</li>
<li><a href="https://aihubmix.com/" target="_blank">AI HUB MIX</a>：中国大陆优化</li>
<li>使用其他第三方<a href="https://github.com/songquanpeng/one-api" target="_blank">oneapi</a>服务</li>
<li>使用其他第三方<a href="https://github.com/open-webui/open-webui" target="_blank">llama</a>服务</li>
</ul>
</details>
`;

function str_to_list(str){
    value = str.split("\n");
    let trimmedArray = value.map(v => v.trim());
    return trimmedArray
}

function init_custom_api_key() {
    // 从 localStorage 读取数据
    var localStorageData = localStorage.getItem('user_custom_data');
    try{
        var custom_api_json = JSON.parse(localStorageData);
        // 先按照openai进行获取
        push_data_to_gradio_component(custom_api_json['API_KEY'], 'api_key_field', 'str');
        push_data_to_gradio_component(custom_api_json['API_URL_REDIRECT'][1], 'url_redirect_path', 'str');
        push_data_to_gradio_component(custom_api_json['API_URL_REDIRECT'][0], 'url_redirect_domain', 'str');
        // 自定义需要读取一些额外的内容
        push_data_to_gradio_component(custom_api_json['CUSTOM_MODELS'].join("\n"),'custom_model_input','str');

        // 后端获取值，便于使用
        push_data_to_gradio_component(custom_api_json,'user_custom_data','str');
    }
    catch(e){}// 出问题就用默认值
    
    update_field_visible('OpenAI');
}

function save_custom_api_key(api_json) {
    // 将JSON对象转换为字符串
    const str = JSON.stringify(api_json);
    localStorage.setItem('user_custom_data', str);
}

function set_api_key(custom_api_json,provider,provider_json,value){
    set_other(custom_api_json,provider_json[provider],value);
    save_custom_api_key(custom_api_json);
}

function set_url_domain(custom_api_json,provider,value){

    if (provider == 'OpenAI') var type = 'API_URL_REDIRECT';
    else if (provider == '自定义')  var type = 'CUSTOM_REDIRECT';

    custom_api_json[type][0] = value.trim();
    push_data_to_gradio_component(custom_api_json,'user_custom_data','str');
    save_custom_api_key(custom_api_json);
}

function set_url_path(custom_api_json,provider,value){

    if (provider == 'OpenAI') var type = 'API_URL_REDIRECT';
    else if (provider == '自定义')  var type = 'CUSTOM_REDIRECT';
    custom_api_json[type][1] = value.trim();
    push_data_to_gradio_component(custom_api_json,'user_custom_data','str');
    save_custom_api_key(custom_api_json);
}

function set_other(custom_api_json,key,value){
    if ( typeof value == 'string'){value = value.trim()}

    if (key == 'CUSTOM_MODELS')
        {
            value = str_to_list(value)
    }
    
    custom_api_json[key] = value;
    push_data_to_gradio_component(custom_api_json,'user_custom_data','str');
    save_custom_api_key(custom_api_json);
}

function update_api_and_url_redirect_field(custom_api_json,provider,provider_json){

    if (provider == 'OpenAI'){
        push_data_to_gradio_component(custom_api_json['API_URL_REDIRECT'][1], 'url_redirect_path', 'str');
        push_data_to_gradio_component(custom_api_json['API_URL_REDIRECT'][0], 'url_redirect_domain', 'str');
    }
    else if (provider == '自定义'){
        push_data_to_gradio_component(custom_api_json['CUSTOM_REDIRECT'][1], 'url_redirect_path', 'str');
        push_data_to_gradio_component(custom_api_json['CUSTOM_REDIRECT'][0], 'url_redirect_domain', 'str');
    }

    push_data_to_gradio_component(custom_api_json[provider_json[provider]], 'api_key_field', 'str');
}

function update_field_visible(provider) {

    if (provider == '自定义') {
        push_data_to_gradio_component(CUSTOM_HELP_MSG, 'custom_api_help_msg', 'str');
    }
    else {
        push_data_to_gradio_component(NORMAL_HELP_MSG, 'custom_api_help_msg', 'str');
    }


    const domain = document.getElementById('url_redirect_domain');
    const path = document.getElementById('url_redirect_path');
    const url_redirect = [domain, path];

    // 重定向的隐藏和显示
    url_redirect.forEach(field => {
        if (provider == 'OpenAI' || provider == '自定义') { field.style.display = 'inline' }
        else { field.style.display = 'none' }
    });

    //自定义独有的
    const custom_model_input = document.getElementById('custom_model_input');
    const one_api = [custom_model_input];
    one_api.forEach(field => {
        if (provider == '自定义') {field.style.display = 'inline';}
        else {field.style.display = 'none';}
    });
}

//!  暂时无用
function update_model_selector(elem_id,custom_model,one_api_toggle) {
    const dropdown = document.getElementById(elem_id);

    if (!one_api_toggle) return

    // 清除现有选项
    dropdown.innerHTML = '';

    // 整理输入值
    if (typeof custom_model == 'string' ){custom_model = str_to_list(custom_model)}
        
    // 添加新的选项
    custom_model.forEach(function(choice) {
        var option = document.createElement('option');
        option.value = choice;
        option.textContent = choice;
        dropdown.appendChild(option);
    });
    }


