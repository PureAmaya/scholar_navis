As the third step in the Scholar Navis workflow, use this tool to analyze articles and uncover more focused research directions or results information.

After completing the previous steps and gaining a general understanding of the current state, you can use this tool for a deeper level of comprehension.

<br><font color=red>This tool supports AI interaction. After running any feature of the tool, you can engage in conversation.</font>

When there are necessary areas for further in-depth exploration, AI may remind you to use the "find" command and conduct a detailed analysis of the literature.

- find" command: Locate the article of interest (details below)

- Fine-grained Analysis of Article: Conduct a more in-depth analysis of a specific article

<br>

The following steps are not in any particular order; choose according to your own situation and needs.

<br>1. **View Summary Content**

| Item                             | Input Prompt                                                                                                                                                          |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Select summary library           | Enter the name of the summary library you want to view                                                                                                                |
| Instruction parameters           | Leave blank                                                                                                                                                           |
| Auxiliary instructions           | Default (select: No command)                                                                                                                                          |
| Adjust GPT's language preference | You can adjust it according to your reading needs and AI capabilities. By default, GPT will respond in the selected language. Generally, the default setting is fine. |

The previous summary content will be displayed.

<br>2. **Direct Conversation**

| Item                             | Input Prompt                                                                                                                                                          |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Select summary library           | Enter the name of the summary library for the conversation                                                                                                            |
| Instruction parameters           | Leave blank                                                                                                                                                           |
| Auxiliary instructions           | Default (select: No command)                                                                                                                                          |
| Adjust GPT's language preference | You can adjust it according to your reading needs and AI capabilities. By default, GPT will respond in the selected language. Generally, the default setting is fine. |

After running the tool, you can directly ask questions about the summary content. You can copy and paste the content you want to ask about, and AI will typically respond in the preferred language.

<br>3. **Draw Mind Map**

| Item                             | Input Prompt                                                                                                                                                                                                                                                               |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Select summary library           | Enter the name of the summary library for the mind map                                                                                                                                                                                                                     |
| Instruction parameters           | Please enter a number: 1 - Flowchart, 2 - Sequence Diagram, 3 - Class Diagram, 4 - Pie Chart, 5 - Gantt Chart, 6 - State Diagram, 7 - Entity-Relationship Diagram, 8 - Quadrant Prompt Diagram, 9 - Mind Map (default, if no number is entered, this graphic will be used) |
| Adjust GPT's language preference | Invalid                                                                                                                                                                                                                                                                    |
| Auxiliary instructions           | Select <u>draw: Create Mind Map [Built-in Function of gpt_academic, language preference may be ineffective] (parameters required)</u>                                                                                                                                      |

Please note that this feature calls a built-in function of gpt_academic (provided by [Menghuan1918](https://github.com/Menghuan1918)), and Scholar Navis cannot adjust the language of GPT's response.

<br>4. **Trace Summary Content (Find Source Articles)**

| Item                             | Input Prompt                                                                                                                                                          |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Select summary library           | Enter the name of the summary library for tracing                                                                                                                     |
| Instruction parameters           | The content to trace. It can be content copied and pasted directly from the summary or questions related to the summary content                                       |
| Adjust GPT's language preference | You can adjust it according to your reading needs and AI capabilities. By default, GPT will respond in the selected language. Generally, the default setting is fine. |
| Auxiliary instructions           | Select <u>find: Find source of summarization content (parameters required)</u>                                                                                        |

If the desired article is not found, try a few times; if no results are found after multiple attempts, you can also try adjusting the content to trace. Supports conversation.

<br>4. **Formulate a Topic**

| Item                             | Input Prompt                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Select summary library           | Enter the name of the summary library for topic formulation                                                                                                                                                                                                                                                                                                                                                                                           |
| Instruction parameters           | Set requirements for GPT to summarize the topic. You can leave it blank, in which case the default requirement will be used: "First off, the topic has to be right, with a solid basis for it to be pursued; secondly, it needs to have a pretty good amount of originality, something that differs from the info I'm giving you; and lastly, it should be somewhat pioneering, aiming to focus on areas that haven't been touched on by others yet." |
| Adjust GPT's language preference | You can adjust it according to your reading needs and AI capabilities. By default, GPT will respond in the selected language. Generally, the default setting is fine.                                                                                                                                                                                                                                                                                 |
| Auxiliary instructions           | Select <u>topic: Formulate a topic (parameters required)</u>                                                                                                                                                                                                                                                                                                                                                                                          |

These large language models are not specialized academic models for any particular field, <font color=red>so the formulated topics may not be suitable and are for reference only.</font> Supports conversation.
