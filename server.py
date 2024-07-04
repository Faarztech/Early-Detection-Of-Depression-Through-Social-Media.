from flask import Flask, request, render_template, flash, redirect, session
from models import Model
from depression_detection_tweets import DepressionDetection
from TweetModel import process_message
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, UserMixin, logout_user

app = Flask(__name__)

# Configuration for SQLAlchemy and LoginManager
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.config['SECRET_KEY'] = 'thisissecret'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# SQLAlchemy User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    fname = db.Column(db.String(80), nullable=False)
    lname = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username 

# Function to load a user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create all database tables
with app.app_context():
    db.create_all()

# Register route
@app.route("/", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle form submission
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('uname')
        
        # Create a new user and add it to the database
        user = User(fname=fname, lname=lname, email=email, password=password, username=username)
        db.session.add(user)
        db.session.commit()
        
        flash('User has been registered successfully', 'success')
        return redirect('/login')
    
    return render_template("register.html")

# Login route
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle form submission
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Query the database for the user
        user = User.query.filter_by(username=username).first()
        
        # Check if the user exists and the password is correct
        if user and password == user.password:
            login_user(user)
            return redirect('/index')
        else:
            flash('Invalid Credentials', 'warning')
            return redirect('/login')
    
    return render_template("login.html")

# Logout route
@app.route("/logout")
def logout():
    logout_user()  # Logout the current user
    return render_template("thank-you.html")

# Additional routes from the first code
@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/sentiment")
def sentiment():
    return render_template("sentiment.html")

@app.route("/service")
def service():
    return render_template("service.html")

@app.route("/model")
def model():
    return render_template("Model.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/remedies")
def remedies():
    return render_template("remedies.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/result")
def result():
    return render_template("result.html")

# Function for sentiment prediction
@app.route("/predictSentiment", methods=["POST"])
def predictSentiment():
    message = request.form['form10']
    pm = process_message(message)
    result = DepressionDetection.classify(pm, 'bow') or DepressionDetection.classify(pm, 'tf-idf')
    return render_template("tweetresult.html", result=result)

# Function for depression prediction
@app.route('/predict', methods=["POST"])
def predict():
    q1 = int(request.form['a1'])
    q2 = int(request.form['a2'])
    q3 = int(request.form['a3'])
    q4 = int(request.form['a4'])
    q5 = int(request.form['a5'])
    q6 = int(request.form['a6'])
    q7 = int(request.form['a7'])
    q8 = int(request.form['a8'])
    q9 = int(request.form['a9'])
    q10 = int(request.form['a10'])

    values = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10]
    model = Model()
    classifier = model.svm_classifier()
    prediction = classifier.predict([values])

    # Interpret the prediction and provide a result
    if prediction[0] == 0:
        result = 'Your Depression test result : No Depression'
    elif prediction[0] == 1:
        result = 'Your Depression test result : Mild Depression'
    elif prediction[0] == 2:
        result = 'Your Depression test result : Moderate Depression'
    elif prediction[0] == 3:
        result = 'Your Depression test result : Moderately severe Depression'
    else:
        result = 'Your Depression test result : Severe Depression'

    return render_template("result.html", result=result)

# Run the app
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(port=5987, host='0.0.0.0', debug=True)
