import sqlite3
import logging
import sys
from datetime import date, datetime
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
db_connection_count = 0

# Task 1.3: reference Knowledge QnA
logger = logging.getLogger("__name__")
logging.basicConfig(level=logging.DEBUG)
h1 = logging.StreamHandler(sys.stdout)
h1.setLevel(logging.DEBUG)
h2 = logging.StreamHandler(sys.stderr)
h2.setLevel(logging.ERROR)
logger.addHandler(h1)
logger.addHandler(h2)

# to get current time and date to append to log outputs: reference python datetime docs and forums
today = date.today()
today_date = str(today.day) + '/' + str(today.month) + '/' + str(today.year)
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
current_datetime = today_date + ', ' + current_time


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global db_connection_count
    db_connection_count += 1
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


# Task 1.1
@app.route("/healthz")
def healthz():
    app.logger.info(current_datetime + ', Status request successful!')
    return jsonify(result='OK - healthy'), 200
    # jsonify() returns a Response object with the application/json mimetype set


# Task 1.2
@app.route("/metrics")
def metrics():
    app.logger.info(current_datetime + ', Metrics request successful!')
    connection = get_db_connection()
    query = connection.execute('SELECT COUNT(*) FROM posts')
    post_count = 0
    for row in query:
        post_count = row[0]
    return jsonify(db_connection_count=db_connection_count, post_count=post_count), 200


# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.info(current_datetime + ', 404 page returned!')
        return render_template('404.html'), 404
    else:
        # get title of post retrieved
        connection = get_db_connection()
        query_str = 'SELECT title FROM posts WHERE id = ' + str(post_id)
        query = connection.execute(query_str)
        for row in query:
            title = row[0]
        app.logger.info(current_datetime + ', Article "' + str(title) + '" retrieved!')
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    app.logger.info(current_datetime + ', About us page retrieved!')
    return render_template('about.html')


# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
            app.logger.info(current_datetime + ', Article "' + title + '" created!')
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')


# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=3111)
