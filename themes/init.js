/*
Original Author: gpt_academic@binary-husky

Modified by PureAmaya on 2024-12-28
- Due to the removal of certain features/replacement by gradio components, the corresponding code has been removed.
- Added scholar_navis feature support: dark mode toggle, localization support for JS, fixed issue where the gradio_medal interface unexpectedly closes when opening the dropdown.
*/


async function GptAcademicJavaScriptInit(selected_language) {

await scholar_navis_init(selected_language);
find_all_modal();
dark_mode_init();
var custom_model_input = document.getElementById('custom_model_input');
custom_model_input.style.display = 'none';
console.log("GptAcademicJavaScriptInit: selected_language = " + selected_language);

}
