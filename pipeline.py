import logging
import os
import yaml
import sys

from datetime import datetime, timedelta
from pprint import pprint as pp

from data_retriever import RapidDataRetriever
from llm_stuff import LLMProcessor


log = logging.getLogger(__name__)

radar = RapidDataRetriever(
    base_url="https://api-football-v1.p.rapidapi.com/v3",
    apikey=os.getenv("RAPID_APIKEY"),
    host=os.getenv("RAPID_HOST"))
lp = LLMProcessor(
    model_name="gpt-4o",
    model_provider="openai")

with open("prompts.yaml") as f:
    prompts = yaml.safe_load(f)

# Get data from a desired time period
last_match = (datetime.now() - timedelta(12)).strftime('%Y-%m-%d')
matches_data = radar.get_full_data(date=last_match)
if not matches_data:
    log.info("No matches found for the day! Shutting down...")
    sys.exit(0)

# Enrich the data with LLM-generated output
for md in matches_data:
    res = lp.generate_from_data(prompt_=prompts["json_description"], data=md)
    md["llm_description"] = res.content
pp(matches_data)

# Save the data into a database


