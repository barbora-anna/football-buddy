import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pprint import pprint as pp

import yaml

from data_retriever import RapidDataRetriever
from db_operations import SQLiteOperations
from send_email import EmailSender
from llm_operations import OpenAIOperations


log = logging.getLogger(__name__)


class FootballBuddy:
    def __init__(self, date: str, team: str, rapidapi_url: str, rapidapi_apikey: str, rapidapi_host: str,
                 sqlite_db_name: str):
        """
        Class handling data from RapidAPI: football matches fixtures of a selected team. Handles sourcing, enhancement,
        storage, and other operations of the program.
        :param date: must be in %Y-%m-%d format, day to source fixtures from
        :param team: team of interest
        :param rapidapi_url: base url for RapidAPI queries
        :param rapidapi_apikey: personal API key for RapidAPI service
        :param rapidapi_host: RapidAPI host
        :param sqlite_db_name: the name of SQLite database
        """
        self.date = date
        self.team = team

        self.radar = RapidDataRetriever(
            base_url=rapidapi_url,
            apikey=rapidapi_apikey,
            host=rapidapi_host)
        self.oai_ops = OpenAIOperations()
        self.db_ops = SQLiteOperations(db_name=sqlite_db_name)

        with open("prompts.yaml", "r") as f:
            self.prompts = yaml.safe_load(f)

        self.schemas = {}
        for schema in ["llm_answer", "rapid_data"]:
            with open(f"json_schemas/{schema}.json", "r") as f:
                self.schemas[schema] = json.load(f)

    def get_rapidapi_data(self, season, league, country_code):
        return self.radar.get_full_data(date=self.date, season=season, league=league, country_code=country_code)

    def enrich_and_load_into_db(self, matches_data):
        self.db_ops.create_tables()

        model_name = self.prompts["json_description"]["main"]["llm"]["name"]
        llm = self.oai_ops.init_chat_model(
            model_name=model_name,
            temperature=self.prompts["json_description"]["main"]["llm"]["temperature"])

        for m in matches_data:
            if self.radar.data_is_ok(m, schema=self.schemas["rapid_data"]):
                m["llm"] = {"text": self.oai_ops.get_llm_match_description(llm=llm, match_data=m),
                            "llm": model_name}
                self.db_ops.insert_into_fixture(m)
            else:
                raise RuntimeError(f"Invalid data retrieved from Rapid API! Data: {m}")

    def fetch_fixture_data_for_llm(self):
        fixture_ids = self.db_ops.fetch_fixture_ids(self.date)
        matches = []
        for id_ in fixture_ids:
            matches.append(self.db_ops.fetch_match_data(id_))
        log.info(f"Found {len(matches)} for day {self.date}")
        return matches

    def get_json_from_response(self, llm_response):
        try:
            # Try to json loads LLM response
            if not isinstance(llm_response, dict):
                llm_response = json.loads(llm_response)
            # Check data integrity
            if self.radar.data_is_ok(data=llm_response, schema=self.schemas["llm_answer"]):
                # If ok, return data
                return llm_response
        except Exception as e:
            log.exception(f"Invalid json response from LLM! Response: {llm_response}; Err: {e}")
        # Otherwise return placeholder
        return {}

    def get_llm_insight_triggers(self, retrieved_matches_data):
        model_name = self.prompts["trigger_detection"]["main"]["llm"]["name"]
        llm = self.oai_ops.init_chat_model(
            model_name=model_name,
            temperature=self.prompts["trigger_detection"]["main"]["llm"]["temperature"])

        triggers = []
        for md in retrieved_matches_data:
            llm_response = self.oai_ops.get_llm_trigger_about_data(llm=llm, match_data=md, wanted_team=self.team)

            if json_res := self.get_json_from_response(llm_response):
                if json_res["trigger"] == "yes":
                    log.info(f"Interesting activity trigger for match ID {md['fixture']}: {json_res}")
                    json_res["fixture_id"] = md["fixture"]
                    triggers.append(json_res)
        log.info(f"Identified {len(triggers)} triggers for matches events...")
        return triggers

    def collect_valid_triggers(self, fixtures_data):
        triggers_ = self.get_llm_insight_triggers(fixtures_data)
        return [t for t in triggers_ if self.get_json_from_response(t)]
        # TODO: Run invalid triggers through a validator LLM (prompt with shots is ready in prompts.yaml)

    def format_email(self, triggers):
        llm = self.oai_ops.init_chat_model(
            model_name=self.prompts["email_formatting"]["main"]["llm"]["name"],
            temperature=self.prompts["email_formatting"]["main"]["llm"]["temperature"])

        email_data = []
        for t in triggers:
            email_data.append(self.db_ops.fetch_email_data(t["fixture_id"]))

        return self.oai_ops.format_email(llm=llm, data=email_data)


if __name__ == "__main__":

    # SETUP LOGGING
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
        level="DEBUG")
    # log.setLevel("DEBUG")

    # LOAD CONFIG
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # INSTANTIATE CLASSES
    foo_bud = FootballBuddy(
        date=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        team=config["data_config"]["team"],
        rapidapi_url=config["rapid_api"]["base_url"],
        rapidapi_host=config["rapid_api"]["host"],
        rapidapi_apikey=os.getenv("RAPID_APIKEY"),
        sqlite_db_name=config["data_config"]["db_name"])

    mailer = EmailSender(
        host=config["email_service"]["smtp"]["host"],
        port=config["email_service"]["smtp"]["port"],
        sender_email=config["email_service"]["participants_meta"]["sender"]["email"],
        sender_password=os.getenv("EMAIL_SENDER_PASSWORD")
    )

    # SOURCE MATCHES FIXTURES FROM RAPID API
    team_config = config["data_config"]["team"]

    if not (raw_data := foo_bud.get_rapidapi_data(season=team_config["season"], league=team_config["league"],
                                                  country_code=team_config["country_code"])):
        log.info(f"No matches found for date {foo_bud.date}. Shutting down...")
        sys.exit(0)

    # ENRICH DATA WITH LLM-GENERATED SUMMARY AND STORE IT
    foo_bud.enrich_and_load_into_db(raw_data)

    # FETCH RELEVANT DATA FOR LLM
    fixture_data = foo_bud.fetch_fixture_data_for_llm()

    # GET TRIGGERS FOR INTERESTING EVENTS
    trigger_event_data = foo_bud.collect_valid_triggers(fixture_data)

    # LET LLM GENERATE AN EMAIL FROM TRIGGERED DATA
    email_body = foo_bud.format_email(trigger_event_data)

    # FORMAT AND SEND EMAIL
    formatted_mail = mailer.format_email(
            subject=config["email_service"]["email_params"]["subject"],
            receiver_email=config["email_service"]["participants_meta"]["receiver"]["email"],
            content=email_body,
            is_html=True)

    mailer.send_email(formatted_mail)
