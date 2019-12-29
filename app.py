#Objeto global = g
#flash despegar un mensaje despues de la siguiente peticion.
#Renderear una Template de html que vamos a ocupar
#url_for generar una URL a cierto idpoint.
#redirect redireccionar a un usuario.
#Importamos de flask_login LoginManager para manejar las sesiones de los usr.
#abort : sale de la lista actual , 404 error
from flask import (Flask, g, render_template, flash, url_for, redirect, abort)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, login_required, current_user,
                        logout_user, AnonymousUserMixin)
#Para crear la vista de inicio de sesion:
from flask_bcrypt import check_password_hash
import models
import forms

DEBUG = True
PORT = 8000
HOST = "0.0.0.0"

#instanciar app
#definimos nuestra llave secreta que diferencia esta aplicacion de otras
#que se encuentren en la web
app = Flask(__name__)
app.secret_key = "nqoijdq;wpdjqwoiw.enfpoqdpq;okdp12o320938jmqodq09;1283091"

#Definiendo usuario anonimo
class Anonymous(AnonymousUserMixin):
    def __int__(self):
        self.username = "Invitado"

#Instanciamos LoginManager
#indicamos con lo siguiente la vista que se va a desplegar al usuario cuando
#inicie sesion.
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.anonymous_user = Anonymous


#creamos un metodo para cargar al usuario.
@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Conecta a la base de Datos antes de cada request"""
    #Verificar que no haya una conexion definida antes de hacer esta peticion.
    #hasattr verifica que este objeto que ponemos en el primer argumento
    #no tenga este atributo definido en si mismo.
    g.db = models.DATABASE
    #models es nuestro arhivo de modelos
    #para conectarnos antes de hacer cualquier peticion
    if g.db.is_closed():
        g.db.connect()
        g.user = current_user

@app.after_request
def after_request(response):
    """Cerramos la conexión a la BD"""
    g.db.close()
    return response

                                #VISTAS

#View Post
@app.route("/post/<int:post_id>")
def view_post(post_id):
    posts = models.Post.select().where(models.Post.id == post_id)
    if posts.count() == 0:
        abort(404)
    return render_template("stream.html", stream = posts)


#Follow
@app.route("/follow/<username>")
@login_required
def follow(username):
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            models.Relationship.create(
                from_user = g.user._get_current_object(),
                to_user = to_user
            )
        except models.IntegrityError:
            pass
        else:
            flash("Ahora sigues a {}".format(to_user.username), "success")
    return redirect(url_for("stream", username = to_user.username))


#Unfollow
@app.route("/unfollow/<username>")
@login_required
def unfollow(username):
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            models.Relationship.get(
                from_user = g.user._get_current_object(),
                to_user = to_user
            ).delete_instance()
        except models.IntegrityError:
            pass
        else:
            flash("Haz dejado de seguir a {}".format(to_user.username), "success")
    return redirect(url_for("stream", username = to_user.username))


#Registro
@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    #Queremos que se valide la informacion que nos mandaron con los Validadores
    #que ya predefinimos.
    if form.validate_on_submit():
        flash('Fuiste Registrado!!!', 'success')
        #creamos el registro en la base de datos con la informacion que ya
        #sabemos que fue validada
        models.User.create_user(
            username = form.username.data,
            email = form.email.data,
            password= form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


#Login
@app.route("/login", methods = ("GET", "POST"))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Tu nombre de usuario o contraseña son incorrectos","error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Iniciaste sesion","success")
                return redirect(url_for("index"))
    return render_template("login.html",form = form)

#Logout
@app.route("/logout", methods = ("GET", "POST"))
@login_required
def logout():
    #deslogea al usuario, logout_user() ya viene predefinida con flask_login
    logout_user()
    flash("Has salido de FaceSmash", "success")
    return redirect(url_for("index"))


#Post
@app.route("/new_post", methods = ("GET", "POST"))
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        models.Post.create(user = g.user._get_current_object(),
                content = form.content.data.strip())
        flash("Mensaje Posteado", "success")
        return redirect(url_for("index"))
    return render_template("post.html",form = form)


#Index
@app.route("/")
def index():
    stream = models.Post.select().limit(100)
    return render_template("stream.html", stream = stream)


#Stream
@app.route("/stream")
@app.route("/stream/<username>")
def stream(username = None):
    template = "stream.html"
    if username and username != current_user.username:
        try:
            #** parecidos a username
            user = models.User.select().where(models.User.username**username).get()
        except models.DoesNotExist:
            abort(404)
        else:
            stream = user.post.limit(100)
    else:
        stream = current_user.get_stream().limit(100)
        user = current_user
    if username:
        template = "user_stream.html"
    return render_template(template, stream = stream, user = user)


#Error 404
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username = "Juan",
            email = "fernandezjubin@gmail.com",
            password = "domingo20juan"
        )
    except ValueError:
        pass
    app.run(debug = DEBUG, host = HOST, port = PORT)
