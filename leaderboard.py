import os
import sys
import json
import requests

DATA_DIR = os.getenv('DATA_DIR', '/data')
USERS_FILE = os.path.join(DATA_DIR, 'leaderboard_users.json')
SCORES_FILE = os.path.join(DATA_DIR, 'leaderboard_scores.json')
ASKED_FILE = os.path.join(DATA_DIR, 'asked_questions.json')
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')

GRAPHQL_ENDPOINT = 'https://leetcode.com/graphql'


def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: Configuration file '{CONFIG_FILE}' not found.", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_FILE, 'r') as f:
        cfg = json.load(f)
    token = cfg.get('admin_token')
    if not token:
        print("Error: 'admin_token' missing in config.", file=sys.stderr)
        sys.exit(1)
    return token


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)


def load_asked():
    if os.path.exists(ASKED_FILE):
        with open(ASKED_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def fetch_problem_map():
    url = 'https://leetcode.com/api/problems/algorithms/'
    resp = requests.get(url, headers={'User-Agent': 'LeaderboardScript/1.0'}, timeout=10)
    resp.raise_for_status()
    data = resp.json().get('stat_status_pairs', [])
    return {p['stat']['question__title_slug']: p['stat']['frontend_question_id'] for p in data}


def fetch_user_solved(username, limit=1000):
    query = {
        "query": "query recentAcSubmissions($username: String!, $limit: Int!) { recentAcSubmissionList(username: $username, limit: $limit) { title slug } }",
        "variables": {"username": username, "limit": limit},
        "operationName": "recentAcSubmissions"
    }
    resp = requests.post(GRAPHQL_ENDPOINT, json=query, headers={'User-Agent': 'LeaderboardScript/1.0'}, timeout=10)
    resp.raise_for_status()
    result = resp.json()
    submissions = result.get('data', {}).get('recentAcSubmissionList', [])
    return [s['slug'] for s in submissions]


def calc_scores(users):
    asked = set(load_asked())
    problem_map = fetch_problem_map()
    scores = []
    for user in users:
        slugs = fetch_user_solved(user)
        solved_ids = {problem_map.get(slug) for slug in slugs if slug in problem_map}
        score = len([qid for qid in asked if qid in solved_ids])
        scores.append((user, score))
    return sorted(scores, key=lambda x: x[1], reverse=True)


def update_scores():
    scores = calc_scores(load_users())
    data = [{"user": u, "score": s} for u, s in scores]
    with open(SCORES_FILE, 'w') as f:
        json.dump(data, f)
    return data


def load_scores():
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def add_user(username, token, expected):
    if token != expected:
        print('Invalid admin token.', file=sys.stderr)
        sys.exit(1)
    register_user(username)


def register_user(username):
    users = load_users()
    if username not in users:
        users.append(username)
        save_users(users)
        print(f"Registered '{username}' to leaderboard.")
    else:
        print(f"'{username}' is already tracked.")


def main(argv):
    expected_token = load_config()
    if len(argv) < 2:
        print('Usage: leaderboard.py [add USER TOKEN | register USER | update | list]')
        return
    if argv[1] == 'add' and len(argv) == 4:
        _, _, user, token = argv
        add_user(user, token, expected_token)
    elif argv[1] == 'register' and len(argv) == 3:
        _, _, user = argv
        register_user(user)
    elif argv[1] == 'update':
        data = update_scores()
        for rank, entry in enumerate(data, 1):
            print(f"{rank}. {entry['user']}: {entry['score']}")
    elif argv[1] == 'list':
        scores = load_scores()
        if not scores:
            scores = update_scores()
        for rank, entry in enumerate(scores, 1):
            print(f"{rank}. {entry['user']}: {entry['score']}")
    else:
        print('Invalid command.')


if __name__ == '__main__':
    main(sys.argv)
