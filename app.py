from flask import Flask, render_template, request, redirect, url_for
import json
import random
import os
import time

app = Flask(__name__)

DATA_FILE = "data/results.json"

# ------------------

# Helpers

# ------------------

def load_data():
    if not os.path.exists(DATA_FILE):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        save_data({})
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_user(username, max_table=9):
    data = load_data()
    if username not in data:
        data[username] = {
        "total_correct": 0,
        "table_stats": {str(i): 0 for i in range(2, max_table + 1)},
        "times": []
        }
    save_data(data)

def delete_user(username):
    data = load_data()
    if username in data:
        del data[username]
    save_data(data)

def edit_user(username, new_settings):
    data = load_data()
    if username in data:
        data[username].update(new_settings)
    save_data(data)

# ------------------

# Routes

# ------------------

@app.route("/")
def index():
    data = load_data()
    return render_template("index.html", users=data.keys())

@app.route("/dashboard/<user>")
def dashboard(user):
    data = load_data()
    if user not in data:
        return redirect(url_for("index"))
    return render_template("dashboard.html", user=user, results=data[user])

@app.route("/practice/<user>")
def practice(user):
    data = load_data()
    if user not in data:
        return redirect(url_for("index"))

#```
    problems = []

    # Anpassning per användare (max_table per user)
    max_table = max(int(k) for k in data[user]["table_stats"].keys())
    num_problems = 10 if max_table <= 6 else 20

    for _ in range(num_problems):
        a = random.randint(2, max_table)
        b = random.randint(2, max_table)
        problems.append((a, b))

        start_time = time.time()
    return render_template("practice.html", user=user, problems=problems, start_time=start_time)
#```

@app.route("/submit/<user>", methods=["POST"])
def submit(user):
    answers = request.form
    data = load_data()
    if user not in data:
        return redirect(url_for("index"))

 #   ```
    total_correct = 0
    start_time_str = answers.get("start_time")
    try:
        start_time = float(start_time_str)
    except (TypeError, ValueError):
        start_time = time.time()

    end_time = time.time()
    total_time = round(end_time - start_time, 2)

    for key in answers:
        if key == "start_time":
            continue
        a, b = key.split("x")
        correct = int(a) * int(b)
        user_answer = int(answers[key])
        if user_answer == correct:
            total_correct += 1
            data[user]["table_stats"][a] += 1

    data[user]["total_correct"] += total_correct
    data[user].setdefault("times", []).append(total_time)

    save_data(data)
    return redirect(url_for("dashboard", user=user))
#```

@app.route("/summary/<user>")
def summary(user):
    data = load_data()
    if user not in data:
        return redirect(url_for("index"))
    stats = data[user]["table_stats"]
    sorted_tables = sorted(stats.items(), key=lambda item: item[1])
    return render_template("summary.html", user=user, stats=sorted_tables)

# ------------------

# Admin page

# ------------------

@app.route("/admin", methods=["GET", "POST"])
def admin():
    data = load_data()

#```
    if request.method == "POST":
        action = request.form.get("action")
        username = request.form.get("username")

        if action == "add":
            max_table = int(request.form.get("max_table", 9))
            add_user(username, max_table)
        elif action == "delete":
            delete_user(username)
        elif action == "edit":
            max_table = int(request.form.get("max_table", 9))
            edit_user(username, {"table_stats": {str(i): 0 for i in range(2, max_table + 1)}})

        return redirect(url_for("admin"))

    return render_template("admin.html", users=data)
#```

# ------------------

# Run

# ------------------

if __name__ == "__main__":
    app.run(debug=True)
