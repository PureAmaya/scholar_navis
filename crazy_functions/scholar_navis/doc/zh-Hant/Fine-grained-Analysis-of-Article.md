作為 Scholar Navis 工具流的第四步（通常情況下，也是最後一步），使用該工具對某一篇文章進行精細的分析

分析內容主要包含以下幾點：

- 文章摘要

- 文章引言或研究背景

- 實驗方法

- 實驗結論

- 實驗的創新點

- 實驗的不足和缺陷

- 寫作手法和敘事邏輯（含寫作建議）

分析完成後，支持對整篇文章和總結內容進行對話詢問

<br>

下面的步驟不分先後，根據自身情況和需要選擇即可。

<br>1. **分析任意一篇文章**

| 项目          | 輸入提示                                                                                                      |
| ----------- | --------------------------------------------------------------------------------------------------------- |
| 選定的文章       | 上傳文章後，這裡會自動填寫（請上傳後再打開該功能）                                                                                 |
| 選擇總結庫       | 留空即可                                                                                                      |
| 輔助指令        | 通常選擇「無」（保持預設即可）。當文件過長，或希望AI預先閱讀一次時，可以選擇：<u>pre_read: AI預先閱讀內容</u>。                                        |
| 調整 GPT 偏好語言 | 可以根據自己的閱讀需要和 AI 的能力進行調整。通常情況下，GPT 會根據所選的語言進行答覆。一般情况下，默認即可。                                                |
| 使用AI輔助功能    | 在獲取文章的標題和 doi 資訊時，如果已有資訊不夠完整、或準確性不佳，詢問 AI 以獲得更加準確的資訊。但是由於過程需要上網，AI 亦需要處理時間，所以處理速度較慢。在文章數量較少、對時間要求較低時推薦使用。 |

會對上傳的文章進行分析，分析後可以進行追問。

<br>2. **分析總結庫內文章**

該步驟需要執行兩次插件。即下方的“1”和“2”需要按照順序執行。

<br>

1. 從總結庫中選定目標文章

| 项目          | 輸入提示          |
| ----------- | ------------- |
| 選定的文章       | 留空即可          |
| 選擇總結庫       | 輸入需要查看的總結庫的名字 |
| 輔助指令        | 默認即可（選擇：無）    |
| 調整 GPT 偏好語言 | 不受影響，默認即可     |
| 使用AI輔助功能    | 默認即可（選擇：禁用）   |

運行之後，根據提示打開一個新的標籤頁，可以看到這個總結庫內所有的文章。點擊文章標題（如果沒有文章標題，則為文件名，這種情況一般較少* ）可以看到對該篇文章的摘要（顯示語言為英語）。

- 選擇合心的文章後，選擇 [複製文章] 複製好，之後可以跳轉到下一步

- 如果提示複製失敗，可以選擇 [下載文章]，之後參考上述“分析任意一篇文章”即可

<br>

2. 分析選定文章

| 项目          | 輸入提示                                                                                              |
| ----------- | ------------------------------------------------------------------------------------------------- |
| 選定的文章       | 粘貼複製的內容                                                                                           |
| 選擇總結庫       | 留空即可                                                                                              |
| 輔助指令        | 通常選擇「無」（保持預設即可）。當文件過長，或希望AI預先閱讀一次時，可以選擇：<u>pre_read: AI預先閱讀內容</u>。                                |
| 調整 GPT 偏好語言 | 可以根據自己的閱讀需要和 AI 的能力進行調整。通常情況下，GPT 會根據所選的語言進行答覆。一般情况下，默認即可。                                        |
| 使用AI輔助功能    | 在獲取文章的標題和 doi 資訊時，如果已有資訊不夠完整、或準確性不佳，詢問 AI 以獲得更加準確的資訊。但是由於過程需要上網，AI 亦需要處理時間，所以處理速度較慢。在文章數量較少時推薦使用。 |

會對選定的文章進行分析，分析後可以進行追問。
