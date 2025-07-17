# Random LeetCode to Teams Script

This script fetches a random, non-premium LeetCode problem and posts it as an Adaptive Card to a Microsoft Teams channel, ensuring each question is unique until the list resets.

Note: It is possible to modify the webhook URL and body to send messages to other platforms, but this script is specifically designed for Microsoft Teams (Power Automate - Adaptive Cards).

## Features

* Fetches the full list of LeetCode problems via the public API
* Skips paid-only (premium) questions
* Tracks asked question IDs in `asked_questions.json` to avoid repeats
* Resets history when all non-premium questions have been used
* Sends an additional SQL question every day
* Tracks asked SQL question IDs in `asked_sql_questions.json`
* Reads `teams_webhook_url`, `sql_teams_webhook_url`, and `admin_token` from `config.json`
* Provides a simple leaderboard utility to track user progress
* Posts Adaptive Cards with a clickable **View on LeetCode** button

## Prerequisites

* Python 3.6+
* A Microsoft Teams Incoming Webhook URL (create under **Connectors** in your Teams channel)

## Repository Structure

```
.
├── daily.py                  # Main script
├── leaderboard.py            # Simple leaderboard utility
├── web_leaderboard.py        # Optional Flask web app for registration
├── config.json               # Stores your Teams webhook URLs and admin token
├── asked_questions.json      # Generated: tracks asked code question IDs
├── asked_sql_questions.json  # Generated: tracks asked SQL question IDs
├── leaderboard_users.json    # Generated: tracked usernames
└── leaderboard_scores.json   # Generated: daily scores
```

## Configuration

Create a `config.json` file in the same directory:

```json
{
  "teams_webhook_url": "<your_webhook_url>",
  "sql_teams_webhook_url": "<your_sql_webhook_url>",
  "admin_token": "<admin_token>"
}
```

## Installation

1. Clone or download this repository.
2. Install dependencies:

   ```bash
   pip install requests
   ```

## Usage

Run the script manually:

```bash
python3 daily.py
```

To schedule daily delivery, add a cron job (Linux/macOS) or Task Scheduler (Windows):

```cron
# Every weekday at 9:00 AM:
0 9 * * 1-5 /usr/bin/env python3 /path/to/daily.py
```

# Deployment

This script can be deployed on any machine with Docker installed. The Dockerfile provided in this repository allows you to build a Docker image that contains all the necessary dependencies and configurations to run the script.

Note: This repository was quickly created and does not follow all best practices around security, such as keeping secrets out of the docker image build.

```sh
# Build the Docker image
docker build -t daily-code-question .

# Run the Docker container
docker run -d --name daily-code-question daily-code-question
```

## Leaderboard

Use `leaderboard.py` or the optional web server to track user progress.
Run a small Flask app for one-time registration:

```bash
pip install flask
python3 web_leaderboard.py
```

Then visit `http://localhost:8000/` to submit your LeetCode username.
View the current scores at `http://localhost:8000/scores`.

You can also manage users via `leaderboard.py` with the admin token:

```bash
python3 leaderboard.py add <leetcode_username> <admin_token>
```

Show the current rankings:

```bash
python3 leaderboard.py list
```

## Behavior

* On each run, the script:

  1. Loads `config.json` for the webhook URLs
  2. Fetches coding problems from the algorithms problem set and SQL problems from the database set
  3. Filters out premium questions
  4. Selects a random unasked coding problem
  5. Posts an Adaptive Card to the coding channel
  6. Selects a random unasked SQL problem
  7. Posts an Adaptive Card to the SQL channel
  8. Appends the question IDs to the appropriate history files
  9. Refreshes leaderboard scores each day

* When all non-premium problems have been asked, the history resets and questions become available again.

## Troubleshooting

* **Invalid JSON**: Ensure `config.json` is valid JSON and contains `teams_webhook_url`, `sql_teams_webhook_url`, and `admin_token`.
* **Network errors**: Confirm your machine has internet access and the Teams URL is reachable.
* **Permissions errors**: Verify your webhook URL is correct and has not been revoked.

## Customization

* **Filter difficulty**: Modify `pick_random_problem()` to include filtering by `choice['difficulty']['level']` if desired.
* **Alternate formats**: Adjust the Adaptive Card payload in `send_teams_message()` to change styling or add additional fields.
