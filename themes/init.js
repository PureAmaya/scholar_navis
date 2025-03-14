/*
Original Author: gpt_academic@binary-husky

Modified by PureAmaya on 2025-03-14
- Resolve the occasional GptAcademicJavaScriptInit undefined error.

Modified by PureAmaya on 2024-12-28
- Due to the removal of certain features/replacement by gradio components, the corresponding code has been removed.
- Added scholar_navis feature support: dark mode toggle, localization support for JS, fixed issue where the gradio_medal interface unexpectedly closes when opening the dropdown.
*/



// 将初始化逻辑封装到 DOMContentLoaded 事件中
document.addEventListener("DOMContentLoaded", function() {
    async function GptAcademicJavaScriptInit(selected_language) {
        try {
            // 1. 检查依赖函数
            if (typeof scholar_navis_init !== "function") {
                throw new Error("scholar_navis_init undefined!");
            }
            
            // 2. 执行初始化逻辑
            await scholar_navis_init(selected_language);
            find_all_modal();
            dark_mode_init();
            
            // 3. 操作 DOM 元素前检查存在性
            const custom_model_input = document.getElementById("custom_model_input");
            if (custom_model_input) {
                custom_model_input.style.display = "none";
            } else {
                console.warn("The custom_model_input element was not found.");
            }
            
            console.log(`GptAcademicJavaScriptInit: selected_language = ${selected_language}`);
        } catch (error) {
            console.error("Initialization failed:", error);
        }
    }

    // 4. 挂载到全局时使用唯一命名
    window.MyProject_GptAcademicInit = GptAcademicJavaScriptInit;
});

