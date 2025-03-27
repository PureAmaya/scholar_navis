'''
Author: scholar_navis@PureAmaya
很乱，以后慢慢整理）（
'''

# 该插件的根目录
import os
from argon2 import PasswordHasher

ph = PasswordHasher()


GPT_SUPPORT_LAMGUAGE = (
    "简体中文",
    "繁體中文",
    "English",
    "日本語",
    "Français",
    "Deutsch",
    "Русский",
    "العربية",
    "Español",
)


GPT_ACADEMIC_ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
"""gpt_academic根目录"""
SCHOLAR_NAVIS_ROOT_PATH = os.path.join(
    GPT_ACADEMIC_ROOT_PATH, "crazy_functions", "scholar_navis"
)
"""scholar navis 插件的根目录"""
WEB_SERVICES_ROOT_PATH = os.path.join(GPT_ACADEMIC_ROOT_PATH, "web_services")
"""一些WEB服务的根目录"""
NOTIFICATION_ROOT_PATH = os.path.join(GPT_ACADEMIC_ROOT_PATH, "notification")
"""一些简易通知的根目录"""
GITHUB_RELEASE_VERSION_URL = "https://raw.githubusercontent.com/PureAmaya/scholar_navis/refs/heads/main/crazy_functions/scholar_navis/version"
"""github上，获取最新版版本号的url"""


try:
    with open(os.path.join(GPT_ACADEMIC_ROOT_PATH, "version"), "r") as f:
        VERSION = f.read().strip()
except:
    VERSION = "1.0.0"


if __name__ == "__main__":
    print("")
    print(GPT_ACADEMIC_ROOT_PATH)
    print(SCHOLAR_NAVIS_ROOT_PATH)


# ! 没啥用，找个时间删了
def get_data_dir(root_dir: str):
    root_dir = os.path.join("data", root_dir)
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
    # SCHOLAR_NAVIS_ROOT_PATH/data/root_dir/sub_dir
    return root_dir


footer = """
<footer class="footer-content">
    <div class="footer-item">
        <p>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-github" viewBox="0 0 16 16">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8"/>
            </svg>
            <a href="https://github.com/PureAmaya/scholar_navis" target="_blank">Scholar Navis</a>
            <span class="version">ver. {VERSION}</span>
        </p>
    </div>
    <div class="footer-item">
        <p>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-github" viewBox="0 0 16 16">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8"/>
            </svg>
            Based on 
            <a href="https://github.com/binary-husky/gpt_academic" target="_blank">GPT Academic</a>
            <span class="version">ver. 3.83</span>
        </p>
    </div>
    <div class="footer-item">
        <p>
            <svg xmlns="http://www.w3.org/2000/svg" width="576" height="576" viewBox="0 0 576 576" fill="none">
            <defs>
                <linearGradient id="gradient1" x1="60" y1="341" x2="429.5" y2="344" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stop-color="#F9D100"/>
                <stop offset="100%" stop-color="#F97700"/>
                </linearGradient>
                <linearGradient id="gradient2" x1="513.5" y1="231" x2="143.5" y2="231" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stop-color="#F9D100"/>
                <stop offset="100%" stop-color="#F97700"/>
                </linearGradient>
                <linearGradient id="gradient3" x1="60" y1="344" x2="428.987" y2="341.811" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stop-color="#F9D100"/>
                <stop offset="100%" stop-color="#F97700"/>
                </linearGradient>
            </defs>

            <!-- Main diamond shape -->
            <path 
                d="M287.5 229L86 344.5L287.5 460L489 344.5L287.5 229Z"
                stroke="url(#gradient1)"
                stroke-width="59"
                stroke-linejoin="round"
            />

            <!-- Upper diamond shape -->
            <path
                d="M287.5 116L86 231.5L287.5 347L489 231.5L287.5 116Z"
                stroke="url(#gradient2)"
                stroke-width="59"
                stroke-linejoin="round"
            />

            <!-- Diagonal connector -->
            <path
                d="M86 344L288 229"
                stroke="url(#gradient3)"
                stroke-width="59"
                stroke-linejoin="bevel"
            />
            </svg>
                Powered by 
                <a href="https://www.gradio.app/" target="_blank">Gradio</a>
                <span class="version">ver. 5.20.0</span>
        </p>
    </div>
</footer>
""".format(VERSION=VERSION)
font_path = os.path.join('themes','fonts','SourceHanSansSC-VF.otf.woff2')
