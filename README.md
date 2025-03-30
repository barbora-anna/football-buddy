# FootballBuddy

## Overview
FootballBuddy is a Python application that retrieves previous day's football match fixtures using 
the RapidAPI service. The program enriches match data using OpenAI's LLM, stores it in a SQLite database, 
identifies interesting events, and sends automated email updates based on detected triggers.

## Features

- Fetches football match data from RapidAPI.
- Enriches data with AI-generated insights.
- Stores match details in an SQLite database.
- Detects interesting events using an AI model.
- Sends automated email notifications for relevant matches.

## Installation
### Prerequisites
Ensure you have **Python 3.8+** and **pip** 

Install dependencies:
```
pip install -r requirements.txt
```

## Configuration
The following env variables are required: 
```
OPENAI_API_KEY
RAPID_APIKEY            
EMAIL_SENDER_PASSWORD
```

The project also contains a config file with the following structure:
```
data_config:
  team:
    league:                     # The league to receive info about
    team:                       # The main team of interest
    season:                     # The season to observe
    country_code:               # Two-letter country code (see RapidAPI docs for details)
  db_name:                      # Database to store data in

rapid_api:
  base_url:                     # Base url for RapidAPI requests
  host:                         # RapidAPI host

email_service:
  participants_meta:            
    sender:             
      email:                    # Email address to send mail from
    receiver:
      email:                    # The receiver of the email -- will be scaled in the upcoming versions of the program
  email_params:
    subject:                    # The subject of the email
  smtp:
    host:                       # SMTP host
    port:                       # SMTP port (for both see Seznam docs)
```
## Running the project
Run the project using **main.py**.
The script will:
- Retrieve matches data.
- Enhance it with AI insights.
- Store it in a local database.
- Detect interesting match events.
- Generate and send an email summary.

## File structure
```
/football-buddy 
│── json_schemas           # Schemas for json structure validation
    │── llm_answer.json 
    │── rapid_data.json
│── sql_scripts
    │── create_tables.sql  # SQL for table creation
│── data_retriever.py      # Fetches matches fixtures from Rapid API 
│── llm_operations.py      # Handles LLM-related operations and calls to OpenAI
│── db_operations.py       # Stores and processes match data in SQLite 
│── main.py                # Runs the whole process 
│── requirements.txt       # Required Python libraries 
│── send_email.py          # Handles email formatting and sending
│── config.yaml            # Project configuration
│── prompts.yaml           # Structured file with prompts and LLM metadata
│── README.md              # Documentation 
```
