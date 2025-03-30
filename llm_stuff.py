import logging
import os
import yaml

from datetime import datetime, timedelta
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain.prompts import FewShotPromptTemplate
from langchain.chat_models import init_chat_model
from data_retriever import RapidDataRetriever

from pprint import pprint as pp


log = logging.getLogger(__name__)


class LLMProcessor:
    def __init__(self, model_name, model_provider):
        self.model_name = model_name
        self.provider = model_provider
        self.model = None

    def use_model(self):
        if not self.model:
            self.model = init_chat_model(self.model_name, model_provider=self.provider)
        return self.model

    def generate_from_data(self, prompt_, vars_):
        prompt_template = ChatPromptTemplate.from_template(prompt_)
        prompt = prompt_template.invoke(vars_)
        try:
            response = self.use_model().invoke(prompt)
            return response
        except Exception:
            log.exception(f"Could not fetch LLM response! Prompt: {prompt}, data: {vars_}")
            raise

    def generate_from_data_shots(self, prompt_, data, examples):
        prompt = FewShotPromptTemplate(
            example_prompt=PromptTemplate(
                input_variables=["input", "output"],
                template="{input} => {output}"
            ),
            examples=examples,
            prefix=prompt_,
            suffix="DATA: {data}",
            input_variables=["data"])

        formatted_prompt = prompt.format(data=data)
        try:
            response = self.use_model().invoke(formatted_prompt)
            return response
        except Exception:
            log.exception(f"Fetching LLM response to multiple shots failed! Full prompt: {formatted_prompt}")
            raise

if __name__ == "__main__":

    with open("prompts.yaml", "r") as f:
        prompts = yaml.safe_load(f)

    lp = LLMProcessor("gpt-4o", "openai")

    # last_match = (datetime.now() - timedelta(11)).strftime('%Y-%m-%d')

    # prompt = prompt_template.invoke({"data": data[0]})
    # response = model.invoke(prompt)
    # response = lp.generate_from_data(prompt_=prompts["json_description"])
    response = lp.generate_from_data_shots(prompt_=prompts["anomaly_detection"]["fix"]["sys"],
                                           data="{'yeah': 'idk'}",
                                           examples=prompts["anomaly_detection"]["fix"]["shots"])
    pp(response.content)

