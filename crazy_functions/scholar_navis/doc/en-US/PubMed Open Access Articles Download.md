This is an affiliated tool of Scholar Navis. The tool allows you to batch download Open Access articles from PubMed's FTP using the API method.

After the download is complete, you can perform other related tasks or use Scholar Navis' workflow for cutting-edge analysis.

<br>Scholar Navis retrieves the locations of OA articles by accessing the <a href="https://www.ncbi.nlm.nih.gov/pmc/tools/oa-service/" target="_blank">OA Web Service API</a> and downloads the PMC Open Access Subset Only by accessing the <a href="https://www.ncbi.nlm.nih.gov/pmc/tools/ftp/" target="_blank">FTP Service</a>.

PubMed: You can use the file lists in CSV or txt format to search for the location of specific files or you can use the [<a href="https://www.ncbi.nlm.nih.gov/pmc/tools/oa-service/" target="_blank">OA Web Service API</a>].

<font color=red>Do not obtain articles in bulk through illegal methods such as scraping web pages, as this is not permitted. If you are concerned about being banned, please DON'T USE THIS FUNCTION.</font>

<br>

**The following are the steps to follow (in order):**

<br>

1. **Search for Articles in PubMed**

Search using the usual methods.

<br>

2. ****Obtain CSV****

<img title="PUBMED-CSV" src="img/pubmed.png" alt="" style="zoom:50%;">

- Click on `save` to bring up the `Save citations to file` dialog, select Format as CSV; `Selection` should be based on your needs and the search results (if you are unsure, you can select All results).

- After that, click `Create file` to download, and you will obtain the required CSV file.

<br>

3. **Configure Network Proxy (Optional**)

Configure your proxy in the <a href="https://github.com/binary-husky/gpt_academic" target="_blank">GPT Academic</a>'s config_private.py file.

<br>

4. **Use Scholar Navis for Bulk Download**

Upload the  csv files and run this function.

| Item                      | Input Prompt                                                                                   |
| ------------------------- | ---------------------------------------------------------------------------------------------- |
| Upload saved article list | Usually already filled in automatically. The content is the path of the file you just uploaded |
| Auxiliary instruction     | Default is fine (choose: No command)                                                           |

<br>

5. **Handle Download Results**
- After the download is complete, a list of successfully downloaded articles and failed downloads will be displayed. You can directly navigate to the corresponding PubMed interface to manually search or download (the reason for the failure will also be displayed).

- You can find `Click to get the article` to download `pubmed_openaccess_download.zip` and `Click to get the download log`to download `download_log.log` in the file download area (also in the conversation list).
  
  - `pubmed_openaccess_download.zip`: All articles downloaded in bulk. Click to access. Scholar Navis supports direct analysis using this compressed package, and you can upload this package to do so. You can also review the articles within the compressed package for other literature reading tasks.
  
  - `download_log.log`: The log of this download task, which records the download date, PMID, PMCID, download status, and download information in detail.
