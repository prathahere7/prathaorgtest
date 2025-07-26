from flask import Flask, request, render_template_string
import sqlite3
import subprocess
import requests

app = Flask(__name__)

# --- Init DB ---
def init_db():
    conn = sqlite3.connect('ssrf_rce_sqli.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

# --- Home Page ---
@app.route('/')
def index():
    return '''
        <h2>Vulnerable Flask App</h2>
        <ul>
            <li><a href="/register">Register (SQLi)</a></li>
            <li><a href="/fetch-url?url=http://example.com">Fetch URL (SSRF)</a></li>
            <li><a href="/exec">Execute Command (RCE)</a></li>
        </ul>
    '''

# --- SQL Injection ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('ssrf_rce_sqli.db')
        cur = conn.cursor()
        # SQL Injection
        query = f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')"
        cur.execute(query)
        conn.commit()
        conn.close()

        return "User registered"
    
    return '''
        <h3>Register</h3>
        <form method="POST">
            Username: <input name="username"><br>
            Password: <input name="password"><br>
            <input type="submit" value="Submit">
        </form>
    '''

# --- SSRF (Server-Side Request Forgery) ---
@app.route('/fetch-url')
def fetch_url():
    target_url = request.args.get('url')
    try:
        # SSRF vulnerability - unvalidated user-controlled URL
        r = requests.get(target_url, timeout=5)
        return f"<pre>{r.text}</pre>"
    except Exception as e:
        return f"<pre>Failed to fetch URL: {e}</pre>"

# --- Remote Code Execution ---
@app.route('/exec', methods=['GET', 'POST'])
def exec_cmd():
    if request.method == 'POST':
        cmd = request.form.get('cmd')
        try:
            # RCE vulnerability
            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5)
            return f"<pre>{result.decode()}</pre>"
        except Exception as e:
            return f"<pre>
