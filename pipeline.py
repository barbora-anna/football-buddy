import logging
import os
import yaml
import sys

import jsonschema
from datetime import datetime, timedelta
from pprint import pprint as pp

from data_schema import schema
from data_retriever import RapidDataRetriever
from llm_stuff import LLMProcessor
from db_operations import DatabaseManager


log = logging.getLogger(__name__)


llm_for_commentary = "gpt-4o"


radar = RapidDataRetriever(
    base_url="https://api-football-v1.p.rapidapi.com/v3",
    apikey=os.getenv("RAPID_APIKEY"),
    host=os.getenv("RAPID_HOST"))
lp = LLMProcessor(
    model_name=llm_for_commentary,
    model_provider="openai")
dam = DatabaseManager(db_name="football_matches.db")

with open("prompts.yaml") as f:
    prompts = yaml.safe_load(f)

# Get data from a desired time period
last_match = (datetime.now() - timedelta(13)).strftime('%Y-%m-%d')
matches_data = radar.get_full_data(date=last_match)
for i in matches_data:
    try:
        jsonschema.validate(instance=i, schema=schema)
    except jsonschema.exceptions.ValidationError as ve:
        log.fatal(f"Unable to process data from API! Invalid schema: {ve}")
        raise

if not matches_data:
    log.info("No matches found for the day! Shutting down...")
    sys.exit(0)

# Enrich the data with LLM-generated output
for md in matches_data:
    res = lp.generate_from_data(prompt_=prompts["json_description"], data=md)
    md["llm"] = {"description": res.content,
                 "model": llm_for_commentary}
pp(matches_data)

# Create tables in the database
dam.connect()
dam.create_tables("create_tables.sql")
for match in matches_data:
    dam.insert_into_fixture(match)
dam.close()






