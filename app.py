import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import os
import re
import traceback
from prometheus_client import Counter, Histogram, generate_latest, make_wsgi_app, CollectorRegistry
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import time
import os
if os.getenv('COVERAGE_RUN') == 'true':
    import coverage
    coverage.process_startup()




# Logging configuration
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback_super_secret_key')

# Mock data
users = {"user": "password"}
products = [{"id": 1, "name": "Laptop", "price": 1000}, {"id": 2, "name": "Phone", "price": 500}]
orders = []

# Prometheus Metrics Setup
registry = CollectorRegistry()
REQUEST_COUNT = Counter(
    'http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'http_status'], registry=registry
)
REQUEST_LATENCY = Histogram(
    'http_request_latency_seconds', 'HTTP Request Latency', ['method', 'endpoint'], registry=registry
)

# SendGrid configuration
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', 'dummy_key')

# Email sending function
def send_email(subject, to_email, body):
    if SENDGRID_API_KEY == 'dummy_key':
        logging.warning("SENDGRID_API_KEY not configured. Skipping email sending.")
        return 200, "Mock email sent"
    try:
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        mail = Mail(Email("olgashabaykina202226@gmail.com"), To(to_email), subject, Content("text/plain", body))
        response = sg.send(mail)
        logging.info(f"Email sent successfully! Status code: {response.status_code}")
        return response.status_code, response.body
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        traceback.print_exc()
        return 500, "Failed to send email"

def order_placed_notification(order, customer_email):
    subject = "Order Confirmation"
    body = f"Thank you for your order! You have ordered a {order['product']['name']}."
    return send_email(subject, customer_email, body)

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def record_metrics(response):
    latency = time.time() - request.start_time
    REQUEST_LATENCY.labels(method=request.method, endpoint=request.path).observe(latency)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.path, http_status=response.status_code).inc()
    return response

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username in users and users[username] == password:
            session["user"] = username
            flash("Login successful!", "success")
            return redirect(url_for("catalog"))
        flash("Invalid credentials. Please try again.", "danger")
    return render_template("login.html")

@app.route("/catalog")
def catalog():
    if "user" not in session:
        flash("Please log in.", "danger")
        return redirect(url_for("login"))
    return render_template("catalog.html", products=products)

@app.route("/order", methods=["POST"])
def order():
    if "user" not in session:
        flash("Please log in.", "danger")
        return redirect(url_for("login"))

    product_id = request.form.get("product_id")
    customer_email = request.form.get("customer_email", "").strip()

    if not product_id or not customer_email:
        flash("Missing product ID or email address.", "danger")
        return redirect(url_for("catalog"))

    product = next((p for p in products if p["id"] == int(product_id)), None)
    if not product:
        flash("Product not found. Please try again.", "danger")
        return redirect(url_for("catalog"))

    if not re.match(r"[^@]+@[^@]+\.[^@]+", customer_email):
        flash("Invalid email address. Please try again.", "danger")
        return redirect(url_for("catalog"))

    orders.append({"user": session["user"], "product": product})
    order_placed_notification({"user": session["user"], "product": product}, customer_email)
    flash(f"Order placed for {product['name']}!", "success")
    return redirect(url_for("catalog"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out.", "info")
    return redirect(url_for("login"))

@app.route('/metrics')
def metrics():
    return generate_latest(registry)

# Helper for testing
def get_prometheus_registry():
    return registry

# Prometheus integration
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {'/metrics': make_wsgi_app(registry)})

if __name__ == "__main__":
    logging.info("Starting Flask application...")
    app.run(debug=True, port=5001)
