# Football Buddy project

## Overview
This project automates custom football reporting. It sources football matches
fixtures, statistics, and events, generates a summary, and sends an email 
in case of a selected football team having played or in case of interesting events. 
Such events can include red cards, injuries, or any anomalies being noted. 

## Project workflow
### Extract
Fetches football match fixtures from Rapid API using data_retriever.py.
### Transform
Sends match data to LangChain-powered LLM to generate a match report (llm_processor.py).
### Load & Prepare
Stores match data in SQLite and performs SQL operations for cleaning and structuring (database.py).
### Analyze & Decide
Runs a second LLM-based analysis on the cleaned data for insights.
### Trigger Notification
Sends an automated email if the LLM finds noteworthy insights.

## Installation

## Project structure
```
/football-buddy 
│── json_schemas           # Schemas for json structure validation
    │── llm_answer.json 
    │── rapid_data.json
│── sql_scripts            # Larger SQL scripts
│── data_retriever.py      # Fetches match fixtures from Rapid API 
│── llm_stuff.py           # Generates match descriptions 
│── database.py            # Stores and processes match data in SQLite 
│── pipeline.py            # Runs the whole process 
│── email_notifier.py      # Sends email alerts 
│── requirements.txt       # Required Python libraries 
│── README.md              # Documentation 
```

