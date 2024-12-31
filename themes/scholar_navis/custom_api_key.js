// 由 Scholar Navis 添加
// 不会玩js emm，有些地方先凑合吧
// 后续考虑用gr.BrowserState()代替localStorage读写


function str_to_list(str) {
    value = str.split("\n");
    let trimmedArray = value.map(v => v.trim());
    return trimmedArray
}


function save_custom_api_key(api_json) {
    // 将JSON对象转换为字符串
    const str = JSON.stringify(api_json);
    localStorage.setItem('user_custom_data', str);
}

function set_api_key(custom_api_json, provider, provider_json, value) {
    return set_other(custom_api_json, provider_json[provider], value);
}

function set_url_domain(custom_api_json, provider, value) {

    if (provider == 'OpenAI') var type = 'API_URL_REDIRECT';
    else if (provider == '自定义(custom)') var type = 'CUSTOM_REDIRECT';

    custom_api_json[type][0] = value.trim();
    //save_custom_api_key(custom_api_json);  没有必要每次修改都保存
    //push_data_to_gradio_component(custom_api_json, 'user_custom_data', 'str');
    return custom_api_json
}

function set_url_path(custom_api_json, provider, value) {

    if (provider == 'OpenAI') var type = 'API_URL_REDIRECT';
    else if (provider == '自定义(custom)') var type = 'CUSTOM_REDIRECT';
    custom_api_json[type][1] = value.trim();
    //save_custom_api_key(custom_api_json);
    //push_data_to_gradio_component(custom_api_json, 'user_custom_data', 'str');
    return custom_api_json
}

function set_other(custom_api_json, key, value) {
    if (typeof value == 'string') { value = value.trim() }

    if (key == 'CUSTOM_MODELS') {
        value = str_to_list(value)
    }

    custom_api_json[key] = value;
    // save_custom_api_key(custom_api_json);

    //push_data_to_gradio_component(custom_api_json, 'user_custom_data', 'str');
    return custom_api_json
}

function update_api_and_url_redirect_field(custom_api_json, provider, provider_json) {

    if (provider == 'OpenAI') {
        //push_data_to_gradio_component(custom_api_json['API_URL_REDIRECT'][1], 'url_redirect_path', 'str');
        //push_data_to_gradio_component(custom_api_json['API_URL_REDIRECT'][0], 'url_redirect_domain', 'str');
        return [custom_api_json[provider_json[provider]], custom_api_json['API_URL_REDIRECT'][0], custom_api_json['API_URL_REDIRECT'][1]]
    }
    else if (provider == '自定义(custom)') {
        //push_data_to_gradio_component(custom_api_json['CUSTOM_REDIRECT'][1], 'url_redirect_path', 'str');
        //push_data_to_gradio_component(custom_api_json['CUSTOM_REDIRECT'][0], 'url_redirect_domain', 'str');
        return [custom_api_json[provider_json[provider]], custom_api_json['CUSTOM_REDIRECT'][0], custom_api_json['CUSTOM_REDIRECT'][1]]
    }
    else return [custom_api_json[provider_json[provider]], '', '']
    //push_data_to_gradio_component(custom_api_json[provider_json[provider]], 'api_key_field', 'str');
}

function update_field_visible(provider,helper_msg) {

    const domain = document.getElementById('url_redirect_domain');
    const path = document.getElementById('url_redirect_path');
    const url_redirect = [domain, path];

    // 重定向的隐藏和显示
    url_redirect.forEach(field => {
        if (provider == 'OpenAI' || provider == '自定义(custom)') { field.style.display = 'inline' }
        else { field.style.display = 'none' }
    });

    //自定义功能独有的部分的隐藏与显示
    const custom_model_input = document.getElementById('custom_model_input');
    const one_api = [custom_model_input];
    one_api.forEach(field => {
        if (provider == '自定义(custom)') { field.style.display = 'inline'; return helper_msg[1]}
        else { field.style.display = 'none';return helper_msg[0] }
    });

    if (provider == '自定义(custom)') { return helper_msg[1]}
    else { return helper_msg[0] }
}

//!  暂时无用
function update_model_selector(elem_id, custom_model, one_api_toggle) {
    const dropdown = document.getElementById(elem_id);

    if (!one_api_toggle) return

    // 清除现有选项
    dropdown.innerHTML = '';

    // 整理输入值
    if (typeof custom_model == 'string') { custom_model = str_to_list(custom_model) }

    // 添加新的选项
    custom_model.forEach(function (choice) {
        var option = document.createElement('option');
        option.value = choice;
        option.textContent = choice;
        dropdown.appendChild(option);
    });
}



function delete_user_custom_data() {

    ok_fn = () => { localStorage.removeItem('user_custom_data'); location.reload() }
    double_button_notification('删除确认', '确认要删除此设备上的API-KEY等信息吗？', '删除', '取消', true, ok_fn)


}





