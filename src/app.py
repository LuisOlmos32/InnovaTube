from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from config import config 


#Models 
from  models.ModelUser import ModelUser
#entities
from models.entities.User import User

app = Flask(__name__)

db = MySQL(app)

@app.route('/')
def index():
    
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login(): 
    
    if request.method == 'POST': 
        # print(request.form['username'])
        # print(request.form['password'])
        
        user = User(0,request.form['username'],request.form['password']  )
        logged_user = ModelUser.login(db, user)
        
        if logged_user is not None: 
            if  logged_user.password: 
                return redirect(url_for('home'))
            else:
                flash("Invalid password ")
                return  render_template("auth/login.html")
        else:
            flash("User not found")
            return  render_template("auth/login.html")
    else: 
        return render_template('auth/login.html')
    
@app.route("/home")
def home(): 
    return render_template('auth/home.html')



if __name__ == '__main__': 
    app.config.from_object(config['development'])
    app.run()