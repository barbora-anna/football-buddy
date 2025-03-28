import logging
import os
import yaml

from datetime import datetime, timedelta
from langchain_core.prompts import ChatPromptTemplate
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

    def generate_from_data(self, prompt_, data):
        prompt_template = ChatPromptTemplate.from_template(prompt_)
        prompt = prompt_template.invoke({"data": data})
        try:
            response = self.use_model().invoke(prompt)
            return response
        except Exception:
            log.exception(f"Could not fetch LLM response! Prompt: {prompt}, data: {data}")
            raise


radar = RapidDataRetriever(
    base_url="https://api-football-v1.p.rapidapi.com/v3",
    apikey=os.getenv("RAPID_APIKEY"),
    host=os.getenv("RAPID_HOST"))
# llm = ChatOpenAI(model_name="gpt-4o", temperature=0)
# model = init_chat_model("gpt-4o-mini", model_provider="openai")
#
# prompt_template = PromptTemplate.from_template(
#     template=prompts['json_description'])

if __name__ == "__main__":
    with open("prompts.yaml") as f:
        prompts = yaml.safe_load(f)

    lp = LLMProcessor("gpt-4o", "openai")
    last_match = (datetime.now() - timedelta(11)).strftime('%Y-%m-%d')
    data = radar.get_full_data(date=last_match)

    # prompt = prompt_template.invoke({"data": data[0]})
    # response = model.invoke(prompt)
    response = lp.generate_from_data(prompt_=prompts["json_description"])
    pp(response.content)

