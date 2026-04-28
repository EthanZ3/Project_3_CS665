from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = "dev-secret-key"


@app.route("/")
def dashboard():
    stats = {
        "total_guests": 0,
        "total_rooms": 0,
        "total_reservations": 0,
        "total_revenue": 0,
    }

    room_status_summary = []
    recent_reservations = []

    return render_template(
        "dashboard.html",
        title="Dashboard",
        stats=stats,
        room_status_summary=room_status_summary,
        recent_reservations=recent_reservations
    )


@app.route("/guests")
def list_guests():
    return "Guests page coming soon"


@app.route("/rooms")
def list_rooms():
    return "Rooms page coming soon"


@app.route("/reservations")
def list_reservations():
    return "Reservations page coming soon"


if __name__ == "__main__":
    app.run(debug=True)