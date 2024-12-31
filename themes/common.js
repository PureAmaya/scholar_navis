// 标志位
enable_tts = false;

// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//  第 1 部分: 工具函数
// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

function push_data_to_gradio_component(DAT, ELEM_ID, TYPE) {
    throw new Error("Not implemented");
}

function update_array(arr, item, mode) {
    //   // Remove "输入清除键"
    //   p = updateArray(p, "输入清除键", "remove");
    //   console.log(p); // Should log: ["基础功能区", "函数插件区"]

    //   // Add "输入清除键"
    //   p = updateArray(p, "输入清除键", "add");
    //   console.log(p); // Should log: ["基础功能区", "函数插件区", "输入清除键"]

    const index = arr.indexOf(item);
    if (mode === "remove") {
        if (index !== -1) {
            // Item found, remove it
            arr.splice(index, 1);
        }
    } else if (mode === "add") {
        if (index === -1) {
            // Item not found, add it
            arr.push(item);
        }
    }
    return arr;
}


function gradioApp() {
    // https://github.com/GaiZhenbiao/ChuanhuChatGPT/tree/main/web_assets/javascript
    const elems = document.getElementsByTagName('gradio-app');
    const elem = elems.length == 0 ? document : elems[0];
    if (elem !== document) {
        elem.getElementById = function (id) {
            return document.getElementById(id);
        };
    }
    return elem.shadowRoot ? elem.shadowRoot : elem;
}


function setCookie(name, value, days) {
    var expires = "";

    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }

    document.cookie = name + "=" + value + expires + "; path=/";
}


function getCookie(name) {
    var decodedCookie = decodeURIComponent(document.cookie);
    var cookies = decodedCookie.split(';');

    for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();

        if (cookie.indexOf(name + "=") === 0) {
            return cookie.substring(name.length + 1, cookie.length);
        }
    }

    return null;
}


let toastCount = 0;
function toast_push(msg, duration) {
    duration = isNaN(duration) ? 3000 : duration;
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => {
        toast.style.top = `${parseInt(toast.style.top, 10) - 70}px`;
    });
    const m = document.createElement('div');
    m.innerHTML = msg;
    m.classList.add('toast');
    m.style.cssText = `font-size: var(--text-md) !important; color: rgb(255, 255, 255); background-color: rgba(0, 0, 0, 0.6); padding: 10px 15px; border-radius: 4px; position: fixed; top: ${50 + toastCount * 70}%; left: 50%; transform: translateX(-50%); width: auto; text-align: center; transition: top 0.3s;`;
    document.body.appendChild(m);
    setTimeout(function () {
        m.style.opacity = '0';
        setTimeout(function () {
            document.body.removeChild(m);
            toastCount--;
        }, 500);
    }, duration);
    toastCount++;
}


function toast_up(msg) {
    var m = document.getElementById('toast_up');
    if (m) {
        document.body.removeChild(m); // remove the loader from the body
    }
    m = document.createElement('div');
    m.id = 'toast_up';
    m.innerHTML = msg;
    m.style.cssText = "font-size: var(--text-md) !important; color: rgb(255, 255, 255); background-color: rgba(0, 0, 100, 0.6); padding: 10px 15px; margin: 0 0 0 -60px; border-radius: 4px; position: fixed; top: 50%; left: 50%; width: auto; text-align: center;";
    document.body.appendChild(m);
}


function toast_down() {
    var m = document.getElementById('toast_up');
    if (m) {
        document.body.removeChild(m); // remove the loader from the body
    }
}


