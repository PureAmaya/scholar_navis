/* Author: scholar_navis@PureAmaya */


// 以后改成继承吧，不过现在也就用这一个，无所谓了
function double_button_notification(title, msg, ok_label = 'ok', cancel_label = 'cancel', closable = false, ok_fn = null, cancel_fn = null, close_fn = null) {
    alertify.dialog('confirm')
        .setting({
            'movable': false,
            'closable': closable,
            'closableByDimmer': closable,
            'transition': 'fade', 'title': title, 'message': msg,
            'labels': { 'ok': ok_label, 'cancel': cancel_label },
            'pinnable': true, 'modal': true,
            'onshow': null,
            'onclose': close_fn,
            'oncancel': cancel_fn,
            'onok': ok_fn
        })
        .show();
}

/**
 * @param msg
 * @param {'success'|'warning'|'error'|'message'|'notify'} notifier_type
 *  @param delay
 *  @param {'top-right'|'top-center'|'top-left'|'bottom-right'|'bottom-center'|'bottom-left'} position
 */
function Notifier(msg,notifier_type,delay=5,position='top-right'){
    alertify.set('notifier','position', position );
    alertify.notify(msg, notifier_type, delay);
}



// 维护通知
async function check_msg() {

    const json = await getJSON("/api/notification/msg");

    let session_value = parseInt(sessionStorage.getItem('maintenance_show') || '1');
    let local_value = parseInt(localStorage.getItem('maintenance_show') || '1');

    if (json.state) {
        // 新的消息刷新
        const local_code = localStorage.getItem('maintenance_code') || '0';
        if (!Object.keys(json).includes('code') || local_code != json.code) { local_value = 1; session_value = 1; }

        // 本地维护显示
        if (session_value === 1 && local_value === 1) {
            var title = json.title;
            var msg = json.message;
            
            var ok_label = 'Confirm'
            var cancel_label = 'Do not show again'

            var ok_fn = () => { sessionStorage.setItem('maintenance_show', '0') }
            var cancel_fn = () => { localStorage.setItem('maintenance_show', '0') }
            var close_fn = () => { localStorage.setItem('maintenance_code', json.code) }

            double_button_notification(title, msg, ok_label, cancel_label, false, ok_fn, cancel_fn, close_fn)
        }

    }
    // 没有维护，重置
    else {
        localStorage.setItem('maintenance_show', '1');
        sessionStorage.setItem('maintenance_show', '1');
    }
}
