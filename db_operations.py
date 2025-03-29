import logging
import sqlite3


log = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_name):
        self.db = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def flatten_dict(self, nested_dict, parent_key='', sep='_'):
        items = []
        for k, v in nested_dict.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def create_tables(self, script_filename):
        with open(script_filename, "r") as f:
            script = f.read()
        calls = script.split(";")
        for c in calls:
            if c.strip():
                try:
                    self.cursor.execute(c)
                except sqlite3.OperationalError as e:
                    log.exception(f"Error executing SQL: {e}")
        self.conn.commit()

    def insert_into(self, table_name, columns, values):
        query = f'''
        INSERT OR IGNORE INTO {table_name} ({", ".join(columns)})
        VALUES ({", ".join(["?"] * len(values))})
        '''
        self.cursor.execute(query, values)

    def insert_into_fixture(self, fixture_data):
        f_id = fixture_data["fixture_id"]

        fixture = fixture_data["about"]["fixture"]
        status = fixture["status"]
        league = fixture_data["about"]["league"]
        columns = [
            "fixture_id", "date", "referee", "timestamp", "timezone", "elapsed_mins", "extra_mins", "status",
            "league", "season"]
        values = [
            f_id,
            fixture["date"],
            fixture["referee"],
            fixture["timestamp"],
            fixture["timezone"],
            status["elapsed"],
            status["extra"],
            status["long"],
            league["name"],
            league["season"]
        ]
        self.insert_into(table_name="Fixture", columns=columns, values=values)
        self.conn.commit()

        away_team = fixture_data["about"]["teams"]["away"]
        columns = [
            "fixture_id", "team_type", "team_id", "logo", "name", "winner"]
        values = [
            f_id,
            "away",
            away_team["id"],
            away_team["logo"],
            away_team["name"],
            away_team["winner"]
        ]
        self.insert_into(table_name="Teams", columns=columns, values=values)
        self.conn.commit()

        home_team = fixture_data["about"]["teams"]["home"]
        values = [
            f_id,
            "home",
            home_team["id"],
            home_team["logo"],
            home_team["name"],
            home_team["winner"]
        ]
        self.insert_into(table_name="Teams", columns=columns, values=values)
        self.conn.commit()

        score = fixture_data["about"]["score"]
        columns = ["fixture_id", "score_type", "team_id", "score_value"]
        for score_type in ["extratime", "fulltime", "halftime", "penalty"]:
            for team_id in ["away", "home"]:
                values = [
                    f_id,
                    score_type,
                    team_id,
                    score[score_type][team_id]
                ]
                self.insert_into(table_name="Score", columns=columns, values=values)
                self.conn.commit()

        events = fixture_data["events"]
        columns = [
            "fixture_id", "assist", "comments", "detail", "player", "team_id", "time", "type"]
        for e in events:
            time = e["time"]["elapsed"] + e["time"]["extra"] if e["time"]["extra"] else e["time"]["elapsed"]

            values = [
                f_id,
                e["assist"]["name"],
                e["comments"],
                e["detail"],
                e["player"]["name"],
                e["team"]["id"],
                time,
                e["type"]
            ]
            self.insert_into(table_name="Events", columns=columns, values=values)
            self.conn.commit()

        stats = fixture_data["stats"]
        columns = ["fixture_id", "team_id", "type", "value"]
        for team in stats:
            for s in team["statistics"]:
                values = [
                    f_id,
                    team["team"]["id"],
                    s["type"],
                    s["value"]]
                self.insert_into(table_name="Stats", columns=columns, values=values)
                self.conn.commit()

        columns = ["fixture_id", "text", "llm"]
        values = [f_id, fixture_data["llm"]["description"], fixture_data["llm"]["model"]]
        self.insert_into(table_name="Commentary", columns=columns, values=values)
        self.conn.commit()


if __name__ == "__main__":
    dam = DatabaseManager(db_name="football_matches.db")
    dam.connect()
    dam.create_tables("create_tables.sql")