function begin_loading_status() {
    // Create the loader div and add styling
    var loader = document.createElement('div');
    loader.id = 'Js_File_Loading';
    var C1 = document.createElement('div');
    var C2 = document.createElement('div');
    // var C3 = document.createElement('span');
    // C3.textContent = '上传中...'
    // C3.style.position = "fixed";
    // C3.style.top = "50%";
    // C3.style.left = "50%";
    // C3.style.width = "80px";
    // C3.style.height = "80px";
    // C3.style.margin = "-40px 0 0 -40px";

    C1.style.position = "fixed";
    C1.style.top = "50%";
    C1.style.left = "50%";
    C1.style.width = "80px";
    C1.style.height = "80px";
    C1.style.borderLeft = "12px solid #00f3f300";
    C1.style.borderRight = "12px solid #00f3f300";
    C1.style.borderTop = "12px solid #82aaff";
    C1.style.borderBottom = "12px solid #82aaff"; // Added for effect
    C1.style.borderRadius = "50%";
    C1.style.margin = "-40px 0 0 -40px";
    C1.style.animation = "spinAndPulse 2s linear infinite";

    C2.style.position = "fixed";
    C2.style.top = "50%";
    C2.style.left = "50%";
    C2.style.width = "40px";
    C2.style.height = "40px";
    C2.style.borderLeft = "12px solid #00f3f300";
    C2.style.borderRight = "12px solid #00f3f300";
    C2.style.borderTop = "12px solid #33c9db";
    C2.style.borderBottom = "12px solid #33c9db"; // Added for effect
    C2.style.borderRadius = "50%";
    C2.style.margin = "-20px 0 0 -20px";
    C2.style.animation = "spinAndPulse2 2s linear infinite";

    loader.appendChild(C1);
    loader.appendChild(C2);
    // loader.appendChild(C3);
    document.body.appendChild(loader); // Add the loader to the body

    // Set the CSS animation keyframes for spin and pulse to be synchronized
    var styleSheet = document.createElement('style');
    styleSheet.id = 'Js_File_Loading_Style';
    styleSheet.textContent = `
    @keyframes spinAndPulse {
        0% { transform: rotate(0deg) scale(1); }
        25% { transform: rotate(90deg) scale(1.1); }
        50% { transform: rotate(180deg) scale(1); }
        75% { transform: rotate(270deg) scale(0.9); }
        100% { transform: rotate(360deg) scale(1); }
    }

    @keyframes spinAndPulse2 {
        0% { transform: rotate(-90deg);}
        25% { transform: rotate(-180deg);}
        50% { transform: rotate(-270deg);}
        75% { transform: rotate(-360deg);}
        100% { transform: rotate(-450deg);}
    }
    `;
    document.head.appendChild(styleSheet);
}


function cancel_loading_status() {
    // remove the loader from the body
    var loadingElement = document.getElementById('Js_File_Loading');
    if (loadingElement) {
        document.body.removeChild(loadingElement);
    }
    var loadingStyle = document.getElementById('Js_File_Loading_Style');
    if (loadingStyle) {
        document.head.removeChild(loadingStyle);
    }
    // create new listen event
    let clearButton = document.querySelectorAll('div[id*="elem_upload"] button[aria-label="Clear"]');
    for (let button of clearButton) {
        button.addEventListener('click', function () {
            setTimeout(function () {
                register_upload_event();
            }, 50);
        });
    }
}


// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//  第 2 部分: 复制按钮
// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


var allow_auto_read_continously = true;
var allow_auto_read_tts_flag = false;

let timeoutID = null;
let lastInvocationTime = 0;
let lastArgs = null;
function do_something_but_not_too_frequently(min_interval, func) {
    return function (...args) {
        lastArgs = args;
        const now = Date.now();
        if (!lastInvocationTime || (now - lastInvocationTime) >= min_interval) {
            lastInvocationTime = now;
            // 现在就执行
            setTimeout(() => {
                func.apply(this, lastArgs);
            }, 0);
        } else if (!timeoutID) {
            // 等一会执行
            timeoutID = setTimeout(() => {
                timeoutID = null;
                lastInvocationTime = Date.now();
                func.apply(this, lastArgs);
            }, min_interval - (now - lastInvocationTime));
        } else {
            // 压根不执行
        }
    }
}





// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//  第 3 部分: chatbot动态高度调整
// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
function chatbotAutoHeight() {
    // 自动调整高度：立即
    function update_height() {
        var { height_target, chatbot_height, chatbot } = get_elements(true);
        if (height_target != chatbot_height) {
            var pixelString = height_target.toString() + 'px';
            chatbot.style.maxHeight = pixelString; chatbot.style.height = pixelString;
        }
    }

    // 自动调整高度：缓慢
    function update_height_slow() {
        var { height_target, chatbot_height, chatbot } = get_elements();
        if (height_target != chatbot_height) {
            // sign = (height_target - chatbot_height)/Math.abs(height_target - chatbot_height);
            // speed = Math.max(Math.abs(height_target - chatbot_height), 1);
            new_panel_height = (height_target - chatbot_height) * 0.5 + chatbot_height;
            if (Math.abs(new_panel_height - height_target) < 10) {
                new_panel_height = height_target;
            }
            var pixelString = new_panel_height.toString() + 'px';
            chatbot.style.maxHeight = pixelString; chatbot.style.height = pixelString;
        }
    }
    monitoring_input_box()
    update_height();
    window.addEventListener('resize', function () { update_height(); });
    window.addEventListener('scroll', function () { update_height_slow(); });
    setInterval(function () { update_height_slow() }, 50); // 每50毫秒执行一次
}


swapped = false;
function swap_input_area() {
    // Get the elements to be swapped
    var element1 = document.querySelector("#input-panel");
    var element2 = document.querySelector("#basic-panel");

    // Get the parent of the elements
    var parent = element1.parentNode;

    // Get the next sibling of element2
    var nextSibling = element2.nextSibling;

    // Swap the elements
    parent.insertBefore(element2, element1);
    parent.insertBefore(element1, nextSibling);
    if (swapped) { swapped = false; }
    else { swapped = true; }
}


function get_elements(consider_state_panel = false) {
    var chatbot = document.querySelector('#gpt-chatbot > div.wrap.svelte-18telvq');
    if (!chatbot) {
        chatbot = document.querySelector('#gpt-chatbot');
    }
    const panel1 = document.querySelector('#input-panel').getBoundingClientRect();
    const panel2 = document.querySelector('#basic-panel').getBoundingClientRect()
    const panel3 = document.querySelector('#plugin-panel').getBoundingClientRect();
    // const panel4 = document.querySelector('#interact-panel').getBoundingClientRect();
    const panel_active = document.querySelector('#state-panel').getBoundingClientRect();
    if (consider_state_panel || panel_active.height < 25) {
        document.state_panel_height = panel_active.height;
    }
    // 25 是chatbot的label高度, 16 是右侧的gap
    var height_target = panel1.height + panel2.height + panel3.height + 0 + 0 - 25 + 16 * 2;
    // 禁止动态的state-panel高度影响
    height_target = height_target + (document.state_panel_height - panel_active.height)
    var height_target = parseInt(height_target);
    var chatbot_height = chatbot.style.height;
    // 交换输入区位置，使得输入区始终可用
    if (!swapped) {
        if (panel1.top != 0 && (0.9 * panel1.bottom + 0.1 * panel1.top) < 0) { swap_input_area(); }
    }
    else if (swapped) {
        if (panel2.top != 0 && panel2.top > 0) { swap_input_area(); }
    }
    // 调整高度
    const err_tor = 5;
    if (Math.abs(panel1.left - chatbot.getBoundingClientRect().left) < err_tor) {
        // 是否处于窄屏模式
        height_target = window.innerHeight * 0.6;
    } else {
        // 调整高度
        const chatbot_height_exceed = 15;
        const chatbot_height_exceed_m = 10;
        b_panel = Math.max(panel1.bottom, panel2.bottom, panel3.bottom)
        if (b_panel >= window.innerHeight - chatbot_height_exceed) {
            height_target = window.innerHeight - chatbot.getBoundingClientRect().top - chatbot_height_exceed_m;
        }
        else if (b_panel < window.innerHeight * 0.75) {
            height_target = window.innerHeight * 0.8;
        }
    }
    var chatbot_height = parseInt(chatbot_height);
    return { height_target, chatbot_height, chatbot };
}



// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//  第 4 部分: 粘贴、拖拽文件上传
// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

var elem_upload = null;
var elem_upload_float = null;
var elem_input_main = null;
var elem_input_float = null;
var elem_chatbot = null;
var elem_upload_component_float = null;
var elem_upload_component = null;
var exist_file_msg = '⚠️请先删除上传区（左上方）中的历史文件，再尝试上传。'

