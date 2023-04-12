## Models used in Generative Assistants

Here you may find a list of models that currently available for use in Generative Assistants.

| model name                | container name           | model link                                                          | open-source?             | size (billion parameters) | GPU usage                 | max tokens (prompt + response) | description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
|---------------------------|--------------------------|---------------------------------------------------------------------|--------------------------|---------------------------|---------------------------|--------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| BLOOMZ 7B                 | transformers-lm-bloomz7b | [link](https://huggingface.co/bigscience/bloomz-7b1)                | yes                      | 7.1B                      | 33GB                      | 2,048 tokens                   | An open-source multilingual task-oriented large language model. BLOOMZ 7B1 comes from BLOOMZ model family (featuring 560M, 1.1B, 1.7B, 3B, 7.1B, and 176B parameter versions). Each of the models is a [BLOOM](https://huggingface.co/bigscience/bloom) model of corresponding size, fine-tuned on cross-lingual task-instruction dataset (46 languages, 16 NLP tasks).  For more details about BLOOM, refer to [this paper](https://arxiv.org/pdf/2211.05100.pdf). For more details about BLOOMZ and its dataset, refer to [this paper](https://arxiv.org/pdf/2211.01786.pdf).  |
| GPT-J 6B                  | transformers-lm-gptj     | [link](https://huggingface.co/EleutherAI/gpt-j-6b)                  | yes                      | 6B                        | 25GB                      | 2,048 tokens                   | An open-source large language model. English-only, not fine-tuned for instruction following, not capable of code generation. For more details, refer to this [GitHub repo](https://github.com/kingoflolz/mesh-transformer-jax)                                                                                                                                                                                                                                                                                                                                                   |
| GPT-3.5                   | openai-api-davinci3      | [link](https://platform.openai.com/docs/models/gpt-3-5)             | no (paid access via API) | supposedly, 175B          | - (cannot be run locally) | 4,097 tokens                   | Based on text-davinci-003 -- the largest and most capable of GPT-3/GPT-3.5 models family (featuring davinci, curie, babbage, ada models) not optimized for chat. Unlike earlier GPT-3 models, also able to understand and generate code. Unlike GPT-3.5 turbo, not optimised for chat. For more details, refer to [OpenAI website](https://platform.openai.com/docs/models/gpt-3-5).                                                                                                                                                                                             |
| ChatGPT                   | openai-api-chatgpt       | [link](https://platform.openai.com/docs/models/gpt-3-5)             | no (paid access via API) | supposedly, 175B          | - (cannot be run locally) | 4,096 tokens                   | Based on gpt-3.5-turbo -- the most capable of the entire GPT-3/GPT-3.5 models family. Optimized for chat. Able to understand and generate code. For more details, refer to [OpenAI website](https://platform.openai.com/docs/models/gpt-3-5).                                                                                                                                                                                                                                                                                                                                    |
| Open-Assistant SFT-1 12B  | transformers-lm-oasst12b | [link](https://huggingface.co/OpenAssistant/oasst-sft-1-pythia-12b) | yes                      | 12B                       | 26GB (half-precision)     | 5,120 tokens                   | An open-source large language model [Open-Assistant SFT-1 12B Model](https://huggingface.co/OpenAssistant/oasst-sft-1-pythia-12b). This is the first iteration English supervised-fine-tuning (SFT) model of the Open-Assistant project. It is based on a Pythia 12B that was fine-tuned on ~22k human demonstrations of assistant conversations collected through the https://open-assistant.io/ human feedback web app before March 7, 2023. The model is known to fail horribly at answering math and coding questions. This model is usable only for English conversations.  |