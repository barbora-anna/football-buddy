import sqlite3

# connector = sqlite3.connect("football_matches.db")
# c = con.cursor()
#
# c.execute(
#     '''
#     CREATE TABLE IF NOT EXISTS about_match
#     (
#         [id] INTEGER PRIMARY KEY,
#         [name] TEXT,
#         [stuff] TEXT
#     )
#     '''
# )
#
# connector.commit()


def get_keys():
    ...

class TableLoader:
    def __init__(self, db_name):
        self.db = db_name

    def flatten_dict(self, nested_dict, parent_key='', sep='_'):
        items = []
        for k, v in nested_dict.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)








