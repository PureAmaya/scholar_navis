
function scholar_navis_init() {

    try {
        init_custom_api_key();
    }
    catch { }

    // 加载pdf优化器（暂时没啦）
    //push_data_to_gradio_component('<iframe src="' + window.location.origin + '/file=themes/scholar_navis/local_pdf_optimizer/local_pdf_optimizer.html" width="100%" height="220px"></iframe>', 'local_pdf_optimizer', 'no_conversion');



    // 使用方法
    loadResources()


}


async function loadResources() {
    await loadJS('https://cdn.jsdelivr.net/npm/alertifyjs@1.14.0/build/alertify.min.js');
    await loadCSS('https://cdn.jsdelivr.net/npm/alertifyjs@1.14.0/build/css/alertify.min.css');
    await loadCSS('https://cdn.jsdelivr.net/npm/alertifyjs@1.14.0/build/css/themes/bootstrap.min.css')
    check_maintance();
}



async function loadCSS(url) {
    var response = await fetch(url)
    var css = await response.text()
    var style = document.createElement('style');
    style.type = 'text/css';
    style.appendChild(document.createTextNode(css));
    document.head.appendChild(style);

}

async function loadJS(url) {
    var response = await fetch(url)
    var js = await response.text()

    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.appendChild(document.createTextNode(js));
    document.head.appendChild(script);

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

// 以后改成继承吧，不过现在也就用这一个，无所谓了
function double_button_notification(title, msg, ok_label = 'ok', cancel_label = 'cancel',closable = false, ok_fn = null, cancel_fn = null,close_fn = null) {
    alertify.dialog('confirm')
        .setting({'movable': false,
    'closable': closable,
    'closableByDimmer':closable,
    'transition': 'fade', 'title': title, 'message': msg ,
    'labels': { 'ok': ok_label, 'cancel': cancel_label},
    'pinnable': true, 'modal': true ,
    'onshow':null, 
    'onclose': close_fn,
    'oncancel': cancel_fn,
    'onok': ok_fn})
        .show();
}

async function check_maintance() {
    var json = await getJSON("/api/notification/maintenance")

    var session_value = parseInt(sessionStorage.getItem('maintenance_show') || '1');
    var local_value = parseInt(localStorage.getItem('maintenance_show') || '1');

    if (json.state) {
        // 新的维护刷新
        var local_hash = localStorage.getItem('maintenance_hash') || '0';
        if ( ! Object.keys(json).includes('hash')  || local_hash!= json.hash) {local_value = 1; session_value = 1; }

        // 本地维护显示
        if (session_value == 1 && local_value === 1)
            {
                var title = '需要维护';
                var msg =  `
                <p>预计开始时间：${json.start_time}；预计时长：${json.estimated_duration}</p>
    
                <h3>维护内容：</h3>
                <p>${json.description}<p>
            `
                var ok_label = '确认'
                var cancel_label = '本次维护不再显示'
    
                var ok_fn = () => {sessionStorage.setItem('maintenance_show', '0')}
                var cancel_fn = () => {localStorage.setItem('maintenance_show', '0')}
                var close_fn = () => {localStorage.setItem('maintenance_hash', json.hash) }

                double_button_notification(title,msg,ok_label,cancel_label,false,ok_fn,cancel_fn,close_fn)
        }
            
    }
    // 没有维护，重置
    else{
        localStorage.setItem('maintenance_show', '1');
        sessionStorage.setItem('maintenance_show', '1');
    }
}
