import logging
import sqlite3


log = logging.getLogger(__name__)

sql_queries = {
    "fixture_ids": '''
        SELECT fixture_id 
        FROM Fixture 
        WHERE date LIKE ?
        ''',
    "events_data": '''
        SELECT assist, comments, detail, player, time, type
        FROM Events
        WHERE fixture_id = ?
        ''',
    "stats_data": '''
        SELECT t.name AS team_name, s.type, s.value
                FROM Stats s
                JOIN Teams t ON s.team_id = t.team_id
                WHERE s.fixture_id = ?
                ''',
}

class DatabaseManager:
    def __init__(self, db_name):
        self.db = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def create_tables(self, script_filename):
        with open(script_filename, "r") as f:
            script = f.read()
        calls = script.split(";") # TODO: Problematic if script contains ;
        for c in calls:
            if c.strip():
                try:
                    self.cursor.execute(c)
                except sqlite3.OperationalError as e:
                    log.exception(f"Error executing SQL from file {script_filename}: {e}")
        self.conn.commit()

    def _insert_into(self, table_name, columns, values):
        query = f'''
                INSERT OR IGNORE INTO {table_name} ({", ".join(columns)})
                VALUES ({", ".join(["?"] * len(values))})
                '''
        try:
            with self.conn:
                self.cursor.execute(query, values)
        except sqlite3.IntegrityError as e:
            log.exception(f"Data insert failed for {table_name}. Error: {e}")

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
        self._insert_into(table_name="Fixture", columns=columns, values=values)

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
        self._insert_into(table_name="Teams", columns=columns, values=values)

        home_team = fixture_data["about"]["teams"]["home"]
        values = [
            f_id,
            "home",
            home_team["id"],
            home_team["logo"],
            home_team["name"],
            home_team["winner"]
        ]
        self._insert_into(table_name="Teams", columns=columns, values=values)

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
                self._insert_into(table_name="Score", columns=columns, values=values)

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
            self._insert_into(table_name="Events", columns=columns, values=values)

        stats = fixture_data["stats"]
        columns = ["fixture_id", "team_id", "type", "value"]
        for team in stats:
            for s in team["statistics"]:
                values = [
                    f_id,
                    team["team"]["id"],
                    s["type"],
                    s["value"]]
                self._insert_into(table_name="Stats", columns=columns, values=values)

        columns = ["fixture_id", "text", "llm"]
        values = [f_id, fixture_data["llm"]["description"], fixture_data["llm"]["model"]]
        self._insert_into(table_name="Commentary", columns=columns, values=values)

    def fetch_fixture_ids(self, date):
        self.cursor.execute(sql_queries["fixture_ids"], (date + "%",))
        return [row[0] for row in self.cursor.fetchall()]

    def fetch_events_data(self, fixture_id):
        self.cursor.execute(sql_queries['events_data'], (fixture_id,))
        return [dict(row) for row in self.cursor.fetchall()]

    def fetch_stats_data(self, fixture_id):
        self.cursor.execute(sql_queries["stats_data"], (fixture_id,))
        return [dict(row) for row in self.cursor.fetchall()]

    def fetch_match_data(self, fixture_id):
        events = self.fetch_events_data(fixture_id)
        stats = self.fetch_stats_data(fixture_id)
        return {"fixture": fixture_id, "events": events, "stats": stats}



if __name__ == "__main__":
    log.setLevel("DEBUG")
    dam = DatabaseManager(db_name="football_matches.db")
    dam.connect()
    # dam.execute_sql_script("create_tables.sql")

    fixture_ids = dam.fetch_fixture_ids("2025-03-16")
    matches = []
    for id_ in fixture_ids:
        matches.append(dam.fetch_match_data(id_))

