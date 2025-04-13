/*
Original Author: gpt_academic@binary-husky

Modified by PureAmaya on 2025-03-18
- The initialization of JS is handed over to JS itself for execution.

Modified by PureAmaya on 2025-03-14
- Resolve the occasional GptAcademicJavaScriptInit undefined error.

Modified by PureAmaya on 2024-12-28
- Due to the removal of certain features/replacement by gradio components, the corresponding code has been removed.
- Added scholar_navis feature support: dark mode toggle, localization support for JS, fixed issue where the gradio_medal interface unexpectedly closes when opening the dropdown.
*/

// 等待依赖加载完毕
async function waitForDependency() {
    const maxAttempts = 10;
    let attempts = 0;
    return new Promise((resolve, reject) => {
      const checkInterval = setInterval(() => {
        if (typeof scholar_navis_init === 'function') {
          clearInterval(checkInterval);
          resolve();
        } else if (attempts >= maxAttempts) {
          clearInterval(checkInterval);
          reject(new Error('scholar_navis_init not found after retries'));
        }
        attempts++;
      }, 100); // 每 100ms 检查一次
    });
  }


// 将初始化逻辑封装到 DOMContentLoaded 事件中
    async function GptAcademicJavaScriptInit() {
        try {
            await waitForDependency(); // 等待依赖就绪
            // 2. 执行初始化逻辑
            await scholar_navis_init();
            find_all_modal();
            dark_mode_init();
            
            // 3. 操作 DOM 元素前检查存在性
            const custom_model_input = document.getElementById("custom_model_input");
            if (custom_model_input) {
                custom_model_input.style.display = "none";
            } else {
                console.warn("The custom_model_input element was not found.");
            }
            console.log("GptAcademic JavaScript initialization complete.");
        } catch (error) {
            console.error("Initialization failed:", error);
        }
    }


GptAcademicJavaScriptInit();
