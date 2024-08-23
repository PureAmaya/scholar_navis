這是 Scholar Navis 的附屬工具。該工具允許您以 API 的方式，從 PubMed 的 FTP 上批量下載 Open Access 文章。

下載完成後，可以進行其他有關的工作，也可以使用 Scholar Navis 的工作流程進行前沿分析。

<br>Scholar Navis 透過訪問<a href="https://www.ncbi.nlm.nih.gov/pmc/tools/oa-service/" target="_blank">OA Web Service API</a>獲取 OA 文章的位置，並訪問<a href="https://www.ncbi.nlm.nih.gov/pmc/tools/ftp/" target="_blank">FTP Service</a>下載PMC Open Access Subset Only。

PubMed:  You can use the file lists in CSV or txt format to search for the location of specific files or you can use the [<a href="https://www.ncbi.nlm.nih.gov/pmc/tools/oa-service/" target="_blank">OA Web Service API</a>.

<font color=red>請勿通過直接扒取網頁等不合法的方式批量獲取文章，這樣做是不允許的。如果您擔心會被封禁，請勿使用此功能。</font>

<br>

**以下為操作步驟（按順序執行）：**

<br>

1. **PubMed檢索文章**

按照通常方法進行檢索即可。

<br>

2. **獲取csv**

<img title="PUBMED-CSV" src="img/pubmed.png" alt="" style="zoom:50%;">

- 點擊 `save` 標籤，會彈出 `Save citations to file` 視窗，Format選擇 CSV；Selection根據自身需求、檢索結果選擇即可（如果不清楚選擇什麼，可以選擇 All results）

- 之後點擊 `Create file` 下載，就得到了需要的 csv 文件

<br>

3. **配置網絡代理（可選）**

在<a href="https://github.com/binary-husky/gpt_academic" target="_blank">GPT Academic</a> 的 config_private.py 中配置您的代理。

<br>

4. **使用 Scholar Navis 進行批量下載**

上傳 csv 後，運行該功能即可。

| 项目        | 输入提示                   |
| --------- | ---------------------- |
| 上傳保存的文章清單 | 通常已經自動填寫。內容是剛剛上傳的文件的路徑 |
| 輔助指令      | 默认即可（選擇：無）             |

<br>

5. **處理下載結果**
- 下載完成後，會顯示下載成功文章和下載失敗的文章列表，這裡可以直接跳轉到對應的 PubMed 界面，自行手工檢索或下載。（下載失敗的原因也會顯示）

- 可以找到`點擊以取得下載之文章`以下載`pubmed_openaccess_download.zip`，以及`點擊以獲取下載日誌`以下載`download_log.log`。
  
  - `pubmed_openaccess_download.zip`：所有批量下載完成的文章，點擊即可獲取。Scholar Navis 支持直接使用該壓縮包進行分析，上傳該壓縮包即可。也可以自行檢查壓縮包內的文章，進行其他的文獻閱讀任務。
  
  - `download_log.log`：本次下載任務的日誌，較為詳細地記錄了下載日期、PMID、PMCID、下載狀態和下載信息。
