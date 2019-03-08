from flask import Flask, render_template
app = Flask(__name__)

# each app.route is an endpoint

@app.route('/')
def hello_world():
    return 'mySQL db ACCESS testing'

