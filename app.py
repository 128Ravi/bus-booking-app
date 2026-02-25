from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bus.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ===============================
# Database Models
# ===============================

class Bus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    from_city = db.Column(db.String(100), nullable=False)
    to_city = db.Column(db.String(100), nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, nullable=False)
    passenger_name = db.Column(db.String(100), nullable=False)
    travel_date = db.Column(db.String(50), nullable=False)
    seats = db.Column(db.String(200), nullable=False)
    amount_paid = db.Column(db.Integer, nullable=False)


# ===============================
# Initialize Database
# ===============================

with app.app_context():
    db.create_all()

    # Insert sample buses if empty
    if not Bus.query.first():
        sample_buses = [
            Bus(name="Green Express", from_city="Chennai", to_city="Bangalore",
                total_seats=40, available_seats=40, price=750),
            Bus(name="Night Rider", from_city="Chennai", to_city="Hyderabad",
                total_seats=36, available_seats=36, price=1200),
            Bus(name="Super Deluxe", from_city="Bangalore", to_city="Chennai",
                total_seats=40, available_seats=40, price=800)
        ]
        db.session.add_all(sample_buses)
        db.session.commit()


# ===============================
# Routes
# ===============================

@app.route("/")
def home():
    return render_template("index.html")


# Search Buses
@app.route("/search", methods=["POST"])
def search():
    from_city = request.form.get("from")
    to_city = request.form.get("to")
    travel_date = request.form.get("date")

    buses = Bus.query.filter_by(
        from_city=from_city,
        to_city=to_city
    ).all()

    return render_template("results.html", buses=buses, date=travel_date)


# Seat Selection Page
@app.route("/select/<int:bus_id>/<date>")
def select_seat(bus_id, date):
    bus = Bus.query.get_or_404(bus_id)
    return render_template("seat_select.html", bus=bus, date=date)


# Move to Payment Page
@app.route("/confirm/<int:bus_id>", methods=["POST"])
def confirm(bus_id):
    bus = Bus.query.get_or_404(bus_id)

    passenger_name = request.form.get("name")
    travel_date = request.form.get("date")
    selected_seats = request.form.getlist("seats")

    if not selected_seats:
        return "Please select at least one seat."

    total_amount = len(selected_seats) * bus.price

    # Store booking temporarily in session
    session["booking_data"] = {
        "bus_id": bus.id,
        "passenger_name": passenger_name,
        "travel_date": travel_date,
        "seats": selected_seats,
        "amount": total_amount
    }

    return render_template(
        "payment.html",
        name=passenger_name,
        seats=selected_seats,
        amount=total_amount,
        bus=bus
    )


# Process Payment (Simulation)
@app.route("/process_payment", methods=["POST"])
def process_payment():
    booking_data = session.get("booking_data")

    if not booking_data:
        return redirect(url_for("home"))

    bus = Bus.query.get_or_404(booking_data["bus_id"])

    # Check seat availability
    if bus.available_seats < len(booking_data["seats"]):
        return "Not enough seats available!"

    # Save booking
    new_booking = Booking(
        bus_id=booking_data["bus_id"],
        passenger_name=booking_data["passenger_name"],
        travel_date=booking_data["travel_date"],
        seats=",".join(booking_data["seats"]),
        amount_paid=booking_data["amount"]
    )

    bus.available_seats -= len(booking_data["seats"])

    db.session.add(new_booking)
    db.session.commit()

    # Clear session
    session.pop("booking_data", None)

    return render_template(
        "confirmation.html",
        name=new_booking.passenger_name,
        seats=new_booking.seats.split(","),
        amount=new_booking.amount_paid
    )


# ===============================
# Run Application
# ===============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)