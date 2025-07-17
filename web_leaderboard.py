import os
import json
from flask import Flask, request, redirect, render_template_string
import leaderboard

app = Flask(__name__)

DATA_DIR = os.getenv('DATA_DIR', '/data')

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            leaderboard.register_user(username)
        return redirect('/')
    users = leaderboard.load_users()
    html = '''
    <h1>Leaderboard Registration</h1>
    <form method="post">
      <input type="text" name="username" placeholder="LeetCode Username" required>
      <button type="submit">Register</button>
    </form>
    <h2>Current Users</h2>
    <ul>{% for user in users %}<li>{{ user }}</li>{% endfor %}</ul>
    '''
    return render_template_string(html, users=users)

@app.route('/scores')
def scores():
    data = leaderboard.load_scores()
    html = '''
    <h1>Leaderboard</h1>
    <ul>{% for entry in data %}<li>{{ loop.index }}. {{ entry['user'] }}: {{ entry['score'] }}</li>{% endfor %}</ul>
    '''
    return render_template_string(html, data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '8000')))