function locate_upload_elems() {
    elem_upload = document.getElementById('elem_upload')
    elem_upload_float = document.getElementById('elem_upload_float')
    elem_input_main = document.getElementById('user_input_main')
    elem_input_float = document.getElementById('user_input_float')
    elem_chatbot = document.getElementById('gpt-chatbot')
    elem_upload_component_float = elem_upload_float.querySelector("input[type=file]");
    elem_upload_component = elem_upload.querySelector("input[type=file]");
}

function upload_files(files) {
    let totalSizeMb = 0
    elem_upload_component_float = elem_upload_float.querySelector("input[type=file]");
    if (files && files.length > 0) {
        // 执行具体的上传逻辑
        if (elem_upload_component_float) {
            for (let i = 0; i < files.length; i++) {
                // 将从文件数组中获取的文件大小(单位为字节)转换为MB，
                totalSizeMb += files[i].size / 1024 / 1024;
            }
            // 检查文件总大小是否超过20MB
            if (totalSizeMb > 20) {
                toast_push('⚠️文件夹大于 20MB 🚀上传文件中', 3000);
            }
            let event = new Event("change");
            Object.defineProperty(event, "target", { value: elem_upload_component_float, enumerable: true });
            Object.defineProperty(event, "currentTarget", { value: elem_upload_component_float, enumerable: true });
            Object.defineProperty(elem_upload_component_float, "files", { value: files, enumerable: true });
            elem_upload_component_float.dispatchEvent(event);
        } else {
            toast_push(exist_file_msg, 3000);
        }
    }
}


function elem_upload_component_pop_message(elem) {
    if (elem) {
        const dragEvents = ["dragover"];
        const leaveEvents = ["dragleave", "dragend", "drop"];
        dragEvents.forEach(event => {
            elem.addEventListener(event, function (e) {
                e.preventDefault();
                e.stopPropagation();
                if (elem_upload_float.querySelector("input[type=file]")) {
                    toast_up('⚠️释放以上传文件')
                } else {
                    toast_up(exist_file_msg)
                }
            });
        });
        leaveEvents.forEach(event => {
            elem.addEventListener(event, function (e) {
                toast_down();
                e.preventDefault();
                e.stopPropagation();
            });
        });
        elem.addEventListener("drop", function (e) {
            toast_push('正在上传中，请稍等。', 2000);
            begin_loading_status();
        });
    }
}


function register_upload_event() {
    locate_upload_elems();
    if (elem_upload_float) {
        _upload = document.querySelector("#elem_upload_float div.center.boundedheight.flex")
        elem_upload_component_pop_message(_upload);
    }
    if (elem_upload_component_float) {
        elem_upload_component_float.addEventListener('change', function (event) {
            toast_push('正在上传中，请稍等。', 2000);
            begin_loading_status();
        });
    }
    if (elem_upload_component) {
        elem_upload_component.addEventListener('change', function (event) {
            toast_push('正在上传中，请稍等。', 2000);
            begin_loading_status();
        });
    } else {
        toast_push("oppps", 3000);
    }
}


function monitoring_input_box() {
    register_upload_event();

    if (elem_input_main) {
        if (elem_input_main.querySelector("textarea")) {
            register_func_paste(elem_input_main.querySelector("textarea"));
        }
    }
    if (elem_input_float) {
        if (elem_input_float.querySelector("textarea")) {
            register_func_paste(elem_input_float.querySelector("textarea"));
        }
    }
    if (elem_chatbot) {
        register_func_drag(elem_chatbot);
    }

}


// 监视页面变化
window.addEventListener("DOMContentLoaded", function () {
    // const ga = document.getElementsByTagName("gradio-app");
    gradioApp().addEventListener("render", monitoring_input_box);
});



// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//  第 7 部分: JS初始化函数
// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


function get_checkbox_selected_items(elem_id) {
    display_panel_arr = [];
    document.getElementById(elem_id).querySelector('[data-testid="checkbox-group"]').querySelectorAll('label').forEach(label => {
        // Get the span text
        const spanText = label.querySelector('span').textContent;
        // Get the input value
        const checked = label.querySelector('input').checked;
        if (checked) {
            display_panel_arr.push(spanText)
        }
    });
    return display_panel_arr;
}


