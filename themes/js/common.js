/*
'''
Original Author: gpt_academic@binary-husky

Modified by PureAmaya on 2025-04-08
- Useless variables, methods, and other content have been removed: files upload, chatbot dynamic height adjustment, Copy button and some other JS
Add comments to the methods used by some gradio.
- Adjust the reset_conversation method to remove unnecessary cookies (js_previous_chat_cookie) generated.

Modified by PureAmaya on 2024-12-28
- Some features are implemented by the Gradio component.
- Due to the upgrade to Gradio 5, some functionalities have become invalid and have been removed.
'''
*/

function push_data_to_gradio_component(DAT, ELEM_ID, TYPE) {
    throw new Error("Not implemented");
}

/* gradio */
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

/* gradio */
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

/* gradio */
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

/* gradio */
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

/* gradio */
function click_real_submit_btn() {
    document.getElementById("elem_submit").click();
}

/* gradio */
function reset_conversation() {
 let stopButton = document.getElementById("elem_stop");
    stopButton.click();
    return [[], [], "Reset"];
}

/* gradio */
function setCookie(name, value, days) {
    var expires = "";

    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }

    document.cookie = name + "=" + value + expires + "; path=/";
}


