#!/usr/bin/env python3
'''
This script fetches a random LeetCode problem and sends it as a Microsoft Teams message via an incoming webhook, ensuring uniqueness by tracking asked question IDs, skipping premium problems, and loading configuration from a JSON file.
It formats the payload according to the Teams webhook schema using an Adaptive Card with a clickable button.

Usage:
    1. Create an Incoming Webhook in your Microsoft Teams channel and copy its URL.
    2. In the same directory as this script, create a file named `config.json` with the following content:
       {
           "teams_webhook_url": "<your_webhook_url>"
       }
    3. Install dependencies:
       pip install requests
    4. Run the script:
       python3 random_leetcode_teams.py
'''

import os
import sys
import requests
import random
import json

ASKED_FILE = 'asked_questions.json'
CONFIG_FILE = 'config.json'


def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: Configuration file '{CONFIG_FILE}' not found.", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_FILE, 'r') as f:
        try:
            cfg = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Configuration file '{CONFIG_FILE}' is not valid JSON.", file=sys.stderr)
            sys.exit(1)
    url = cfg.get('teams_webhook_url')
    if not url:
        print(f"Error: 'teams_webhook_url' not set in '{CONFIG_FILE}'.", file=sys.stderr)
        sys.exit(1)
    return url


def load_asked():
    if os.path.exists(ASKED_FILE):
        with open(ASKED_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_asked(asked):
    with open(ASKED_FILE, 'w') as f:
        json.dump(asked, f)


def fetch_problems():
    '''Fetches all LeetCode problems via the public API endpoint.'''
    url = 'https://leetcode.com/api/problems/all/'
    headers = {'User-Agent': 'RandomLeetCodeTeamsScript/1.0'}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get('stat_status_pairs', [])


def pick_random_problem(problems, asked):
    '''Selects a random non-premium problem, avoiding repeats.'''
    non_premium = [p for p in problems if not p.get('paid_only', False)]
    if not non_premium:
        raise ValueError('No non-premium problems available.')

    unasked = [p for p in non_premium if p['stat']['frontend_question_id'] not in asked]
    if not unasked:
        asked.clear()
        unasked = non_premium

    choice = random.choice(unasked)
    stat = choice['stat']
    qid = stat['frontend_question_id']
    title = stat['question__title']
    slug = stat['question__title_slug']
    difficulty_map = {1: 'Easy', 2: 'Medium', 3: 'Hard'}
    diff = difficulty_map.get(choice['difficulty']['level'], 'Unknown')
    link = f'https://leetcode.com/problems/{slug}/'
    return qid, title, diff, link


def send_teams_message(webhook_url, qid, title, difficulty, link, num_asked):
    '''Sends an Adaptive Card formatted payload to Teams with a clickable button.'''
    payload = {
        "type": "object",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.2",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": f"Daily Code Question (Day #{num_asked}) \nLeetCode #{qid}: {title} ({difficulty})",
                            "wrap": True,
                            "weight": "Bolder",
                            "size": "Medium"
                        }
                    ],
                    "actions": [
                        {
                            "type": "Action.OpenUrl",
                            "title": "View on LeetCode",
                            "url": link
                        }
                    ]
                }
            }
        ]
    }
    resp = requests.post(webhook_url, json=payload, timeout=10)
    resp.raise_for_status()


def main():
    webhook_url = load_config()
    problems = fetch_problems()
    asked = load_asked()
    qid, title, difficulty, link = pick_random_problem(problems, asked)
    asked.append(qid)
    save_asked(asked)
    count = len(asked)

    send_teams_message(webhook_url, qid, title, difficulty, link, count)
    print(f"Sent question #{qid} ({title}) to Microsoft Teams.")


if __name__ == '__main__':
    main()
