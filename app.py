from flask import Flask, render_template, request, redirect, url_for
import json, random, os, time

app = Flask(__name__)

DATA_FILE = "data/results.json"

# ------------------
# Helpers
# ------------------
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ------------------
# Routes
# ------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard/<user>")
def dashboard(user):
    data = load_data()[user]
    return render_template("dashboard.html", user=user, results=data)

@app.route("/practice/<user>")
def practice(user):
    problems = []

    # Anpassning per användare
    if user == "valter":
        num_problems = 10
        max_table = 6
    elif user == "david":
        num_problems = 10
        max_table= 9
    else:  # lovisa
        num_problems = 20
        max_table = 9

    # Skapa slumpade uppgifter
    for _ in range(num_problems):
        a = random.randint(2, max_table)
        b = random.randint(2, max_table)
        problems.append((a, b))

    # Starttid
    start_time = time.time()

    return render_template("practice.html", user=user, problems=problems, start_time=start_time)

@app.route("/submit/<user>", methods=["POST"])
def submit(user):
    answers = request.form
    data = load_data()

    total_correct = 0

    # Hämta starttid från formuläret med fallback
    start_time_str = answers.get("start_time")
    try:
        start_time = float(start_time_str)
    except (TypeError, ValueError):
        start_time = time.time()

    end_time = time.time()
    total_time = round(end_time - start_time, 2)  # sekunder

    # Räkna poäng och uppdatera tabellstatistik
    for key in answers:
        if key == "start_time":
            continue
        a, b = key.split("x")
        correct = int(a) * int(b)
        user_answer = int(answers[key])
        if user_answer == correct:
            total_correct += 1
            data[user]["table_stats"][a] += 1

    # Uppdatera totalscore och logga tid
    data[user]["total_correct"] += total_correct
    if "times" not in data[user]:
        data[user]["times"] = []
    data[user]["times"].append(total_time)

    save_data(data)
    return redirect(url_for("dashboard", user=user))

@app.route("/summary/<user>")
def summary(user):
    data = load_data()[user]["table_stats"]
    # Sortera tabeller efter antal rätt (lägst först = behöver öva mer)
    sorted_tables = sorted(data.items(), key=lambda item: item[1])
    return render_template("summary.html", user=user, stats=sorted_tables)

# ------------------
# Run
# ------------------
if __name__ == "__main__":
    # Om JSON-data saknas, skapa initial struktur
    if not os.path.exists(DATA_FILE):
        os.makedirs("data", exist_ok=True)
        initial = {
            "valter": {"total_correct": 0, "table_stats": {str(i): 0 for i in range(2, 7)}, "times": []},
            "lovisa": {"total_correct": 0, "table_stats": {str(i): 0 for i in range(2, 10)}, "times": []},
            "david": {"total_correct": 0, "table_stats": {str(i): 0 for i in range(2, 12)}, "times": []}
        }
        save_data(initial)

    app.run(debug=True)