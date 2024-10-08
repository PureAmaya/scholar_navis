As the first step in the Scholar Navis workflow, use this feature to load the literature to be analyzed.

<br>Interaction with AI is not supported; all operations are performed offline.

If you need to upload articles, please upload them first before running the relevant function.

**Before the subsequent analysis is completed, you can add as many PDF articles as you like, and you can also freely modify keywords to optimize the content and direction of the analysis.**

<br>

The following steps are not in any particular order; choose according to your own situation and needs.

<br>1. **When creating a new summary library:**

| Item                                     | Input Prompt                                                                                                                                                                                            |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| File upload path or URL                  | Upload a single PDF article or a compressed package containing multiple PDF articles. Ensure the upload is complete before starting this function (it will be automatically filled in).                 |
| Create or select a summarization library | Enter a new, non-existent name for the summary library. You can leave it blank to display all existing summary libraries.                                                                               |
| Instruction parameters                   | Enter your keywords. AI will analyze around these keywords, establishing an analysis direction for AI. Use Chinese commas (，) or English commas (,) to separate, which can be words or nominal phrases. |
| Auxiliary instructions                   | <u>key: query or update keywords (parameters required)</u>                                                                                                                                              |

<br>2. **When adding articles to an existing summary library:**

| Item                                     | Input Prompt                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| File upload path or URL                  | Upload a single PDF article or a compressed package containing multiple PDF articles. Ensure the upload is complete before starting this function (it will be automatically filled in).                                                                                                                                                                                                                                            |
| Create or select a summarization library | Enter an existing name for the summary library. You can leave it blank to display all existing summary libraries.                                                                                                                                                                                                                                                                                                                  |
| Instruction parameters                   | <b>**If prompted for no keywords**</b><br>       Enter your keywords. AI will analyze around these keywords, establishing an analysis direction for AI. Use Chinese commas (，) or English commas (,) to separate, which can be words or nominal phrases<br><b>**If prompted for existing keywords**</b><br>    Ignore this item if you do not want to update the keywords; if you want to update the keywords, enter them normally |
| Auxiliary instructions                   | <b>**If prompted for no keywords**</b><br>    <u>key: query or update keywords (parameters required)</u><br><b>****If prompted for existing keywords****</b><br>    Ignore this item if you do not want to update the keywords; if you want to update the keywords, please select <u>key: query or update keywords (parameters required).</u>                                                                                      |

<br>3. **Only update keywords:**

| Item                                     | Input Prompt                                                                                                                                                                                           |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| File upload path or URL                  | Leave blank.                                                                                                                                                                                           |
| Create or select a summarization library | Enter an existing name for the summary library. You can leave it blank to display all existing summary libraries.                                                                                      |
| Instruction parameters                   | Enter your keywords. AI will analyze around these keywords, establishing an analysis direction for AI. Use Chinese commas (，) or English commas (,) to separate, which can be words or nominal phrases |
| Auxiliary instructions                   | Please select <u>key-force: force update keywords (parameters required)</u>                                                                                                                            |

<br>4. **Only view keywords:**

| Item                                     | Input Prompt                                                                                                      |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| File upload path or URL                  | Leave blank.                                                                                                      |
| Create or select a summarization library | Enter an existing name for the summary library. You can leave it blank to display all existing summary libraries. |
| Instruction parameters                   | Leave blank.                                                                                                      |
| Auxiliary instructions                   | Default (select: No command)                                                                                      |
