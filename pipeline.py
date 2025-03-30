import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pprint import pprint as pp

import jsonschema
import yaml

from data_retriever import RapidDataRetriever
from db_operations import DatabaseManager
from llm_stuff import LLMProcessor
from send_email import EmailSender

# INIT LOGGER
log = logging.getLogger(__name__)
log.setLevel("DEBUG")

# LOAD CONFIG FILE
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


llm_for_commentary = "gpt-4o"
llm_for_evaluation = "..."

# INSTANTIATE CLASSES
radar = RapidDataRetriever(
    base_url="https://api-football-v1.p.rapidapi.com/v3",
    apikey=os.getenv("RAPID_APIKEY"),
    host=os.getenv("RAPID_HOST"))

lp = LLMProcessor(
    model_name=llm_for_commentary,
    model_provider="openai")

dam = DatabaseManager(db_name="football_matches.db")

es = EmailSender(
    host='smtp.seznam.cz',
    port=465,
    sender_email=os.getenv("EMAIL_SENDER_ADDRESS"),
    sender_password=os.getenv("EMAIL_SENDER_PASSWORD"))

# LOAD SCHEMAS FOR JSON VALIDATION
schemas = {}
for schema in ["llm_answer", "rapid_data"]:
    with open(f"json_schemas/{schema}.json", "r") as f:
        schemas[schema] = json.load(f)

# LOAD PROMPTS
with open("prompts.yaml") as f:
    prompts = yaml.safe_load(f)

# GET DATA FROM A DESIRED TIME PERIOD AND VALIDATE JSON
last_match = (datetime.now() - timedelta(13)).strftime('%Y-%m-%d')
matches_data = radar.get_full_data(date=last_match)
for i in matches_data:
    try:
        jsonschema.validate(instance=i, schema=schemas["rapid_data"])
    except jsonschema.exceptions.ValidationError as ve:
        log.fatal(f"Unable to process data from API! Invalid schema: {ve}")
        raise

# SHUT DOWN IF NOT MATCHES FOUND
if not matches_data:
    log.info("No matches found for the day! Shutting down...")
    sys.exit(0)

# ENRICH DATA WITH LLM-GENERATED COMMENT
for md in matches_data:
    res = lp.generate_from_data(prompt_=prompts["json_description"], vars={"data": md})
    md["llm"] = {"description": res.content,
                 "model": llm_for_commentary}
pp(matches_data)

# CONNECT TO DB, CREATE TABLES IF NOT EXISTING, AND LOAD DATA
dam.connect()
dam.create_tables("sql_scripts/create_tables.sql")
for match in matches_data:
    dam.insert_into_fixture(match)

# RETRIEVE DATA OF INTEREST
fixture_ids = dam.fetch_fixture_ids("2025-03-16")
matches = []
for id_ in fixture_ids:
    matches.append(dam.fetch_match_data(id_))

# LET LLM FIND TRIGGERS
triggered_matches = []
for m in matches:
    res = lp.generate_from_data(prompt_=prompts["anomaly_detection"]["main"], vars_={"team": "Slavia", "data": m})
    res_json = json.loads(res.content)

    try:
        jsonschema.validate(instance=res_json, schema=schemas["llm_answer"])
    except jsonschema.exceptions.ValidationError as ve:
        # LET LLM CORRECT STRUCTURE
        res_json = lp.generate_from_data_shots(
            data=m,
            prompt_=prompts["anomaly_detection"]["fix"]["sys"],
            examples=prompts["anomaly_detection"]["fix"]["shots"])
        try:
            jsonschema.validate(instance=res_json, schema=schemas["llm_answer"])
        except jsonschema.exceptions.ValidationError as ve:
            log.error(f"Invalid json data when getting trigger from LLM. Data: {res_json}; Original: {res.content}")
            continue

    if res["answer"] == "yes":
        triggered_matches.append(m["fixture"])

for match in triggered_matches:
    ...

# TODO: objectify, simplify





# CLOSE DB CONNECTION
dam.close()

