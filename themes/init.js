async function GptAcademicJavaScriptInit(selected_language) {

await scholar_navis_init(selected_language);
find_all_modal();
dark_mode_init();
var custom_model_input = document.getElementById('custom_model_input');
custom_model_input.style.display = 'none';
console.log("GptAcademicJavaScriptInit: selected_language = " + selected_language);

}
