

Comments analysis
--

In [Sentiment Analysis nb](https://github.com/c-azb/comments-analysis-llm-django/tree/main/Sentiment%20Analysis%20nb), you can find the fine-tuning process for sentiment classification using the distilBERT pretrained model and the Hugging Face libraries. You can also find a notebook to create the comments overall summarizer using Llama, Langchain, and Ollama.

On [sent_web](https://github.com/c-azb/comments-analysis-llm-django/tree/main/sent_web) we integrate the AI models developed on "Sentiment Analysis nb" with a web application using Django.

The web application allows the user to upload a file that contains the comments. On submit, the comments are first classified individually by the fine-tuned DistilBert model, and basic statistics are calculated. After the comments are analyzed by an LLM to provide an overall summary. The user can create an account or login to save the analysis and search for public analyses made by other users.