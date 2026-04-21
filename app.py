from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from db import init_db
import datetime

app = Flask(__name__)
init_db()

def db():
    return sqlite3.connect("quickdrop.db")

# ---------------- HOME ----------------
@app.route("/")
def index():
    conn = db()
    data = conn.execute("SELECT * FROM deliveries").fetchall()
    conn.close()
    return render_template("index.html", deliveries=data)

# ---------------- CREATE ----------------
@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        conn = db()
        conn.execute("""
        INSERT INTO deliveries (client, pickup, destination, price, status)
        VALUES (?, ?, ?, ?, ?)
        """, (
            request.form["client"],
            request.form["pickup"],
            request.form["destination"],
            request.form["price"],
            "pending"
        ))
        conn.commit()
        conn.close()
        return redirect("/")
    return render_template("create.html")

# ---------------- ACCEPT ----------------
@app.route("/accept/<int:id>")
def accept(id):
    conn = db()
    conn.execute("UPDATE deliveries SET status='accepted' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

# ---------------- DELIVERED ----------------
@app.route("/deliver/<int:id>")
def deliver(id):
    conn = db()
    conn.execute("UPDATE deliveries SET status='delivered' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

# ---------------- DRIVER GPS ----------------
@app.route("/driver/<int:id>")
def driver(id):
    return render_template("driver.html", delivery_id=id)

@app.route("/update_location/<int:id>", methods=["POST"])
def update_location(id):
    data = request.json

    conn = db()
    conn.execute("""
    INSERT INTO tracking (delivery_id, lat, lng, updated_at)
    VALUES (?, ?, ?, ?)
    """, (id, data["lat"], data["lng"], str(datetime.datetime.now())))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

# ---------------- LIVE LOCATION ----------------
@app.route("/last_location/<int:id>")
def last_location(id):
    conn = db()
    data = conn.execute("""
    SELECT lat, lng FROM tracking
    WHERE delivery_id=?
    ORDER BY id DESC LIMIT 1
    """, (id,)).fetchone()
    conn.close()

    if data:
        return jsonify({"lat": data[0], "lng": data[1]})
    return jsonify({"lat": None, "lng": None})

# ---------------- MAP ----------------
@app.route("/map/<int:id>")
def map_view(id):
    return render_template("map.html", delivery_id=id)

# ---------------- PAYMENT (NIAMEY MOBILE MONEY) ----------------
@app.route("/pay/<int:id>", methods=["GET", "POST"])
def pay(id):
    if request.method == "POST":
        conn = db()
        conn.execute("""
        INSERT INTO payments (delivery_id, method, amount, txid, status)
        VALUES (?, ?, ?, ?, ?)
        """, (
            id,
            request.form["method"],
            request.form["amount"],
            request.form["txid"],
            "pending"
        ))
        conn.commit()
        conn.close()
        return redirect("/")

    return render_template("pay.html", delivery_id=id)

# ---------------- CONFIRM PAYMENT ----------------
@app.route("/confirm_payment/<int:id>")
def confirm_payment(id):
    conn = db()
    conn.execute("UPDATE payments SET status='confirmed' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

# ---------------- RUN ----------------
app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
