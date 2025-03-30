import logging
import sqlite3


log = logging.getLogger(__name__)


class SQLite:
    def __init__(self, db_name):
        self.db = db_name

    def __enter__(self):
        self.conn = sqlite3.connect(self.db)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            log.error(f"SQLite error: {exc_type}, {exc_value}")
        self.conn.commit()
        self.conn.close()


class SQLiteOperations:
    def __init__(self, db_name):
        self.wrapper = SQLite(db_name)
        self.queries = {
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
                SELECT Teams.name, Stats.type, Stats.value
                FROM Stats
                JOIN Teams ON Stats.team_id = Teams.team_id
                WHERE Stats.fixture_id = ?
                ''',
            "email_data_teams": '''
                SELECT Teams.name, Teams.goals
                FROM Teams
                WHERE Teams.fixture_id = ?;
                ''',
            "email_data_text": '''
                SELECT Commentary.text
                From Commentary
                WHERE Commentary.fixture_id = ?'''}

    def create_tables(self, script_filename: str = "sql_scripts/create_tables.sql"):
        with open(script_filename, "r") as f:
            script = f.read()
        calls = script.split(";") # TODO: Problematic if script contains ;

        with self.wrapper as db:
            for c in calls:
                if c.strip():
                    try:
                        db.cursor.execute(c)
                    except sqlite3.OperationalError as e:
                        log.exception(f"Error executing SQL from file {script_filename}: {e}")

    def _insert_into(self, table_name, columns, values):
        query = f'''
                INSERT OR IGNORE INTO {table_name} ({", ".join(columns)})
                VALUES ({", ".join(["?"] * len(values))})
                '''
        with self.wrapper as db:
            try:
                db.cursor.execute(query, values)
            except sqlite3.IntegrityError as e:
                log.exception(f"Wrong data format for table {table_name}. Error: {e}")
                raise
            except Exception as e:
                log.exception(f"Exception when inserting data: {e}")

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
            "fixture_id", "team_type", "team_id", "logo", "name", "winner", "goals"]
        values = [
            f_id,
            "away",
            away_team["id"],
            away_team["logo"],
            away_team["name"],
            away_team["winner"],
            fixture_data["about"]["goals"]["away"]
        ]
        self._insert_into(table_name="Teams", columns=columns, values=values)

        home_team = fixture_data["about"]["teams"]["home"]
        values = [
            f_id,
            "home",
            home_team["id"],
            home_team["logo"],
            home_team["name"],
            home_team["winner"],
            fixture_data["about"]["goals"]["home"]
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
        values = [f_id, fixture_data["llm"]["text"], fixture_data["llm"]["llm"]]
        self._insert_into(table_name="Commentary", columns=columns, values=values)

    def fetch_fixture_ids(self, date):
        with self.wrapper as db:
            db.cursor.execute(self.queries["fixture_ids"], (date + "%",))
            return [row[0] for row in db.cursor.fetchall()]

    def fetch_data(self, fetch_query, fixture_id):
        with self.wrapper as db:
            db.cursor.execute(fetch_query, (fixture_id,))
            return [dict(row) for row in db.cursor.fetchall()]

    def fetch_match_data(self, fixture_id):
        events = self.fetch_data(self.queries['events_data'], fixture_id)
        stats = self.fetch_data(self.queries["stats_data"], fixture_id)
        return {"fixture": fixture_id, "events": events, "stats": stats}

    def fetch_email_data(self, fixture_id):
        return {"score": self.fetch_data(self.queries['email_data_teams'], fixture_id),
                "comment": self.fetch_data(self.queries['email_data_text'], fixture_id)}


if __name__ == "__main__":
    log.setLevel("DEBUG")
    db_ops = SQLiteOperations(db_name="football_matches.db")
    # db_ops.execute_sql_script("create_tables.sql")

    date = "..."
    fixture_ids = db_ops.fetch_fixture_ids(date)
    matches = []
    for id_ in fixture_ids:
        matches.append(db_ops.fetch_match_data(id_))
