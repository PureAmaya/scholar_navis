/* Author: scholar_navis@PureAmaya */

async function scholar_navis_init() {

    // 加载pdf优化器（暂时没啦）
    //push_data_to_gradio_component('<iframe src="' + window.location.origin + '/file=themes/scholar_navis/local_pdf_optimizer/local_pdf_optimizer.html" width="100%" height="220px"></iframe>', 'local_pdf_optimizer', 'no_conversion');

    
    try {// 删除旧版本的自定义内容
        var custom_api_json = JSON.parse(localStorage.getItem('user_custom_data'))

        if (custom_api_json && typeof custom_api_json === 'object' && !Array.isArray(custom_api_json)) {
            // 删除 localStorage 中的 user_custom_data
            localStorage.removeItem('user_custom_data');

            // 提醒用户
            // 先用这个笨方法了。。
            label_head = 'Old version custom content has been deleted.'
            alertify.warning(label_head);
        }
    }
    catch (e) {
        // 忽略错误
    }               

    // 检查维护信息
    await check_msg();
}


// 定义一个函数来获取 JSON 数据
async function getJSON(url) {
    try {
        // 发起一个 GET 请求到指定的 URL
        const response = await fetch(url);

        // 检查响应状态码是否表示成功
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // 解析 JSON 数据
        const jsonData = await response.json();

        // 返回解析后的 JSON 对象
        return jsonData;
    } catch (error) {
        // 捕获并处理可能发生的错误
        console.error('There has been a problem with your fetch operation:', error);
        return null;
    }
}


// 从 Base64 解码为原始字符串
function base64ToUtf8(base64) {
    return decodeURIComponent(window.atob(base64));
}

window.modal = [];

function BanModalPointEvents() {
    window.modal.forEach(element => { element.style.pointerEvents = 'none'; });
    //dropdown_in_modal.forEach(element => {element.style.pointerEvents = 'auto'})
    // 延迟 0.1 秒后执行 modal 的操作
    setTimeout(() => {
        window.modal.forEach(element => {
            element.style.pointerEvents = 'auto';
        });
    }, 100); // 100 毫秒即 0.1 秒

}
function find_all_modal() {
    window.modal = document.querySelectorAll('.modal');
}

function set_dark_mode(enable) {
    if (enable) {
        document.querySelector('body').classList.add('dark');
    } else {
        document.querySelectorAll('.dark').forEach(el => el.classList.remove('dark'));
    }
}

function dark_mode_init() {
    const os_prefer_dark_mode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    let dark_mode_enabled = localStorage.getItem('dark_mode_enabled') === 'true' || os_prefer_dark_mode; // 确保为布尔值
    set_dark_mode(dark_mode_enabled);
    localStorage.setItem('dark_mode_enabled', dark_mode_enabled); // 存储布尔值
}
function dark_mode_toggle() {
    let dark_mode_enabled = localStorage.getItem('dark_mode_enabled') === 'true'; // 确保为布尔值
    set_dark_mode(!dark_mode_enabled);
    localStorage.setItem('dark_mode_enabled', !dark_mode_enabled); // 存储布尔值
}

function submitForm(endpoint,input_name,input_value) {
    // 创建一个隐藏的表单，直接提交到服务器
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = endpoint; // 服务器端的处理路径
    form.target = '_blank'; // 在新窗口打开
    
    // 添加隐藏的 input 字段，传递 base64 数据
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = input_name;
    input.value = input_value;
    form.appendChild(input);
    
    // 将表单添加到文档并提交
    document.body.appendChild(form);
    form.submit();
}