function gpt_academic_gradio_saveload(
    save_or_load,       // save_or_load==="save" / save_or_load==="load"
    elem_id,            // element id
    cookie_key,         // cookie key
    save_value = "",      // save value
    load_type = "str",  // type==="str" / type==="float"
    load_default = false, // load default value
    load_default_value = ""
) {
    if (save_or_load === "load") {
        let value = getCookie(cookie_key);
        if (value) {
            console.log('加载cookie', elem_id, value)
            //push_data_to_gradio_component(value, elem_id, load_type);
            return value;
        }
        else {
            if (load_default) {
                console.log('加载cookie的默认值', elem_id, load_default_value)
                //push_data_to_gradio_component(load_default_value, elem_id, load_type);
                return load_default_value;
            }
        }
    }
    if (save_or_load === "save") {
        setCookie(cookie_key, save_value, 365);
    }
}


function reset_conversation(a, b) {
    // console.log("js_code_reset");
    a = btoa(unescape(encodeURIComponent(JSON.stringify(a))));
    setCookie("js_previous_chat_cookie", a, 1);
    return [[], [], "已重置"];
}


function execute_current_pop_up_plugin(guiBase64String) {
    const stringData = atob(guiBase64String);
    let guiJsonData = JSON.parse(stringData);
    gui_args = {}
    for (const key in guiJsonData) {
        if (guiJsonData.hasOwnProperty(key)) {
            const innerJSONString = guiJsonData[key];
            const decodedObject = JSON.parse(innerJSONString);
            gui_args[key] = decodedObject;
        }
    }
    // read user confirmed value
    let text_cnt = 0;
    for (const key in gui_args) {
        if (gui_args.hasOwnProperty(key)) {
            if (gui_args[key].type == 'string') { // PLUGIN_ARG_MENU
                corrisponding_elem_id = "plugin_arg_txt_" + text_cnt
                //gui_args[key].user_confirmed_value = await get_data_from_gradio_component(corrisponding_elem_id);
                gui_args[key].user_confirmed_value = document.getElementById(corrisponding_elem_id).children[1].children[2].children[0].value;
                text_cnt += 1;
            }
        }
    }
    let dropdown_cnt = 0;
    for (const key in gui_args) {
        if (gui_args.hasOwnProperty(key)) {
            if (gui_args[key].type == 'dropdown') { // PLUGIN_ARG_MENU
                corrisponding_elem_id = "plugin_arg_drop_" + dropdown_cnt
                //gui_args[key].user_confirmed_value = await get_data_from_gradio_component(corrisponding_elem_id);
                gui_args[key].user_confirmed_value = document.getElementById(corrisponding_elem_id).children[1].children[2].children[0].children[0].children[0].value;
                dropdown_cnt += 1;
            }
        }
    }
    // close menu
    //push_data_to_gradio_component({
    //    visible: false,
    //    __type__: 'update'
    //}, "plugin_arg_menu", "obj");
    //document.getElementById("plugin_arg_menu").style.display = 'none';



    // execute the plugin
    //push_data_to_gradio_component(JSON.stringify(gui_args), "invisible_current_pop_up_plugin_arg_final", "string");
    //document.getElementById('invisible_current_pop_up_plugin_arg_final').children[0].children[1].children[0].value = JSON.stringify(gui_args);
    //document.getElementById("invisible_callback_btn_for_plugin_exe").click();
    return JSON.stringify(gui_args)
}

