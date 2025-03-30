import logging

import yaml
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

log = logging.getLogger(__name__)


class OpenAIOperations:
    def __init__(self):
        with open("prompts.yaml", "r") as f:
            self.prompts = yaml.safe_load(f)

    def init_chat_model(self, model_name, temperature, **kwargs):
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            **kwargs)

    def llm_query_data(self, llm, prompt, placeholder_and_data: dict):
        template = PromptTemplate.from_template(prompt)
        chain = template | llm

        log.debug(f"Querying LLM {llm}...")
        response = chain.invoke(placeholder_and_data)
        return response.content

    def get_llm_match_description(self, llm, match_data):
        log.debug("Working on match description from fixture metadata...")
        return self.llm_query_data(
            llm=llm,
            prompt=self.prompts["json_description"]["main"]["prompts"]["sys"],
            placeholder_and_data={"data": match_data})

    def get_llm_trigger_about_data(self, llm, match_data, wanted_team):
        log.debug(f"Getting triggers for events and {wanted_team}...")
        return self.llm_query_data(
            llm=llm,
            prompt=self.prompts["trigger_detection"]["main"]["prompts"]["sys"],
            placeholder_and_data={"data": match_data, "team": wanted_team})

    def format_email(self, llm, data):
        log.debug("Formatting email body...")
        return self.llm_query_data(
            llm=llm,
            prompt=self.prompts["email_formatting"]["main"]["prompts"]["sys"],
            placeholder_and_data={"data": data})