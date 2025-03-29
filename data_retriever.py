import logging
import os
import requests
from functools import wraps
from datetime import datetime, timedelta

from pprint import pprint as pp


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

    # TODO: decorator for index validation
    def get_league_id(self, league_name: str = "Czech Liga", country_code: str = "cz") -> int:
        """
        Get source league ID by league name.
        :param league_name: The name of the league in question
        :param country_code: Two-letter country identifier (e.g. "us", "gb", "cz", etc.)
        :return: League ID
        """
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

    def get_league_fixtures(self, date, season: int = 2024):
        payload = {
            "league": self.get_league_id(),
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

    def get_full_data(self, date, season: int = 2024):
        fixtures = self.get_league_fixtures(date, season)
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








if __name__ == "__main__":
    radar = RapidDataRetriever(base_url="https://api-football-v1.p.rapidapi.com/v3",
                               apikey=os.getenv("RAPID_APIKEY"),
                               host=os.getenv("RAPID_HOST"))
    # print(radar.get_league_id(league_name="Czech Liga", country_code="cz"))

    # yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    last_match = (datetime.now() - timedelta(13)).strftime('%Y-%m-%d')
    # print(radar.get_league_fixtures(date=last_match))

    data = radar.get_full_data(date=last_match)
    pp(data)




