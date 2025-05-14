# Random LeetCode to Teams Script

This script fetches a random, non-premium LeetCode problem and posts it as an Adaptive Card to a Microsoft Teams channel, ensuring each question is unique until the list resets.

Note: It is possible to modify the webhook URL and body to send messages to other platforms, but this script is specifically designed for Microsoft Teams (Power Automate - Adaptive Cards).

## Features

* Fetches the full list of LeetCode problems via the public API
* Skips paid-only (premium) questions
* Tracks asked question IDs in `asked_questions.json` to avoid repeats
* Resets history when all non-premium questions have been used
* Reads Microsoft Teams webhook URL from `config.json`
* Posts an Adaptive Card with a clickable **View on LeetCode** button

## Prerequisites

* Python 3.6+
* A Microsoft Teams Incoming Webhook URL (create under **Connectors** in your Teams channel)

## Repository Structure

```
.
├── daily.py                  # Main script
├── config.json               # Stores your Teams webhook URL
└── asked_questions.json      # Generated: tracks asked question IDs
```

## Configuration

Create a `config.json` file in the same directory:

```json
{
  "teams_webhook_url": "<your_webhook_url>"
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

## Behavior

* On each run, the script:

  1. Loads `config.json` for the webhook URL
  2. Fetches problems from the LeetCode API
  3. Filters out premium questions
  4. Selects a random unasked problem
  5. Posts an Adaptive Card to Teams
  6. Appends the question ID to `asked_questions.json`

* When all non-premium problems have been asked, the history resets and questions become available again.

## Troubleshooting

* **Invalid JSON**: Ensure `config.json` is valid JSON and contains `teams_webhook_url`.
* **Network errors**: Confirm your machine has internet access and the Teams URL is reachable.
* **Permissions errors**: Verify your webhook URL is correct and has not been revoked.

## Customization

* **Filter difficulty**: Modify `pick_random_problem()` to include filtering by `choice['difficulty']['level']` if desired.
* **Alternate formats**: Adjust the Adaptive Card payload in `send_teams_message()` to change styling or add additional fields.
