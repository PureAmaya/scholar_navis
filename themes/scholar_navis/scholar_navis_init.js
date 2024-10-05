
function scholar_navis_init() {

    try {
        init_custom_api_key();
    }
    catch { }

    // 加载pdf优化器（暂时没啦）
    //push_data_to_gradio_component('<iframe src="' + window.location.origin + '/file=themes/scholar_navis/local_pdf_optimizer/local_pdf_optimizer.html" width="100%" height="220px"></iframe>', 'local_pdf_optimizer', 'no_conversion');
}