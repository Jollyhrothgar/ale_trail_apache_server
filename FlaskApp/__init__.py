from flask import Flask
app = Flask(__name__)

if __name__ == "__main__":
    app.run()

#Website Building
from flask import render_template
from flask import request
from query_results import query_results

#SQL support
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

#Data Interface
import psycopg2

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html", )

@app.route('/rich_dark')
def rich_dark_page():
    return render_template("rich_dark.html")

@app.route('/medium_smooth')
def medium_smooth_page():
    return render_template("medium_smooth.html")

@app.route("/bright_hoppy")
def bright_hoppy_page():
    return render_template("bright_hoppy.html")

@app.route("/hoppy_results",methods=['GET','POST'])
def hoppy_results_page():
    word_1  = request.form['hop_word_1']
    word_2  = request.form['hop_word_2']
    word_1 = word_1.lower()
    word_2 = word_2.lower()

    results = query_results(0.6,1.0,word_1,word_2)
    status = results['status']
    beer_results = results['beer_list']
    for beer_result in beer_results:
        print beer_result
    return render_template("hoppy_results.html",beers=beer_results)

@app.route("/medium_results",methods=['GET','POST'])
def medium_results_page():
    word_1  = request.form['hop_word_1']
    word_2  = request.form['hop_word_2']
    word_1 = word_1.lower()
    word_2 = word_2.lower()

    results = query_results(0.4,0.6,word_1,word_2)
    status = results['status']
    beer_results = results['beer_list']
    for beer_result in beer_results:
        print beer_result
    return render_template("hoppy_results.html",beers=beer_results)

@app.route("/dark_results",methods=['GET','POST'])
def dark_results_page():
    word_1  = request.form['hop_word_1']
    word_2  = request.form['hop_word_2']
    word_1 = word_1.lower()
    word_2 = word_2.lower()
    results = query_results(0.0,0.4,word_1,word_2)
    status = results['status']
    beer_results = results['beer_list']
    for beer_result in beer_results:
        print beer_result
    return render_template("hoppy_results.html",beers=beer_results)
