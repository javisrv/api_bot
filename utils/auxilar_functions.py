import os
from langchain_openai  import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.callbacks import get_openai_callback
import json

from dotenv import load_dotenv

load_dotenv()
PATH_TEMPLATES = os.getenv('PATH_TEMPLATES')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def get_model(model_type="gpt-4") -> ChatOpenAI:
    model = ChatOpenAI(model_name=model_type)
    return model

def get_prompt(prompt_name, inputs, pydantic_object=None):
    with open(PATH_TEMPLATES, "r", encoding="utf-8") as file:
        templates = json.load(file)
    if pydantic_object:
        parser = JsonOutputParser(pydantic_object=pydantic_object)
        prompt = PromptTemplate(
            template=templates[prompt_name],
            input_variables=inputs["input"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
            )
    else:
        prompt_template = PromptTemplate.from_template(template=templates[prompt_name])
        prompt = prompt_template.format(**inputs)
    return prompt, parser if pydantic_object else None

def invoke_llm(model, prompt, parser, inputs):
    with get_openai_callback() as cb:
        if parser:
            chain = prompt | model | parser
            output = chain.invoke({"input": inputs["input"]})
            return output, cb
        else:
            output = model.invoke(prompt.format(**inputs))
            return output, cb

def parse_tokens(inputs, cb):
    token_usage = {
        "completion_tokens": cb.completion_tokens,
        "prompt_tokens": cb.prompt_tokens,
        "total_tokens": cb.total_tokens
    }
    if "tokens_used" in inputs:
        inputs["tokens_used"]["completion_tokens"] += token_usage["completion_tokens"]
        inputs["tokens_used"]["prompt_tokens"] += token_usage["prompt_tokens"]
        inputs["tokens_used"]["total_tokens"] += token_usage["total_tokens"]
    else:
        inputs["tokens_used"] = token_usage
    return inputs