function hide_all_elem() {
    // PLUGIN_ARG_MENU
    for (text_cnt = 0; text_cnt < 8; text_cnt++) {
        /*
        push_data_to_gradio_component({
            visible: false,
            label: "",
            __type__: 'update'
        }, "plugin_arg_txt_"+text_cnt, "obj");
        */
        document.getElementById("plugin_arg_txt_" + text_cnt).parentNode.parentNode.style.display = 'none';
        document.getElementById("plugin_arg_txt_" + text_cnt).style.display = 'none';
    }
    for (dropdown_cnt = 0; dropdown_cnt < 8; dropdown_cnt++) {
        /*
        push_data_to_gradio_component({
            visible: false,
            choices: [],
            label: "",
            __type__: 'update'
        }, "plugin_arg_drop_"+dropdown_cnt, "obj");
        */
        document.getElementById("plugin_arg_drop_" + dropdown_cnt).parentNode.style.display = 'none';
        document.getElementById("plugin_arg_drop_" + dropdown_cnt).style.display = 'none';
    }
}

function close_current_pop_up_plugin() {
    // PLUGIN_ARG_MENU
    push_data_to_gradio_component({
        visible: false,
        __type__: 'update'
    }, "plugin_arg_menu", "obj");
    hide_all_elem();
}


// 生成高级插件的选择菜单
plugin_init_info_lib = {}
function register_plugin_init(key, base64String) {
    // console.log('x')
    const stringData = atob(base64String);
    let guiJsonData = JSON.parse(stringData);
    if (key in plugin_init_info_lib) {
    }
    else {
        plugin_init_info_lib[key] = {};
    }
    plugin_init_info_lib[key].info = guiJsonData.Info;
    plugin_init_info_lib[key].color = guiJsonData.Color;
    plugin_init_info_lib[key].elem_id = guiJsonData.ButtonElemId;
    plugin_init_info_lib[key].label = guiJsonData.Label
    plugin_init_info_lib[key].enable_advanced_arg = guiJsonData.AdvancedArgs;
    plugin_init_info_lib[key].arg_reminder = guiJsonData.ArgsReminder;
}
function register_advanced_plugin_init_code(key, code) {
    if (key in plugin_init_info_lib) {
    }
    else {
        plugin_init_info_lib[key] = {};
    }
    plugin_init_info_lib[key].secondary_menu_code = code;
}
function run_advanced_plugin_launch_code(key) {
    // convert js code string to function
    generate_menu(plugin_init_info_lib[key].secondary_menu_code, key);
}
function on_flex_button_click(key) {
    if (plugin_init_info_lib.hasOwnProperty(key) && plugin_init_info_lib[key].hasOwnProperty('secondary_menu_code')) {
        run_advanced_plugin_launch_code(key);
    } else {
        document.getElementById("old_callback_btn_for_plugin_exe").click();
    }
}
function run_dropdown_shift(dropdown) {
    let key = dropdown;
    push_data_to_gradio_component({
        value: key,
        variant: plugin_init_info_lib[key].color,
        info_str: plugin_init_info_lib[key].info,
        __type__: 'update'
    }, "elem_switchy_bt", "obj");

    if (plugin_init_info_lib[key].enable_advanced_arg) {
        push_data_to_gradio_component({
            visible: true,
            label: plugin_init_info_lib[key].label,
            __type__: 'update'
        }, "advance_arg_input_legacy", "obj");
    } else {
        push_data_to_gradio_component({
            visible: false,
            label: plugin_init_info_lib[key].label,
            __type__: 'update'
        }, "advance_arg_input_legacy", "obj");
    }
}

function duplicate_in_new_window() {
    // 获取当前页面的URL
    var url = window.location.href;
    // 在新标签页中打开这个URL
    window.open(url, '_blank');
}


// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//  多用途复用提交按钮
// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

function click_real_submit_btn() {
    document.getElementById("elem_submit").click();
}
function multiplex_function_begin(multiplex_sel) {
    if (multiplex_sel === "常规对话") {
        click_real_submit_btn();
        return;
    }
    if (multiplex_sel === "多模型对话") {
        let _align_name_in_crazy_function_py = "询问多个GPT模型";
        call_plugin_via_name(_align_name_in_crazy_function_py);
        return;
    }
}
function run_multiplex_shift(multiplex_sel) {
    let key = multiplex_sel;
    if (multiplex_sel === "常规对话") {
        key = "提交";
    } else {
        key = "提交 (" + multiplex_sel + ")";
    }
    push_data_to_gradio_component({
        value: key,
        __type__: 'update'
    }, "elem_submit_visible", "obj");
}

