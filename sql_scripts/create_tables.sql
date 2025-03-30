CREATE TABLE IF NOT EXISTS Fixture (
    fixture_id INTEGER PRIMARY KEY,
    date TEXT,
    referee TEXT,
    timestamp INTEGER,
    timezone TEXT,
    elapsed_mins INTEGER,
    extra_mins INTEGER,
    status TEXT,
    league TEXT,
    season INTEGER
);

CREATE TABLE IF NOT EXISTS Teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fixture_id INTEGER,
    team_type STRING, -- home/away
    team_id STRING,
    logo STRING,
    name STRING,
    winner BOOLEAN,
    goals INTEGER
);

CREATE TABLE Score (
    score_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fixture_id INTEGER,
    score_type TEXT,  -- 'fulltime', 'halftime', 'extratime', 'penalty'
    team_id INTEGER,  -- Foreign key to the team (home/away)
    score_value INTEGER,  -- The score (e.g., 1, 2, 3, etc.)
    FOREIGN KEY (fixture_id) REFERENCES Fixture(fixture_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES Team(team_id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fixture_id INTEGER,
    assist TEXT,
    comments TEXT,
    detail TEXT,
    player TEXT,
    team_id INTEGER,
    time INTEGER,
    type TEXT,
    FOREIGN KEY (fixture_id) REFERENCES Fixture(fixture_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fixture_id INTEGER,
    team_id INTEGER,
    type TEXT,
    value TEXT,
    FOREIGN KEY (fixture_id) REFERENCES Fixture(fixture_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Commentary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fixture_id INTEGER,
    text TEXT,
    llm TEXT,
    -- prompt_id TEXT
    FOREIGN KEY (fixture_id) REFERENCES Fixture(fixture_id) ON DELETE CASCADE
);
-- also create a table for a prompt to keep track of which prompt belongs to which comment

