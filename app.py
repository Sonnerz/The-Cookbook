import os
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_pymongo import PyMongo

DBS_NAME = os.getenv("DBS_NAME")
MONGO_URI = os.getenv("MONGODB_URI")

app = Flask(__name__)

if app.debug:
    app.config["DBS_NAME"] = "cookbook"
    app.config["MONGO_URI"] = "mongodb://admin:c00k800k32-@ds251332.mlab.com:51332/cookbook"
else:
    app.config["DBS_NAME"] = DBS_NAME
    app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(app)


@app.context_processor
def debug_on_off():
    return dict(debug=app.debug)


def get_record(username):
    try:
        row = user_recipe.find_one({'username': username.lower()})
    except:
        print("error acccessing DB")
        flash("no access")
    if row:
        print("usernane taken")
        flash("that {}, is taken".format(username))
    return row


@app.route('/')
@app.route('/get_test')
def get_test():
    return render_template("index.html", test=mongo.db.test_collection.find())


@app.route('/login_user')
def login_user():
    return render_template("index.html", test=mongo.db.test_collection.find())


@app.route('/signup_user', methods=['POST'])
def signup_user():
    if not check_user = get_record(request.form.get('signupUsername')):
        users = mongo.db.user_recipe
        new_user = {'username': request.form.get('signupUsername'),
                    'password': request.form.get('signupPassword'),
                    'firstname': request.form.get('firstName'),
                    'lastname': request.form.get('lastName')}
        users.insert_one(new_user)
    else:
        message = "Already there"
    return redirect(url_for('get_test'), message)


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'), port=int(os.environ.get('PORT')), debug=True)
