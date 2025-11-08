from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from googleapiclient.discovery import build
from werkzeug.security import generate_password_hash
import requests
import os

# Inicialización
app = Flask(__name__)
csrf = CSRFProtect()

# Configuración de la base de datos para Render (usando variable de entorno)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI", "postgresql://flask_login_6tjz_user:usFK1NDzJBS6baJktDwNAczd4N0wQze0@dpg-d47q6ummcj7s73did8e0-a/flask_login_6tjz")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "12345")

db = SQLAlchemy(app)
login_manager_app = LoginManager(app)

# API de YouTube
YOUTUBE_API_KEY = "AIzaSyA48YcvnD7W3UhpBtWd3IyNpKCP6uJbZA4"

# ======================
# MODELOS DE BASE DE DATOS
# ======================

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))

class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    video_id = db.Column(db.String(100))
    title = db.Column(db.String(200))
    thumbnail = db.Column(db.String(255))

# ======================
# LOGIN MANAGER
# ======================
@login_manager_app.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ======================
# RUTAS
# ======================

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password:  # Aquí deberías verificar con check_password_hash
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash("Usuario o contraseña incorrectos.")
    return render_template('auth/login.html')


@app.route('/register', methods=['GET', 'POST'])
@csrf.exempt
def register():
    if request.method == 'POST':
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

        new_user = User(fullname=fullname, username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Usuario registrado exitosamente.')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


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

    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    user_favorites = [f.video_id for f in favorites]

    return render_template('home.html', videos=videos, user_favorites=user_favorites)


@app.route('/add_favorite', methods=['POST'])
@csrf.exempt
@login_required
def add_favorite():
    video_id = request.form['video_id']
    title = request.form['title']
    thumbnail = request.form['thumbnail']

    new_favorite = Favorite(user_id=current_user.id, video_id=video_id, title=title, thumbnail=thumbnail)
    db.session.add(new_favorite)
    db.session.commit()

    flash('✅ Video agregado a favoritos.')
    return redirect(url_for('favorites'))


@app.route('/favorites', methods=['GET'])
@login_required
def favorites():
    search_query = request.args.get('q', '')
    if search_query:
        data = Favorite.query.filter(
            Favorite.user_id == current_user.id,
            Favorite.title.ilike(f"%{search_query}%")
        ).all()
    else:
        data = Favorite.query.filter_by(user_id=current_user.id).all()

    return render_template('favorites.html', favorites=data)


@app.route('/remove_favorite', methods=['POST'])
@csrf.exempt
@login_required
def remove_favorite():
    video_id = request.form['video_id']
    fav = Favorite.query.filter_by(user_id=current_user.id, video_id=video_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        flash('❌ Video eliminado de favoritos.')
    return redirect(url_for('favorites'))


# ======================
# ERRORES Y MAIN
# ======================

def status_401(error):
    return redirect(url_for('login'))

def status_404(error):
    return "<h1>Pagina no encontrada</h1>", 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea las tablas si no existen
    csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run()
