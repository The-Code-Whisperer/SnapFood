from flask import Flask, render_template, request

# Configure application

app = Flask(__name__)

# Index route
app.route("/", methods=["GET"])
def index():
    return render_template("index.html")
