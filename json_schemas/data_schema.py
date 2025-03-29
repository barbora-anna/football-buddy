{
  "type": "object",
  "properties": {
    "about": {
      "type": "object",
      "properties": {
        "fixture": {
          "type": "object",
          "properties": {
            "date": { "type": "string" },
            "periods": {
              "type": "object",
              "properties": {
                "first": { "type": "integer" },
                "second": { "type": "integer" }
              },
              "required": ["first", "second"]
            },
            "referee": { "type": "string" },
            "status": {
              "type": "object",
              "properties": {
                "elapsed": { "type": "integer" },
                "extra": { "type": "integer" },
                "long": { "type": "string" },
                "short": { "type": "string" }
              },
              "required": ["elapsed", "extra", "long", "short"]
            },
            "timestamp": { "type": "integer" },
            "timezone": { "type": "string" },
            "venue": {
              "type": "object",
              "properties": {
                "city": { "type": "string" },
                "id": { "type": "integer" },
                "name": { "type": "string" }
              },
              "required": ["city", "id", "name"]
            }
          },
          "required": [
            "date", "periods", "referee", "status",
            "timestamp", "timezone", "venue"
          ]
        },
        "goals": {
          "type": "object",
          "properties": {
            "away": { "type": "integer" },
            "home": { "type": "integer" }
          },
          "required": ["away", "home"]
        },
        "league": {
          "type": "object",
          "properties": {
            "country": { "type": "string" },
            "flag": { "type": "string" },
            "id": { "type": "integer" },
            "logo": { "type": "string" },
            "name": { "type": "string" },
            "round": { "type": "string" },
            "season": { "type": "integer" },
            "standings": { "type": "boolean" }
          },
          "required": [
            "country", "flag", "id", "logo",
            "name", "round", "season", "standings"
          ]
        },
        "score": {
          "type": "object",
          "properties": {
            "extratime": {
              "type": "object",
              "properties": {
                "away": { "type": ["integer", "null"] },
                "home": { "type": ["integer", "null"] }
              }
            },
            "fulltime": {
              "type": "object",
              "properties": {
                "away": { "type": "integer" },
                "home": { "type": "integer" }
              },
              "required": ["away", "home"]
            },
            "halftime": {
              "type": "object",
              "properties": {
                "away": { "type": "integer" },
                "home": { "type": "integer" }
              },
              "required": ["away", "home"]
            },
            "penalty": {
              "type": "object",
              "properties": {
                "away": { "type": ["integer", "null"] },
                "home": { "type": ["integer", "null"] }
              }
            }
          },
          "required": ["extratime", "fulltime", "halftime", "penalty"]
        },
        "teams": {
          "type": "object",
          "properties": {
            "away": {
              "type": "object",
              "properties": {
                "id": { "type": "integer" },
                "logo": { "type": "string" },
                "name": { "type": "string" },
                "winner": { "type": "boolean" }
              },
              "required": ["id", "logo", "name", "winner"]
            },
            "home": {
              "type": "object",
              "properties": {
                "id": { "type": "integer" },
                "logo": { "type": "string" },
                "name": { "type": "string" },
                "winner": { "type": "boolean" }
              },
              "required": ["id", "logo", "name", "winner"]
            }
          },
          "required": ["away", "home"]
        }
      },
      "required": ["fixture", "goals", "league", "score", "teams"]
    },
    "events": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "assist": {
            "type": "object",
            "properties": {
              "id": { "type": ["integer", "null"] },
              "name": { "type": ["string", "null"] }
            }
          },
          "comments": { "type": ["string", "null"] },
          "detail": { "type": "string" },
          "player": {
            "type": "object",
            "properties": {
              "id": { "type": "integer" },
              "name": { "type": "string" }
            },
            "required": ["id", "name"]
          },
          "team": {
            "type": "object",
            "properties": {
              "id": { "type": "integer" },
              "logo": { "type": "string" },
              "name": { "type": "string" }
            },
            "required": ["id", "logo", "name"]
          },
          "time": {
            "type": "object",
            "properties": {
              "elapsed": { "type": "integer" },
              "extra": { "type": ["integer", "null"] }
            }
          },
          "type": { "type": "string" }
        },
        "required": [
          "assist", "comments", "detail", "player", "team", "time", "type"
        ]
      }
    },
    "fixture_id": { "type": "integer" },
    "stats": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "statistics": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "type": { "type": "string" },
                "value": { "type": ["integer", "string", "null"] }
              },
              "required": ["type", "value"]
            }
          },
          "team": {
            "type": "object",
            "properties": {
              "id": { "type": "integer" },
              "logo": { "type": "string" },
              "name": { "type": "string" }
            },
            "required": ["id", "logo", "name"]
          }
        },
        "required": ["statistics", "team"]
      }
    }
  },
  "required": ["about", "events", "fixture_id", "stats"]
}


llm_answer_schema = {
    "type": "object",
    "properties": {
        "answer": {"enum": ["yes", "no"]},
        "reason": {"type": ["string", "null"]}
    },
    "required": ["answer", "reason"]
}
