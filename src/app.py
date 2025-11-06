from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from config import config 
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from googleapiclient.discovery import build
from werkzeug.security import generate_password_hash
import requests

# Models 
from models.ModelUser import ModelUser
# Entities
from models.entities.User import User

#configuracion principal
app = Flask(__name__)
csrf = CSRFProtect()
db = MySQL(app)
login_manager_app = LoginManager(app)

YOUTUBE_API_KEY = "AIzaSyA48YcvnD7W3UhpBtWd3IyNpKCP6uJbZA4"  # api de youtube

@login_manager_app.user_loader
def load_user(id): 
    return ModelUser.get_by_id(db, id)

#login
@app.route('/')
def index():   
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login(): 
    if request.method == 'POST': 
        user = User(0, request.form['username'], request.form['password'])
        logged_user = ModelUser.login(db, user)

        if logged_user is not None: 
            if logged_user.password: 
                login_user(logged_user)
                return redirect(url_for('home'))
            else:
                flash("Contraseña incorrecta.")
        else:
            flash("Usuario no encontrado.")
    return render_template('auth/login.html')


@app.route('/register', methods=['GET', 'POST'])
@csrf.exempt
def register():
    if request.method == 'POST':
        # validacion de captcha
        recaptcha_response = request.form.get('g-recaptcha-response')
        secret_key = "6LctjQQsAAAAABI3hmbyU62i-6mXFMsDNJztfraa"
        verify_url = "https://www.google.com/recaptcha/api/siteverify"

        data = {'secret': secret_key, 'response': recaptcha_response}
        response = requests.post(verify_url, data=data)
        result = response.json()

        if not result['success']:
            flash('Por favor verifica el reCAPTCHA.')
            return redirect(url_for('register'))

        fullname = request.form['fullname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('⚠️ Las contraseñas no coinciden.')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        cursor = db.connection.cursor()
        sql = """INSERT INTO user (fullname, username, email, password)
                 VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (fullname, username, email, hashed_password))
        db.connection.commit()

        flash('Usuario registrado exitosamente.')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')


@app.route('/logout')
def logout(): 
    logout_user()
    return redirect(url_for('login'))

#home
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    videos = []
    query = request.args.get('q', 'tecnología') 

    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        request_api = youtube.search().list(
            part='snippet',
            q=query,
            maxResults=8,
            type='video'
        )
        response = request_api.execute()

        for item in response.get('items', []):
            videos.append({
                'id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'thumbnail': item['snippet']['thumbnails']['medium']['url']
            })
    except Exception as e:
        print("Error al obtener videos:", e)

   #
    cursor = db.connection.cursor()
    sql = "SELECT video_id FROM favorites WHERE user_id = %s"
    cursor.execute(sql, (int(current_user.id),))
    user_favorites = [row[0] for row in cursor.fetchall()]

    return render_template('home.html', videos=videos, user_favorites=user_favorites)


#favoritos
@app.route('/add_favorite', methods=['POST'])
@csrf.exempt
@login_required
def add_favorite():
    video_id = request.form['video_id']
    title = request.form['title']
    thumbnail = request.form['thumbnail']

    cursor = db.connection.cursor()
    sql = """INSERT INTO favorites (user_id, video_id, title, thumbnail)
             VALUES (%s, %s, %s, %s)"""
    values = (int(current_user.id), video_id, title, thumbnail)
    cursor.execute(sql, values)
    db.connection.commit()
    flash('✅ Video agregado a favoritos.')
    return redirect(url_for('favorites'))

@app.route('/favorites', methods=['GET'])
@login_required
def favorites():
    search_query = request.args.get('q', '') 
    cursor = db.connection.cursor()

    if search_query:
        sql = "SELECT * FROM favorites WHERE user_id = %s AND title LIKE %s"
        cursor.execute(sql, (int(current_user.id), f"%{search_query}%"))
    else:
        sql = "SELECT * FROM favorites WHERE user_id = %s"
        cursor.execute(sql, (int(current_user.id),))

    data = cursor.fetchall()
    return render_template('favorites.html', favorites=data)



@app.route('/remove_favorite', methods=['POST'])
@csrf.exempt
@login_required
def remove_favorite():
    video_id = request.form['video_id']
    cursor = db.connection.cursor()
    sql = "DELETE FROM favorites WHERE user_id = %s AND video_id = %s"
    cursor.execute(sql, (int(current_user.id), video_id))
    db.connection.commit()
    flash('❌ Video eliminado de favoritos.')
    return redirect(url_for('favorites'))

#detectar errores
def status_401(error): 
    return redirect(url_for('login'))

def status_404(error): 
    return "<h1>Pagina no encontrada</h1>", 404


if __name__ == '__main__': 
    app.config.from_object(config['development'])
    app.config['SECRET_KEY'] = '12345'
    csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run()
