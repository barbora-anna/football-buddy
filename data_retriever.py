import logging
import os
from datetime import datetime, timedelta
from functools import wraps
from pprint import pprint as pp

import jsonschema
import requests

log = logging.getLogger(__name__)


def response_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if not res.ok:
            raise RuntimeError(f"Function {func.__name__} failed! Response: {res}")
        return res.json()
    return wrapper


class RapidDataRetriever:
    def __init__(self, base_url, apikey, host):
        self.headers = {
            "x-rapidapi-key": apikey,
            "x-rapidapi-host": host}
        self.url = base_url
        self.league_id = None

    @response_handler
    def get_(self, url, **kwargs):
        return requests.get(url, headers=self.headers, **kwargs)

    def get_league_id(self, league_name, country_code) -> int:
        if not self.league_id:
            payload = {
                "code": country_code,
                "current": "true"}
            res = self.get_(f"{self.url}/leagues", params=payload)

            for i in res.get("response", {}):
                if i.get("league", {}).get("name") == league_name:
                    self.league_id = i["league"]["id"]
                    log.info(f"Got league ID for {league_name}: {self.league_id}")
                    break
            else:
                raise RuntimeError(f"League {league_name} not found! Response: {res}")
        return self.league_id

    def get_league_fixtures(self, date, season, league, country_code):
        payload = {
            "league": self.get_league_id(league, country_code),
            "date": date,
            "season": season}
        res = self.get_(f"{self.url}/fixtures", params=payload)

        if fixtures := res.get("response"):
            log.info(f"Found {len(fixtures)} matches from {date}")
            return fixtures
        else:
            log.info(f"No matches from {date}")
            return []

    def get_fixture_meta(self, url, fixture_id):
        payload = {"fixture": fixture_id}
        res = self.get_(url, params=payload)

        if meta := res.get("response"):
            log.info(f"Retrieved metadata from url: {url}; fixture ID: {fixture_id}")
            return meta
        else:
            log.info(f"No events found for fixture {fixture_id}")
            return []

    def get_full_data(self, date, season, league, country_code):
        fixtures = self.get_league_fixtures(date, season, league, country_code)
        full_data = []

        for f in fixtures:
            f_id = f["fixture"].pop("id")
            events = self.get_fixture_meta(f"{self.url}/fixtures/events", fixture_id=f_id)
            stats = self.get_fixture_meta(f"{self.url}/fixtures/statistics", fixture_id=f_id)

            full_data.append({
                "fixture_id": f_id,
                "about": f,
                "events": events,
                "stats": stats})

        return full_data

    @staticmethod
    def data_is_ok(data: dict, schema) -> bool:
        try:
            jsonschema.validate(instance=data, schema=schema)
            return True
        except jsonschema.exceptions.ValidationError as ve:
            log.exception(f"Data does not match schema! Detail: {ve}")
            return False


if __name__ == "__main__":
    radar = RapidDataRetriever(base_url="https://api-football-v1.p.rapidapi.com/v3",
                               apikey=os.getenv("RAPID_APIKEY"),
                               host=os.getenv("RAPID_HOST"))

    yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    data = radar.get_full_data(date=yesterday)
    pp(data)




