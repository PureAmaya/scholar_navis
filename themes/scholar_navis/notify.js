function double_button_notification(title, msg, ok_label = 'ok', cancel_label = 'cancel', ok_fn = null, cancel_fn = null,close_fn = null) {
    alertify.dialog('confirm')
        .set('movable', false)
        .set({transition: 'fade', title: title, message: msg })
        .set('labels', { ok: ok_label, cancel: cancel_label })
        .set({'pinnable': false, 'modal': true })
        .set('oncancel', cancel_fn)
        .set('onok', ok_fn)
        .set({onshow:null, onclose:close_fn})
        .show();
}