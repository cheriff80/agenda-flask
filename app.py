from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_session import Session
from datetime import datetime, timedelta
import schedule, asyncio, threading, time, signal, sys, shutil
from telegram import Bot

# ===================== Configuración Flask =====================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agenda.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de sesión en servidor
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './flask_session'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)

db = SQLAlchemy(app)

# ===================== Login Manager =====================
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# ===================== Modelos =====================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    eventos = db.relationship('Evento', backref='usuario', lazy=True)

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    aviso_horas = db.Column(db.Integer, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# ===================== Crear tablas =====================
with app.app_context():
    db.create_all()

# ===================== Telegram =====================
TOKEN = 'TU_TELEGRAM_BOT_TOKEN'
CHAT_ID = 'TU_CHAT_ID'
bot = Bot(token=TOKEN)

async def send_telegram_message(texto):
    await bot.send_message(chat_id=CHAT_ID, text=texto)

def check_eventos():
    now = datetime.now()
    eventos = Evento.query.all()
    for evento in eventos:
        aviso = evento.fecha - timedelta(hours=evento.aviso_horas)
        if aviso <= now < evento.fecha:
            asyncio.run(send_telegram_message(f"📅 Recordatorio: {evento.titulo} a las {evento.fecha.strftime('%H:%M')}"))

# ===================== Scheduler =====================
def run_schedule():
    def loop():
        while True:
            schedule.run_pending()
            time.sleep(60)
    t = threading.Thread(target=loop)
    t.daemon = True
    t.start()

schedule.every(1).minutes.do(check_eventos)
run_schedule()

# ===================== Logout automático al cerrar =====================
def on_exit(signal_received, frame):
    print("Cerrando servidor… borrando todas las sesiones")
    shutil.rmtree('./flask_session', ignore_errors=True)
    sys.exit(0)

signal.signal(signal.SIGINT, on_exit)
signal.signal(signal.SIGTERM, on_exit)

# ===================== Login Manager =====================
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))  # Evita warning de Query.get()

# ===================== Rutas =====================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash("Usuario ya existe")
            return redirect(url_for('register'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Usuario creado. Ahora inicia sesión.")
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('index'))
        flash("Usuario o contraseña incorrectos")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión")
    return redirect(url_for('login'))

@app.route("/")
@login_required
def index():
    eventos = Evento.query.filter_by(user_id=current_user.id).order_by(Evento.fecha).all()
    return render_template("index.html", eventos=eventos)

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_evento():
    if request.method == "POST":
        titulo = request.form['titulo']
        fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%dT%H:%M')
        aviso_horas = int(request.form['aviso_horas'])
        evento = Evento(titulo=titulo, fecha=fecha, aviso_horas=aviso_horas, user_id=current_user.id)
        db.session.add(evento)
        db.session.commit()
        flash("Evento añadido")
        return redirect(url_for('index'))
    return render_template("add_evento.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_evento(id):
    evento = Evento.query.get_or_404(id)
    if evento.user_id != current_user.id:
        flash("No tienes permiso")
        return redirect(url_for('index'))
    if request.method == "POST":
        evento.titulo = request.form['titulo']
        evento.fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%dT%H:%M')
        evento.aviso_horas = int(request.form['aviso_horas'])
        db.session.commit()
        flash("Evento actualizado")
        return redirect(url_for('index'))
    return render_template("edit_evento.html", evento=evento)

@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_evento(id):
    evento = Evento.query.get_or_404(id)
    if evento.user_id != current_user.id:
        flash("No tienes permiso")
        return redirect(url_for('index'))
    db.session.delete(evento)
    db.session.commit()
    flash("Evento eliminado")
    return redirect(url_for('index'))

# ===================== Ejecutar app =====================
if __name__ == "__main__":
    app.run(debug=True)




